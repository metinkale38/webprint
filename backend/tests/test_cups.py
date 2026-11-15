from pathlib import Path

import pytest

from app.services import cups


class FakeResult:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_valid_queue_name():
    assert cups.valid_queue_name("test-drucker_1")
    assert not cups.valid_queue_name("mit leerzeichen")
    assert not cups.valid_queue_name("-start")
    assert not cups.valid_queue_name("")


def test_submit_job_parses_cups_job_id(monkeypatch):
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        return FakeResult(stdout="request id is test-drucker-42 (1 file(s))\n")

    monkeypatch.setattr(cups.subprocess, "run", fake_run)
    result = cups.submit_job("test-drucker", Path("/tmp/test.pdf"), ["-n", "2"])

    assert result == "test-drucker-42"
    assert calls[0][:3] == ["lp", "-d", "test-drucker"]


def test_submit_job_rejects_invalid_queue(monkeypatch):
    def fail_run(*_args, **_kwargs):
        raise AssertionError("subprocess darf nicht aufgerufen werden")

    monkeypatch.setattr(cups.subprocess, "run", fail_run)
    assert cups.submit_job("ungueltig queue", Path("/tmp/test.pdf"), []) is None


def test_add_printer_and_enable(monkeypatch):
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        return FakeResult()

    monkeypatch.setattr(cups.subprocess, "run", fake_run)
    assert cups.add_printer("test-drucker", "ipp://192.0.2.10/ipp/print")

    assert calls[0] == [
        "lpadmin",
        "-p",
        "test-drucker",
        "-v",
        "ipp://192.0.2.10/ipp/print",
        "-m",
        "everywhere",
        "-E",
    ]
    assert calls[1] == ["cupsenable", "test-drucker"]
    assert calls[2] == ["cupsaccept", "test-drucker"]


@pytest.mark.parametrize(
    ("stdout", "expected"),
    [
        ("printer test is idle. enabled since now", "idle"),
        ("printer test now printing test-1. enabled since now", "printing"),
        ("printer test disabled since now", "disabled"),
        ("printer test ist beschaeftigt", "unknown"),
    ],
)
def test_printer_status(monkeypatch, stdout, expected):
    monkeypatch.setattr(cups.subprocess, "run", lambda *_args, **_kwargs: FakeResult(stdout=stdout))
    assert cups.printer_status("test") == expected


def test_printer_status_offline(monkeypatch):
    monkeypatch.setattr(
        cups.subprocess,
        "run",
        lambda *_args, **_kwargs: FakeResult(returncode=1, stderr="does not exist"),
    )
    assert cups.printer_status("test") == "offline"


def test_probe_ipp_parses_attributes(monkeypatch):
    output = """
    printer-make-and-model (textWithoutLanguage) = Test Printer
    color-supported (boolean) = true
    sides-supported (1setOf keyword) = one-sided, two-sided-long-edge
    printer-state (enum) = idle
    """
    monkeypatch.setattr(cups.subprocess, "run", lambda *_args, **_kwargs: FakeResult(stdout=output))

    attributes = cups.probe_ipp("ipp://192.0.2.10/ipp/print")

    assert attributes["printer-make-and-model"] == "Test Printer"
    assert attributes["color-supported"] is True
    assert attributes["sides-supported"] == ["one-sided", "two-sided-long-edge"]
    assert attributes["printer-state"] == "idle"


def test_active_and_completed_job_ids(monkeypatch):
    def fake_run(command, **_kwargs):
        if "not-completed" in command:
            return FakeResult(stdout="printer-1 user 123 date\nprinter-2 user 123 date\n")
        if "completed" in command:
            return FakeResult(stdout="printer-3 user 123 date\n")
        return FakeResult()

    monkeypatch.setattr(cups.subprocess, "run", fake_run)

    assert cups.active_job_ids() == {"printer-1", "printer-2"}
    assert cups.completed_job_ids() == {"printer-3"}


def test_job_status(monkeypatch):
    monkeypatch.setattr(cups, "active_job_ids", lambda: {"printer-1"})
    monkeypatch.setattr(cups, "completed_job_ids", lambda: {"printer-2"})

    assert cups.job_status("printer-1") == "processing"
    assert cups.job_status("printer-2") == "completed"
    assert cups.job_status("printer-3") == "unknown"


def test_printer_options(monkeypatch):
    output = (
        "ColorModel/Color Mode: *Gray RGB\n"
        "Duplex/Two-Sided: *None DuplexNoTumble DuplexTumble\n"
    )
    monkeypatch.setattr(cups.subprocess, "run", lambda *_args, **_kwargs: FakeResult(stdout=output))

    options = cups.printer_options("test")

    assert options["ColorModel"] == ["Gray", "RGB"]
    assert options["Duplex"] == ["None", "DuplexNoTumble", "DuplexTumble"]
