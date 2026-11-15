from ..models.printer import Printer
from ..schemas.job import JobOptions


def build_lp_options(options: JobOptions, printer: Printer | None = None) -> list[str]:
    """CUPS-Optionen aus den UI-Einstellungen bauen."""
    _ = printer
    args = [
        "-n",
        str(max(1, options.copies)),
        "-o",
        f"sides={options.duplex}",
        "-o",
        f"number-up={options.nup}",
        "-o",
        f"print-color-mode={options.color_mode}",
        "-o",
        f"media={options.media}",
    ]
    page_range = options.page_range.strip()
    if page_range:
        args += ["-P", page_range]
    return args
