import pytest

from app.models.printer import Printer
from app.services import discovery


def test_parse_subnets_ignores_invalid():
    networks = discovery._parse_subnets("192.168.1.0/24, 10.0.0.0/24, invalid")
    assert len(networks) == 2


def test_build_device_uri():
    assert (
        discovery.build_device_uri("ipp", "192.0.2.10", 631, "ipp/print")
        == "ipp://192.0.2.10:631/ipp/print"
    )
    assert (
        discovery.build_device_uri("ipps", "192.0.2.10", 631)
        == "ipps://192.0.2.10:631/ipp/print"
    )
    assert (
        discovery.build_device_uri("lpd", "192.0.2.10", 515, "queue")
        == "lpd://192.0.2.10/queue"
    )
    assert (
        discovery.build_device_uri("socket", "192.0.2.10", 9100)
        == "socket://192.0.2.10:9100"
    )


def test_dedupe_prefers_ipp():
    printers = [
        discovery.DiscoveredPrinter(
            "Socket", "socket://192.0.2.10:9100", "socket", "192.0.2.10", 9100
        ),
        discovery.DiscoveredPrinter(
            "IPP", "ipp://192.0.2.10:631/ipp/print", "ipp", "192.0.2.10", 631
        ),
    ]
    merged = discovery._dedupe(printers)
    assert len(merged) == 1
    assert merged[0].protocol == "ipp"


def test_sync_discovered_creates_and_updates(db_session, monkeypatch):
    monkeypatch.setattr(discovery.cups, "add_printer", lambda *args, **kwargs: True)
    monkeypatch.setattr(discovery.cups, "printer_status", lambda *args, **kwargs: "idle")

    discovered = [
        {
            "name": "Testdrucker",
            "device_uri": "ipp://192.0.2.20/ipp/print",
            "protocol": "ipp",
            "host": "192.0.2.20",
            "port": 631,
            "model": "Test",
            "location": "EG",
            "capabilities": {"color-supported": True},
        }
    ]

    created, updated = discovery.sync_discovered(db_session, discovered)
    assert (created, updated) == (1, 0)

    printer = (
        db_session.query(Printer)
        .filter(Printer.device_uri == discovered[0]["device_uri"])
        .one()
    )
    assert printer.slug == "testdrucker"
    assert printer.auto_discovered is True
    assert printer.status == "idle"
    assert printer.last_seen is not None

    created, updated = discovery.sync_discovered(db_session, discovered)
    assert (created, updated) == (0, 1)
    assert (
        db_session.query(Printer)
        .filter(Printer.device_uri == discovered[0]["device_uri"])
        .count()
        == 1
    )


def test_scan_endpoint(admin_client, monkeypatch):
    async def fake_scan_and_sync(db, subnets=None):
        return {"printers": [{"name": "X"}], "created": 1, "updated": 0}

    monkeypatch.setattr("app.api.printers.scan_and_sync", fake_scan_and_sync)
    response = admin_client.post("/api/printers/scan")
    assert response.status_code == 200
    assert response.json()["created"] == 1


def test_refresh_endpoint(admin_client, monkeypatch):
    monkeypatch.setattr("app.api.printers.sync_statuses", lambda db: 3)
    response = admin_client.post("/api/printers/refresh")
    assert response.status_code == 200
    assert response.json()["updated"] == 3


@pytest.mark.asyncio
async def test_scan_network_without_sources(monkeypatch):
    monkeypatch.setattr(discovery.settings, "discovery_mdns", False)
    monkeypatch.setattr(discovery.settings, "discovery_subnets", "")
    assert await discovery.scan_network() == []
