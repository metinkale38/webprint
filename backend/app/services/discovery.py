import asyncio
import ipaddress
import logging
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator

from sqlalchemy.orm import Session
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf

from ..config import settings
from ..models.printer import Printer
from ..utils import slugify
from . import cups

logger = logging.getLogger(__name__)

_SERVICE_PROTOCOLS = {
    "_ipp._tcp.local.": "ipp",
    "_ipps._tcp.local.": "ipps",
    "_printer._tcp.local.": "lpd",
    "_pdl-datastream._tcp.local.": "socket",
}

_PROTOCOL_PRIORITY = {"ipps": 4, "ipp": 3, "lpd": 2, "socket": 1}

_MAX_HOSTS = 1024
_SCAN_PORTS = (631, 515, 9100)


@dataclass
class DiscoveredPrinter:
    name: str
    device_uri: str
    protocol: str
    host: str
    port: int
    model: str = ""
    location: str = ""
    source: str = "mdns"
    capabilities: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "device_uri": self.device_uri,
            "protocol": self.protocol,
            "host": self.host,
            "port": self.port,
            "model": self.model,
            "location": self.location,
            "source": self.source,
            "capabilities": self.capabilities,
        }


def build_device_uri(protocol: str, host: str, port: int, resource: str = "") -> str:
    resource = resource.strip().lstrip("/")
    if protocol == "ipp":
        return f"ipp://{host}:{port}/{resource or 'ipp/print'}"
    if protocol == "ipps":
        return f"ipps://{host}:{port}/{resource or 'ipp/print'}"
    if protocol == "lpd":
        return f"lpd://{host}/{resource or 'lp'}"
    return f"socket://{host}:{port}"


def _decode_properties(info: ServiceInfo) -> dict[str, str]:
    properties: dict[str, str] = {}
    for key, value in info.properties.items():
        if key is None or value is None:
            continue
        decoded_key = key.decode(errors="ignore") if isinstance(key, bytes) else str(key)
        decoded_value = value.decode(errors="ignore") if isinstance(value, bytes) else str(value)
        properties[decoded_key] = decoded_value
    return properties


def _from_service_info(info: ServiceInfo, service_type: str) -> DiscoveredPrinter | None:
    protocol = _SERVICE_PROTOCOLS.get(service_type)
    if protocol is None:
        return None
    try:
        addresses = info.parsed_addresses()
    except Exception:
        return None
    host = next((address for address in addresses if ":" not in address), None)
    if host is None and addresses:
        host = addresses[0]
    if not host:
        return None

    properties = _decode_properties(info)
    resource = properties.get("rp", "")
    name = (
        properties.get("ty")
        or properties.get("product")
        or info.name.split(".")[0].replace("\\032", " ")
    )
    default_port = 631 if protocol in {"ipp", "ipps"} else 515 if protocol == "lpd" else 9100
    port = info.port or default_port
    return DiscoveredPrinter(
        name=name,
        device_uri=build_device_uri(protocol, host, port, resource),
        protocol=protocol,
        host=host,
        port=port,
        model=properties.get("product") or properties.get("ty") or "",
        location=properties.get("note") or properties.get("location") or "",
        source="mdns",
    )


class _MdnsListener:
    def __init__(self) -> None:
        self.found: dict[str, DiscoveredPrinter] = {}

    def _resolve(self, zc: Zeroconf, service_type: str, name: str) -> None:
        info = zc.get_service_info(service_type, name, timeout=2000)
        if info is None:
            return
        printer = _from_service_info(info, service_type)
        if printer is not None:
            self.found[printer.device_uri] = printer

    def add_service(self, zc: Zeroconf, service_type: str, name: str) -> None:
        self._resolve(zc, service_type, name)

    def update_service(self, zc: Zeroconf, service_type: str, name: str) -> None:
        self._resolve(zc, service_type, name)

    def remove_service(self, _zc: Zeroconf, _service_type: str, _name: str) -> None:
        return None


def _browse_mdns(timeout: float) -> list[DiscoveredPrinter]:
    zc = Zeroconf()
    listener = _MdnsListener()
    browsers = [ServiceBrowser(zc, service_type, listener) for service_type in _SERVICE_PROTOCOLS]
    try:
        time.sleep(timeout)
    finally:
        for browser in browsers:
            browser.cancel()
        zc.close()
    return list(listener.found.values())


def _parse_subnets(value: str) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    for raw in value.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            networks.append(ipaddress.ip_network(raw, strict=False))
        except ValueError:
            logger.warning("Ungültiges Discovery-Subnetz: %s", raw)
    return networks


def _hosts(networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network]) -> Iterator[str]:
    count = 0
    for network in networks:
        for host in network.hosts():
            if count >= _MAX_HOSTS:
                return
            count += 1
            yield str(host)


async def _tcp_open(host: str, port: int, timeout: float) -> bool:
    try:
        _reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
    except Exception:
        return False
    writer.close()
    try:
        await writer.wait_closed()
    except Exception:
        pass
    return True


def probe_snmp(ip: str, community: str = "public") -> dict[str, str]:
    try:
        result = subprocess.run(
            [
                "snmpget",
                "-v2c",
                "-c",
                community,
                "-Oqv",
                "-t",
                "1",
                "-r",
                "0",
                ip,
                "1.3.6.1.2.1.1.5.0",
                "1.3.6.1.2.1.1.1.0",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {}
    if result.returncode != 0:
        return {}
    values = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not values:
        return {}
    return {
        "sysName": values[0],
        "sysDescr": values[1] if len(values) > 1 else "",
    }


async def _scan_subnets(value: str, timeout: float) -> list[DiscoveredPrinter]:
    networks = _parse_subnets(value)
    if not networks:
        return []

    semaphore = asyncio.Semaphore(200)
    connect_timeout = min(max(timeout / 2, 0.3), 1.0)

    async def scan_host(host: str) -> list[DiscoveredPrinter]:
        async with semaphore:
            checks = await asyncio.gather(
                *(_tcp_open(host, port, connect_timeout) for port in _SCAN_PORTS)
            )
            open_ports = [
                port for port, is_open in zip(_SCAN_PORTS, checks) if is_open
            ]
            if not open_ports:
                return []

            if 631 in open_ports:
                protocol, port = "ipp", 631
            elif 515 in open_ports:
                protocol, port = "lpd", 515
            else:
                protocol, port = "socket", 9100

            model = ""
            location = ""
            if settings.discovery_snmp:
                snmp = await asyncio.to_thread(probe_snmp, host, settings.snmp_community)
                model = snmp.get("sysDescr", "")
                location = snmp.get("sysName", "")

            return [
                DiscoveredPrinter(
                    name=location or host,
                    device_uri=build_device_uri(protocol, host, port),
                    protocol=protocol,
                    host=host,
                    port=port,
                    model=model,
                    location=location,
                    source="scan",
                )
            ]

    results = await asyncio.gather(
        *(scan_host(host) for host in _hosts(networks)), return_exceptions=True
    )
    printers: list[DiscoveredPrinter] = []
    for result in results:
        if isinstance(result, Exception):
            continue
        printers.extend(result)
    return printers


def _dedupe(printers: list[DiscoveredPrinter]) -> list[DiscoveredPrinter]:
    by_host: dict[str, DiscoveredPrinter] = {}
    for printer in printers:
        current = by_host.get(printer.host)
        if current is None or _PROTOCOL_PRIORITY.get(printer.protocol, 0) > _PROTOCOL_PRIORITY.get(
            current.protocol, 0
        ):
            by_host[printer.host] = printer
    return sorted(by_host.values(), key=lambda printer: (printer.name.lower(), printer.host))


async def _enrich(printers: list[DiscoveredPrinter]) -> None:
    semaphore = asyncio.Semaphore(8)

    async def enrich(printer: DiscoveredPrinter) -> None:
        if printer.protocol not in {"ipp", "ipps"} or printer.capabilities:
            return
        async with semaphore:
            attributes = await asyncio.to_thread(cups.probe_ipp, printer.device_uri)
        if not attributes:
            return
        printer.capabilities = attributes
        if not printer.model:
            printer.model = str(attributes.get("printer-make-and-model") or "")
        if not printer.location:
            printer.location = str(attributes.get("printer-location") or "")

    await asyncio.gather(*(enrich(printer) for printer in printers), return_exceptions=True)


async def scan_network(subnets: str | None = None, timeout: float = 4.0) -> list[dict]:
    tasks = []
    if settings.discovery_mdns:
        tasks.append(asyncio.to_thread(_browse_mdns, timeout))

    network_value = subnets if subnets is not None else settings.discovery_subnets
    if network_value.strip():
        tasks.append(_scan_subnets(network_value, timeout))

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)
    discovered: list[DiscoveredPrinter] = []
    for result in results:
        if isinstance(result, Exception):
            logger.warning("Discovery-Teil fehlgeschlagen: %s", result)
            continue
        discovered.extend(result)

    merged = _dedupe(discovered)
    await _enrich(merged)
    return [printer.to_dict() for printer in merged]


def sync_discovered(db: Session, discovered: list[dict]) -> tuple[int, int]:
    created = 0
    updated = 0

    for item in discovered:
        device_uri = item.get("device_uri")
        if not device_uri:
            continue

        existing = db.query(Printer).filter(Printer.device_uri == device_uri).first()
        if existing is None:
            name = item.get("name") or item.get("host") or "Drucker"
            base_slug = slugify(name)
            slug = base_slug
            counter = 2
            while db.query(Printer).filter(Printer.slug == slug).first() is not None:
                slug = f"{base_slug}-{counter}"
                counter += 1

            printer = Printer(
                name=name,
                slug=slug,
                device_uri=device_uri,
                protocol=item.get("protocol", "ipp"),
                model=item.get("model", ""),
                location=item.get("location", ""),
                driver_mode="everywhere",
                auto_discovered=True,
                enabled=True,
                capabilities=item.get("capabilities", {}),
                last_seen=datetime.now(timezone.utc),
            )
            db.add(printer)
            db.flush()
            if cups.add_printer(slug, device_uri, "everywhere"):
                printer.status = cups.printer_status(slug)
            else:
                printer.status = "offline"
            created += 1
        else:
            existing.last_seen = datetime.now(timezone.utc)
            if item.get("model"):
                existing.model = item["model"]
            if item.get("location"):
                existing.location = item["location"]
            if item.get("capabilities"):
                existing.capabilities = item["capabilities"]
            if existing.status == "offline" and not cups.queue_exists(existing.slug):
                cups.add_printer(existing.slug, existing.device_uri, existing.driver_mode)
            existing.status = cups.printer_status(existing.slug)
            updated += 1

    db.commit()
    return created, updated


def sync_statuses(db: Session) -> int:
    printers = db.query(Printer).filter(Printer.enabled.is_(True)).all()
    for printer in printers:
        printer.status = cups.printer_status(printer.slug)
    db.commit()
    return len(printers)


async def scan_and_sync(db: Session, subnets: str | None = None) -> dict:
    discovered = await scan_network(subnets)
    created, updated = sync_discovered(db, discovered)
    return {"printers": discovered, "created": created, "updated": updated}


async def discovery_loop(interval: int) -> None:
    from ..db import SessionLocal

    while True:
        try:
            with SessionLocal() as db:
                result = await scan_and_sync(db)
                logger.info(
                    "Discovery: %d gefunden, %d neu, %d aktualisiert",
                    len(result["printers"]),
                    result["created"],
                    result["updated"],
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Discovery-Lauf fehlgeschlagen")
        await asyncio.sleep(max(30, interval))
