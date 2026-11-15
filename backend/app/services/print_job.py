from ..models.printer import Printer
from ..schemas.job import JobOptions
from . import cups

_MONO_VALUES = {"gray", "grayscale", "greyscale", "monochrome", "black"}
_COLOR_VALUES = {"rgb", "color", "colour", "cmyk"}


def _color_option(printer: Printer, color_mode: str) -> str:
    capabilities = printer.capabilities or {}
    if capabilities.get("print-color-mode-supported"):
        return f"print-color-mode={color_mode}"

    options = cups.printer_options(printer.slug)
    if "ColorModel" in options:
        values = options["ColorModel"]
        preferred = _MONO_VALUES if color_mode == "monochrome" else _COLOR_VALUES
        value = next((candidate for candidate in values if candidate.lower() in preferred), None)
        if value:
            return f"ColorModel={value}"

    if "OutputMode" in options:
        wanted = "monochrome" if color_mode == "monochrome" else "color"
        value = next(
            (candidate for candidate in options["OutputMode"] if candidate.lower() == wanted),
            None,
        )
        if value:
            return f"OutputMode={value}"

    return f"print-color-mode={color_mode}"


def build_lp_options(options: JobOptions, printer: Printer | None = None) -> list[str]:
    """CUPS-Optionen aus den UI-Einstellungen bauen."""
    args = [
        "-n",
        str(max(1, options.copies)),
        "-o",
        f"sides={options.duplex}",
        "-o",
        f"number-up={options.nup}",
    ]

    if printer is None:
        args += ["-o", f"print-color-mode={options.color_mode}"]
    else:
        args += ["-o", _color_option(printer, options.color_mode)]

    args += ["-o", f"media={options.media}"]

    page_range = options.page_range.strip()
    if page_range:
        args += ["-P", page_range]
    return args
