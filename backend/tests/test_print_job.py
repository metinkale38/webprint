from app.models.printer import Printer
from app.schemas.job import JobOptions
from app.services import print_job


def _options(color_mode: str = "monochrome") -> JobOptions:
    return JobOptions(
        copies=2,
        duplex="two-sided-long-edge",
        nup=2,
        color_mode=color_mode,
        page_range="1-2",
        media="A4",
    )


def _printer(capabilities: dict | None = None) -> Printer:
    return Printer(
        name="Test",
        slug="test",
        device_uri="ipp://192.0.2.10/ipp/print",
        capabilities=capabilities or {},
    )


def test_build_lp_options_without_printer():
    assert print_job.build_lp_options(_options()) == [
        "-n",
        "2",
        "-o",
        "sides=two-sided-long-edge",
        "-o",
        "number-up=2",
        "-o",
        "print-color-mode=monochrome",
        "-o",
        "media=A4",
        "-P",
        "1-2",
    ]


def test_uses_ipp_color_capability():
    args = print_job.build_lp_options(
        _options(), _printer({"print-color-mode-supported": ["color", "monochrome"]})
    )
    assert "print-color-mode=monochrome" in args


def test_falls_back_to_color_model(monkeypatch):
    monkeypatch.setattr(
        print_job.cups,
        "printer_options",
        lambda queue: {"ColorModel": ["Gray", "RGB"]},
    )
    args = print_job.build_lp_options(_options("color"), _printer())
    assert "ColorModel=RGB" in args


def test_falls_back_to_output_mode(monkeypatch):
    monkeypatch.setattr(
        print_job.cups,
        "printer_options",
        lambda queue: {"OutputMode": ["Monochrome", "Color"]},
    )
    args = print_job.build_lp_options(_options(), _printer())
    assert "OutputMode=Monochrome" in args


def test_defaults_to_ipp_attribute(monkeypatch):
    monkeypatch.setattr(print_job.cups, "printer_options", lambda queue: {})
    args = print_job.build_lp_options(_options(), _printer())
    assert "print-color-mode=monochrome" in args
