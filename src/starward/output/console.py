"""
Rich console output for starward.

Provides styled terminal output using the Rich library.
"""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

if TYPE_CHECKING:
    from starward.verbose import VerboseContext

# Single console instance for the app
console = Console()

# Color scheme for astronomical data
COLORS = {
    'label': 'cyan',
    'value': 'white',
    'unit': 'dim',
    'positive': 'green',
    'negative': 'red',
    'warning': 'yellow',
    'planet': 'bold magenta',
    'time': 'blue',
    'header': 'bold cyan',
    'muted': 'dim',
    'accent': 'yellow',
}


def styled_value(value: Any, positive_threshold: float = None) -> Text:
    """
    Create styled text for a value.

    Args:
        value: The value to style
        positive_threshold: If set, values >= threshold are green, < are red
    """
    text = Text(str(value))

    if positive_threshold is not None:
        try:
            num_val = float(str(value).replace('°', '').replace('+', ''))
            if num_val >= positive_threshold:
                text.stylize(COLORS['positive'])
            else:
                text.stylize(COLORS['negative'])
        except (ValueError, TypeError):
            pass

    return text


def create_data_table(
    title: str,
    data: dict[str, Any],
    title_style: str = None,
    box_style: box.Box = box.ROUNDED,
) -> Table:
    """
    Create a two-column table for key-value data.

    Args:
        title: Table title
        data: Dictionary of label -> value pairs
        title_style: Optional style for the title
        box_style: Box style for the table border
    """
    table = Table(
        title=title,
        title_style=title_style or COLORS['header'],
        box=box_style,
        show_header=False,
        padding=(0, 1),
    )

    table.add_column("Label", style=COLORS['label'])
    table.add_column("Value", style=COLORS['value'])

    for label, value in data.items():
        if isinstance(value, Text):
            table.add_row(label, value)
        else:
            table.add_row(label, str(value))

    return table


def create_planet_table(
    title: str,
    headers: list[str],
    rows: list[list[Any]],
    column_styles: list[str] = None,
) -> Table:
    """
    Create a table for planetary data.

    Args:
        title: Table title
        headers: Column headers
        rows: List of row data
        column_styles: Optional list of styles for each column
    """
    table = Table(
        title=title,
        title_style=COLORS['header'],
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
        row_styles=["", "dim"],  # Alternating row styles
    )

    # Default column styles if not provided
    if column_styles is None:
        column_styles = [COLORS['planet']] + [COLORS['value']] * (len(headers) - 1)

    for header, style in zip(headers, column_styles):
        table.add_column(header, style=style)

    for row in rows:
        str_row = [str(cell) if not isinstance(cell, Text) else cell for cell in row]
        table.add_row(*str_row)

    return table


def print_result_panel(
    title: str,
    data: dict[str, Any],
    subtitle: str = None,
    border_style: str = "cyan",
) -> None:
    """
    Print a result in a styled panel.

    Args:
        title: Panel title
        data: Dictionary of label -> value pairs
        subtitle: Optional subtitle
        border_style: Border color
    """
    table = create_data_table(title="", data=data, box_style=box.SIMPLE)

    panel = Panel(
        table,
        title=f"[bold]{title}[/bold]",
        subtitle=f"[dim]{subtitle}[/dim]" if subtitle else None,
        border_style=border_style,
        padding=(0, 1),
    )

    console.print(panel)


def print_verbose_steps(vctx: VerboseContext) -> None:
    """
    Print verbose calculation steps with Rich styling.

    Args:
        vctx: VerboseContext containing the steps
    """
    if not vctx or not vctx.steps:
        return

    console.print()
    console.rule("[bold cyan]Calculation Steps[/bold cyan]", style="cyan")
    console.print()

    for step in vctx.steps:
        indent = "  " * step.level

        # Step title
        title_text = Text()
        title_text.append(f"{indent}[bold cyan]{step.title}[/bold cyan]")
        console.print(f"{indent}[cyan]┌─[/cyan] [bold]{step.title}[/bold]")

        # Step content
        if step.content:
            for line in step.content.split('\n'):
                console.print(f"{indent}[cyan]│[/cyan]  [dim]{line}[/dim]")

        console.print(f"{indent}[cyan]└{'─' * 40}[/cyan]")


def print_about_banner(version: str) -> None:
    """
    Print the styled about banner.

    Args:
        version: Version string to display
    """
    banner = """
[bold cyan]     _                                   _ [/bold cyan]
[bold cyan] ___| |_ __ _ _ ____      ____ _ _ __ __| |[/bold cyan]
[bold cyan]/ __| __/ _` | '__\\ \\ /\\ / / _` | '__/ _` |[/bold cyan]
[bold cyan]\\__ \\ || (_| | |   \\ V  V / (_| | | | (_| |[/bold cyan]
[bold cyan]|___/\\__\\__,_|_|    \\_/\\_/ \\__,_|_|  \\__,_|[/bold cyan]
"""

    content = Text()
    content.append("Astronomy Calculation Toolkit\n", style="bold")
    content.append("─" * 32 + "\n\n", style="dim")
    content.append("Version: ", style="cyan")
    content.append(f"{version}\n", style="white")
    content.append("License: ", style="cyan")
    content.append("MIT\n\n", style="white")
    content.append('"Per aspera ad astra"\n', style="italic yellow")
    content.append("Through hardships to the stars", style="dim italic")

    console.print(banner)
    console.print(Panel(
        content,
        border_style="cyan",
        padding=(1, 2),
    ))


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


def print_planet_position(
    symbol: str,
    name: str,
    time_str: str,
    jd: float,
    ra: str,
    dec: str,
    distance_au: float,
    helio_distance: float,
    magnitude: float,
    elongation: float,
    illumination: float,
    angular_diameter: float,
    vctx: Optional["VerboseContext"] = None,
) -> None:
    """
    Print styled planet position output.

    Args:
        symbol: Planet symbol (e.g., "")
        name: Planet name
        time_str: Formatted time string
        jd: Julian Date
        ra: Right ascension formatted string
        dec: Declination formatted string
        distance_au: Distance from Earth in AU
        helio_distance: Distance from Sun in AU
        magnitude: Visual magnitude
        elongation: Elongation in degrees
        illumination: Illumination fraction (0-1)
        angular_diameter: Angular diameter in arcseconds
        vctx: Optional verbose context
    """
    from rich.table import Table

    # Header
    console.print()
    console.print(f"  [bold magenta]{symbol}  {name}[/bold magenta]")
    console.rule(style="dim")

    # Time info
    time_table = Table(show_header=False, box=None, padding=(0, 2))
    time_table.add_column(style=COLORS['label'])
    time_table.add_column(style=COLORS['value'])
    time_table.add_row("Time", f"[{COLORS['time']}]{time_str} UTC[/{COLORS['time']}]")
    time_table.add_row("JD", f"{jd:.6f}")
    console.print(time_table)
    console.print()

    # Equatorial coordinates
    console.print("  [bold]Equatorial[/bold]")
    coord_table = Table(show_header=False, box=None, padding=(0, 2))
    coord_table.add_column(style=COLORS['label'])
    coord_table.add_column(style=COLORS['value'])
    coord_table.add_row("RA", ra)
    coord_table.add_row("Dec", dec)
    console.print(coord_table)
    console.print()

    # Distance
    console.print("  [bold]Distance[/bold]")
    dist_table = Table(show_header=False, box=None, padding=(0, 2))
    dist_table.add_column(style=COLORS['label'])
    dist_table.add_column(style=COLORS['value'])
    dist_table.add_row("From Earth", f"{distance_au:.6f} AU")
    dist_table.add_row("From Sun", f"{helio_distance:.6f} AU")
    console.print(dist_table)
    console.print()

    # Visual properties
    console.print("  [bold]Visual[/bold]")
    vis_table = Table(show_header=False, box=None, padding=(0, 2))
    vis_table.add_column(style=COLORS['label'])
    vis_table.add_column(style=COLORS['value'])

    # Color code magnitude (brighter = more negative = green)
    mag_style = COLORS['positive'] if magnitude < 0 else COLORS['value']
    vis_table.add_row("Magnitude", f"[{mag_style}]{magnitude:+.2f}[/{mag_style}]")
    vis_table.add_row("Elongation", f"{elongation:.1f}°")
    vis_table.add_row("Phase", f"{illumination * 100:.1f}% illuminated")
    vis_table.add_row("Diameter", f'{angular_diameter:.2f}"')
    console.print(vis_table)
    console.print()

    # Verbose steps
    if vctx:
        print_verbose_steps(vctx)


def print_all_planets_table(
    time_str: str,
    jd: float,
    planets_data: list[dict],
    vctx: Optional["VerboseContext"] = None,
) -> None:
    """
    Print styled table of all planets.

    Args:
        time_str: Formatted time string
        jd: Julian Date
        planets_data: List of dicts with planet info
        vctx: Optional verbose context
    """
    console.print()
    console.print("[bold cyan]Planetary Positions[/bold cyan]")
    console.rule(style="dim")
    console.print(f"  Time: [{COLORS['time']}]{time_str} UTC[/{COLORS['time']}]")
    console.print(f"  JD:   {jd:.6f}")
    console.print()

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
        row_styles=["", "dim"],
    )

    table.add_column("Planet", style=COLORS['planet'])
    table.add_column("RA", style=COLORS['value'])
    table.add_column("Dec", style=COLORS['value'])
    table.add_column("Dist", justify="right", style=COLORS['value'])
    table.add_column("Mag", justify="right")
    table.add_column("Elong", justify="right", style=COLORS['value'])

    for p in planets_data:
        # Color magnitude
        mag = p['magnitude']
        mag_style = COLORS['positive'] if mag < 0 else COLORS['value']
        mag_text = Text(f"{mag:+.1f}", style=mag_style)

        table.add_row(
            f"{p['symbol']} {p['name']}",
            p['ra'],
            p['dec'],
            f"{p['distance']:.3f}",
            mag_text,
            f"{p['elongation']:.1f}°",
        )

    console.print(table)
    console.print()

    if vctx:
        print_verbose_steps(vctx)


def print_messier_table(
    title: str,
    objects: list[dict],
    show_constellation: bool = True,
) -> None:
    """
    Print styled table of Messier objects.

    Args:
        title: Table title
        objects: List of dicts with object info
        show_constellation: Whether to show constellation column
    """
    console.print()
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.rule(style="dim")
    console.print()

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
    )

    table.add_column("M#", style="bold yellow", justify="right")
    table.add_column("Name", style=COLORS['value'], no_wrap=True)
    table.add_column("Type", style="cyan")
    table.add_column("Mag", justify="right")
    if show_constellation:
        table.add_column("Const", style=COLORS['muted'])

    for obj in objects:
        # Color magnitude - brighter objects (lower mag) get highlighted
        mag = obj['magnitude']
        if mag <= 5.0:
            mag_text = Text(f"{mag:.1f}", style="bold green")
        elif mag <= 8.0:
            mag_text = Text(f"{mag:.1f}", style="white")
        else:
            mag_text = Text(f"{mag:.1f}", style="dim")

        row = [
            f"M{obj['number']}",
            obj['name'],
            obj['type'],
            mag_text,
        ]
        if show_constellation:
            row.append(obj['constellation'])

        table.add_row(*row)

    console.print(table)
    console.print()
    console.print(f"  [dim]Total: {len(objects)} objects[/dim]")
    console.print()


def print_messier_detail(
    number: int,
    name: str,
    obj_type: str,
    ra: str,
    dec: str,
    magnitude: float,
    size: float,
    distance: str,
    constellation: str,
    ngc: str,
    description: str,
) -> None:
    """
    Print styled detail view of a Messier object.

    Args:
        number: Messier number
        name: Object name
        obj_type: Object type
        ra: Right ascension formatted
        dec: Declination formatted
        magnitude: Visual magnitude
        size: Angular size in arcmin
        distance: Distance string or None
        constellation: Constellation abbreviation
        ngc: NGC designation or None
        description: Object description
    """
    console.print()
    console.print(f"  [bold yellow]M{number}[/bold yellow] [dim]—[/dim] [bold cyan]{name}[/bold cyan]")
    console.rule(style="dim")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=COLORS['label'])
    table.add_column(style=COLORS['value'])

    table.add_row("Type", f"[cyan]{obj_type}[/cyan]")
    table.add_row("Coordinates", f"{ra}  {dec}")

    # Color magnitude
    if magnitude <= 5.0:
        mag_style = "bold green"
    elif magnitude <= 8.0:
        mag_style = "white"
    else:
        mag_style = "dim"
    table.add_row("Magnitude", f"[{mag_style}]{magnitude:.1f}[/{mag_style}]")

    table.add_row("Size", f"{size:.1f} arcmin")
    table.add_row("Distance", distance if distance else "[dim]Unknown[/dim]")
    table.add_row("Constellation", constellation)
    table.add_row("NGC", ngc if ngc else "[dim]—[/dim]")

    console.print(table)
    console.print()
    console.print(f"  [italic]{description}[/italic]")
    console.print()
