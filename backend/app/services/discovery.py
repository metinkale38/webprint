from ..config import settings


async def scan_network(subnets: str | None = None) -> list[dict]:
    """Drucker im Netzwerk finden.

    M3 implementiert hier mDNS (zeroconf) und den TCP-/SNMP-Scan der in
    ``subnets`` oder ``settings.discovery_subnets`` konfigurierten Subnetze.
    Bis dahin bewusst leer, damit die API stabil bleibt.
    """
    _ = subnets or settings.discovery_subnets
    return []
