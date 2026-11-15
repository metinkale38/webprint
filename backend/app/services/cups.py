import re
import subprocess
from pathlib import Path


def _run(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def submit_job(queue: str, file_path: Path, options: list[str]) -> str | None:
    result = _run(["lp", "-d", queue, *options, str(file_path)], timeout=60)
    if result is None or result.returncode != 0:
        return None
    match = re.search(r"request id is (\S+)", result.stdout)
    return match.group(1) if match else None


def cancel_job(cups_job_id: str) -> bool:
    result = _run(["cancel", cups_job_id])
    return result is not None and result.returncode == 0


def add_printer(name: str, device_uri: str, driver_mode: str = "everywhere") -> bool:
    result = _run(["lpadmin", "-p", name, "-v", device_uri, "-m", driver_mode, "-E"])
    return result is not None and result.returncode == 0


def remove_printer(name: str) -> bool:
    result = _run(["lpadmin", "-x", name])
    return result is not None and result.returncode == 0


def printer_status(name: str) -> str:
    result = _run(["lpstat", "-p", name])
    if result is None or result.returncode != 0:
        return "offline"
    if "is idle" in result.stdout:
        return "idle"
    if "is printing" in result.stdout:
        return "printing"
    if "disabled" in result.stdout:
        return "disabled"
    return "unknown"
