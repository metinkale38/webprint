import re
import subprocess
from pathlib import Path

_QUEUE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_ATTR_PATTERN = re.compile(r"^\s*([A-Za-z0-9-]+)\s+\(([^)]+)\)\s+=\s*(.*)$")


def valid_queue_name(name: str) -> bool:
    return 1 <= len(name) <= 127 and bool(_QUEUE_PATTERN.match(name))


def _run(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def submit_job(queue: str, file_path: Path, options: list[str]) -> str | None:
    if not valid_queue_name(queue):
        return None
    result = _run(["lp", "-d", queue, *options, str(file_path)], timeout=60)
    if result is None or result.returncode != 0:
        return None
    match = re.search(r"request id is (\S+)", result.stdout)
    return match.group(1) if match else None


def cancel_job(cups_job_id: str) -> bool:
    if not cups_job_id.strip():
        return False
    result = _run(["cancel", cups_job_id])
    return result is not None and result.returncode == 0


def add_printer(name: str, device_uri: str, driver_mode: str = "everywhere") -> bool:
    if not valid_queue_name(name) or not device_uri.strip() or not driver_mode.strip():
        return False
    result = _run(["lpadmin", "-p", name, "-v", device_uri, "-m", driver_mode, "-E"])
    if result is None or result.returncode != 0:
        return False
    _run(["cupsenable", name])
    _run(["cupsaccept", name])
    return True


def remove_printer(name: str) -> bool:
    if not valid_queue_name(name):
        return False
    result = _run(["lpadmin", "-x", name])
    return result is not None and result.returncode == 0


def queue_exists(name: str) -> bool:
    if not valid_queue_name(name):
        return False
    result = _run(["lpstat", "-p", name])
    return result is not None and result.returncode == 0


def printer_status(name: str) -> str:
    if not valid_queue_name(name):
        return "offline"
    result = _run(["lpstat", "-p", name])
    if result is None or result.returncode != 0:
        return "offline"
    output = result.stdout.lower()
    if "disabled" in output:
        return "disabled"
    if "now printing" in output or "is printing" in output:
        return "printing"
    if "is idle" in output:
        return "idle"
    return "unknown"


def list_queues() -> list[str]:
    result = _run(["lpstat", "-a"])
    if result is None or result.returncode != 0:
        return []
    names: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if parts and parts[0] not in names:
            names.append(parts[0])
    return names


def _parse_value(raw: str) -> bool | str | list[str]:
    value = raw.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if "," in value:
        return [part.strip() for part in value.split(",") if part.strip()]
    return value


def probe_ipp(uri: str) -> dict:
    if not uri.strip():
        return {}
    test_file = "/usr/share/cups/ipptool/get-printer-attributes.test"
    result = _run(["ipptool", "-tv", uri, test_file], timeout=25)
    if result is None or result.returncode != 0:
        return {}
    attributes: dict = {}
    for line in result.stdout.splitlines():
        match = _ATTR_PATTERN.match(line)
        if match:
            key, _type, value = match.groups()
            attributes[key] = _parse_value(value)
    return attributes
