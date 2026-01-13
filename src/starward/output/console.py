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


def print_ngc_table(
    title: str,
    objects: list[dict],
    show_constellation: bool = True,
) -> None:
    """
    Print styled table of NGC objects.

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

    table.add_column("NGC", style="bold yellow", justify="right")
    table.add_column("Name", style=COLORS['value'], no_wrap=True)
    table.add_column("Type", style="cyan")
    table.add_column("Mag", justify="right")
    if show_constellation:
        table.add_column("Const", style=COLORS['muted'])
    table.add_column("Messier", style="dim", justify="right")

    for obj in objects:
        # Color magnitude based on brightness
        mag = obj.get('magnitude')
        if mag is None:
            mag_str = "[dim]—[/dim]"
        elif mag <= 5.0:
            mag_str = f"[bold green]{mag:.1f}[/bold green]"
        elif mag <= 8.0:
            mag_str = f"{mag:.1f}"
        else:
            mag_str = f"[dim]{mag:.1f}[/dim]"

        name = obj.get('name') or "[dim]—[/dim]"
        messier = f"M{obj['messier']}" if obj.get('messier') else ""

        row = [
            str(obj['number']),
            name,
            obj.get('type', ''),
            mag_str,
        ]
        if show_constellation:
            row.append(obj.get('constellation', ''))
        row.append(messier)

        table.add_row(*row)

    console.print(table)
    console.print()
    console.print(f"  [dim]Total: {len(objects)} objects[/dim]")
    console.print()


def print_ngc_detail(
    number: int,
    name: Optional[str],
    obj_type: str,
    ra: str,
    dec: str,
    magnitude: Optional[float],
    size: Optional[float],
    size_minor: Optional[float],
    distance: Optional[str],
    constellation: str,
    messier: Optional[str],
    hubble_type: Optional[str],
    description: str,
) -> None:
    """
    Print styled detail view of an NGC object.

    Args:
        number: NGC number
        name: Object name or None
        obj_type: Object type
        ra: Right ascension formatted
        dec: Declination formatted
        magnitude: Visual magnitude or None
        size: Angular size in arcmin or None
        size_minor: Minor axis in arcmin or None
        distance: Distance string or None
        constellation: Constellation abbreviation
        messier: Messier designation or None
        hubble_type: Hubble classification or None
        description: Object description
    """
    console.print()
    title = f"  [bold yellow]NGC {number}[/bold yellow]"
    if name:
        title += f" [dim]—[/dim] [bold cyan]{name}[/bold cyan]"
    console.print(title)
    console.rule(style="dim")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=COLORS['label'])
    table.add_column(style=COLORS['value'])

    table.add_row("Type", f"[cyan]{obj_type}[/cyan]")
    table.add_row("Coordinates", f"{ra}  {dec}")

    # Color magnitude
    if magnitude is not None:
        if magnitude <= 5.0:
            mag_style = "bold green"
        elif magnitude <= 8.0:
            mag_style = "white"
        else:
            mag_style = "dim"
        table.add_row("Magnitude", f"[{mag_style}]{magnitude:.1f}[/{mag_style}]")
    else:
        table.add_row("Magnitude", "[dim]Unknown[/dim]")

    # Size
    if size is not None:
        if size_minor is not None:
            size_str = f"{size:.1f} × {size_minor:.1f} arcmin"
        else:
            size_str = f"{size:.1f} arcmin"
        table.add_row("Size", size_str)
    else:
        table.add_row("Size", "[dim]Unknown[/dim]")

    table.add_row("Distance", distance if distance else "[dim]Unknown[/dim]")
    table.add_row("Constellation", constellation)

    if messier:
        table.add_row("Messier", f"[yellow]{messier}[/yellow]")

    if hubble_type:
        table.add_row("Hubble Type", hubble_type)

    console.print(table)
    console.print()
    if description:
        console.print(f"  [italic]{description}[/italic]")
    console.print()


def print_ngc_stats(stats: dict) -> None:
    """
    Print styled NGC catalog statistics.

    Args:
        stats: Dictionary with catalog statistics
    """
    console.print()
    console.print("[bold cyan]NGC Catalog Statistics[/bold cyan]")
    console.rule(style="dim")
    console.print()

    # Summary table
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column(style=COLORS['label'])
    summary.add_column(style=COLORS['value'])

    summary.add_row("Total Objects", f"[bold]{stats['total']:,}[/bold]")
    summary.add_row("With Common Name", str(stats.get('with_common_name', 0)))
    summary.add_row("With Messier ID", str(stats.get('with_messier_designation', 0)))

    console.print(summary)
    console.print()

    # Objects by type
    console.print("  [bold]Objects by Type[/bold]")
    by_type = stats.get('by_type', {})
    type_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    type_table.add_column(style="cyan")
    type_table.add_column(style=COLORS['value'], justify="right")

    for obj_type, count in sorted(by_type.items(), key=lambda x: -x[1])[:10]:
        type_name = obj_type.replace("_", " ").title()
        type_table.add_row(type_name, str(count))

    console.print(type_table)
    console.print()

    # Top constellations
    top_const = stats.get('top_constellations', {})
    if top_const:
        console.print("  [bold]Top Constellations[/bold]")
        const_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        const_table.add_column(style="cyan")
        const_table.add_column(style=COLORS['value'], justify="right")

        for const, count in list(top_const.items())[:5]:
            const_table.add_row(const, str(count))

        console.print(const_table)
        console.print()


def print_ic_table(
    title: str,
    objects: list[dict],
    show_constellation: bool = True,
) -> None:
    """
    Print styled table of IC objects.

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

    table.add_column("IC", style="bold yellow", justify="right")
    table.add_column("Name", style=COLORS['value'], no_wrap=True)
    table.add_column("Type", style="cyan")
    table.add_column("Mag", justify="right")
    if show_constellation:
        table.add_column("Const", style=COLORS['muted'])
    table.add_column("NGC", style="dim", justify="right")

    for obj in objects:
        # Color magnitude based on brightness
        mag = obj.get('magnitude')
        if mag is None:
            mag_str = "[dim]—[/dim]"
        elif mag <= 5.0:
            mag_str = f"[bold green]{mag:.1f}[/bold green]"
        elif mag <= 8.0:
            mag_str = f"{mag:.1f}"
        else:
            mag_str = f"[dim]{mag:.1f}[/dim]"

        name = obj.get('name') or "[dim]—[/dim]"
        ngc = f"NGC {obj['ngc']}" if obj.get('ngc') else ""

        row = [
            str(obj['number']),
            name,
            obj.get('type', ''),
            mag_str,
        ]
        if show_constellation:
            row.append(obj.get('constellation', ''))
        row.append(ngc)

        table.add_row(*row)

    console.print(table)
    console.print()
    console.print(f"  [dim]Total: {len(objects)} objects[/dim]")
    console.print()


def print_ic_detail(
    number: int,
    name: Optional[str],
    obj_type: str,
    ra: str,
    dec: str,
    magnitude: Optional[float],
    size: Optional[float],
    size_minor: Optional[float],
    distance: Optional[str],
    constellation: str,
    ngc: Optional[str],
    hubble_type: Optional[str],
    description: str,
) -> None:
    """
    Print styled detail view of an IC object.

    Args:
        number: IC number
        name: Object name or None
        obj_type: Object type
        ra: Right ascension formatted
        dec: Declination formatted
        magnitude: Visual magnitude or None
        size: Angular size in arcmin or None
        size_minor: Minor axis in arcmin or None
        distance: Distance string or None
        constellation: Constellation abbreviation
        ngc: NGC designation or None
        hubble_type: Hubble classification or None
        description: Object description
    """
    console.print()
    title = f"  [bold yellow]IC {number}[/bold yellow]"
    if name:
        title += f" [dim]—[/dim] [bold cyan]{name}[/bold cyan]"
    console.print(title)
    console.rule(style="dim")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=COLORS['label'])
    table.add_column(style=COLORS['value'])

    table.add_row("Type", f"[cyan]{obj_type}[/cyan]")
    table.add_row("Coordinates", f"{ra}  {dec}")

    # Color magnitude
    if magnitude is not None:
        if magnitude <= 5.0:
            mag_style = "bold green"
        elif magnitude <= 8.0:
            mag_style = "white"
        else:
            mag_style = "dim"
        table.add_row("Magnitude", f"[{mag_style}]{magnitude:.1f}[/{mag_style}]")
    else:
        table.add_row("Magnitude", "[dim]Unknown[/dim]")

    # Size
    if size is not None:
        if size_minor is not None:
            size_str = f"{size:.1f} × {size_minor:.1f} arcmin"
        else:
            size_str = f"{size:.1f} arcmin"
        table.add_row("Size", size_str)
    else:
        table.add_row("Size", "[dim]Unknown[/dim]")

    table.add_row("Distance", distance if distance else "[dim]Unknown[/dim]")
    table.add_row("Constellation", constellation)

    if ngc:
        table.add_row("NGC", f"[yellow]{ngc}[/yellow]")

    if hubble_type:
        table.add_row("Hubble Type", hubble_type)

    console.print(table)
    console.print()
    if description:
        console.print(f"  [italic]{description}[/italic]")
    console.print()


def print_ic_stats(stats: dict) -> None:
    """
    Print styled IC catalog statistics.

    Args:
        stats: Dictionary with catalog statistics
    """
    console.print()
    console.print("[bold cyan]IC Catalog Statistics[/bold cyan]")
    console.rule(style="dim")
    console.print()

    # Summary table
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column(style=COLORS['label'])
    summary.add_column(style=COLORS['value'])

    summary.add_row("Total Objects", f"[bold]{stats['total']:,}[/bold]")
    summary.add_row("With Common Name", str(stats.get('with_common_name', 0)))
    summary.add_row("With NGC ID", str(stats.get('with_ngc_designation', 0)))

    console.print(summary)
    console.print()

    # Objects by type
    console.print("  [bold]Objects by Type[/bold]")
    by_type = stats.get('by_type', {})
    type_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    type_table.add_column(style="cyan")
    type_table.add_column(style=COLORS['value'], justify="right")

    for obj_type, count in sorted(by_type.items(), key=lambda x: -x[1])[:10]:
        type_name = obj_type.replace("_", " ").title()
        type_table.add_row(type_name, str(count))

    console.print(type_table)
    console.print()

    # Top constellations
    top_const = stats.get('top_constellations', {})
    if top_const:
        console.print("  [bold]Top Constellations[/bold]")
        const_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        const_table.add_column(style="cyan")
        const_table.add_column(style=COLORS['value'], justify="right")

        for const, count in list(top_const.items())[:5]:
            const_table.add_row(const, str(count))

        console.print(const_table)
        console.print()


# =============================================================================
# Hipparcos Star Catalog Output
# =============================================================================

def print_stars_table(
    title: str,
    stars: list[dict],
    show_constellation: bool = True,
) -> None:
    """
    Print styled table of Hipparcos stars.

    Args:
        title: Table title
        stars: List of dicts with star info
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

    table.add_column("HIP", style="dim", justify="right")
    table.add_column("Name", style="bold yellow", no_wrap=True)
    table.add_column("Mag", justify="right")
    table.add_column("Spectral", style="cyan")
    if show_constellation:
        table.add_column("Const", style=COLORS['muted'])
    table.add_column("Distance", justify="right")

    for star in stars:
        # Color magnitude based on brightness
        mag = star.get('magnitude')
        if mag is None:
            mag_str = "[dim]—[/dim]"
        elif mag < 0:
            mag_str = f"[bold magenta]{mag:.2f}[/bold magenta]"
        elif mag <= 1.0:
            mag_str = f"[bold green]{mag:.2f}[/bold green]"
        elif mag <= 3.0:
            mag_str = f"[green]{mag:.2f}[/green]"
        else:
            mag_str = f"{mag:.2f}"

        # Format distance
        dist = star.get('distance')
        if dist is not None:
            dist_str = f"{dist:.1f} ly"
        else:
            dist_str = "[dim]—[/dim]"

        name = star.get('name', f"HIP {star.get('hip', '')}")

        row = [
            str(star.get('hip', '')),
            name,
            mag_str,
            star.get('spectral', '') or "[dim]—[/dim]",
        ]
        if show_constellation:
            row.append(star.get('constellation', ''))
        row.append(dist_str)

        table.add_row(*row)

    console.print(table)
    console.print()
    console.print(f"  [dim]Total: {len(stars)} stars[/dim]")
    console.print()


def print_star_detail(
    hip_number: int,
    name: Optional[str],
    bayer: Optional[str],
    flamsteed: Optional[int],
    ra: str,
    dec: str,
    magnitude: float,
    bv_color: Optional[float],
    spectral_type: Optional[str],
    parallax: Optional[float],
    distance_ly: Optional[float],
    proper_motion_ra: Optional[float],
    proper_motion_dec: Optional[float],
    radial_velocity: Optional[float],
    constellation: str,
) -> None:
    """
    Print styled detail view of a Hipparcos star.

    Args:
        hip_number: Hipparcos catalog number
        name: Common name or None
        bayer: Bayer designation or None
        flamsteed: Flamsteed number or None
        ra: Right ascension formatted
        dec: Declination formatted
        magnitude: Visual magnitude
        bv_color: B-V color index or None
        spectral_type: Spectral classification or None
        parallax: Parallax in mas or None
        distance_ly: Distance in light-years or None
        proper_motion_ra: Proper motion in RA or None
        proper_motion_dec: Proper motion in Dec or None
        radial_velocity: Radial velocity or None
        constellation: Constellation abbreviation
    """
    console.print()
    title = f"  [bold yellow]HIP {hip_number}[/bold yellow]"
    if name:
        title += f" [dim]—[/dim] [bold cyan]{name}[/bold cyan]"
    console.print(title)
    console.rule(style="dim")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=COLORS['label'])
    table.add_column(style=COLORS['value'])

    # Designations
    if bayer:
        table.add_row("Bayer", bayer)
    if flamsteed and constellation:
        table.add_row("Flamsteed", f"{flamsteed} {constellation}")

    table.add_row("Coordinates", f"{ra}  {dec}")

    # Color magnitude based on brightness
    if magnitude < 0:
        mag_style = "bold magenta"
    elif magnitude <= 1.0:
        mag_style = "bold green"
    elif magnitude <= 3.0:
        mag_style = "green"
    else:
        mag_style = "white"
    table.add_row("Magnitude", f"[{mag_style}]{magnitude:.2f}[/{mag_style}]")

    if spectral_type:
        table.add_row("Spectral Type", f"[cyan]{spectral_type}[/cyan]")

    if bv_color is not None:
        # Color B-V based on actual star color
        if bv_color < 0:
            bv_style = "blue"
        elif bv_color < 0.3:
            bv_style = "white"
        elif bv_color < 0.6:
            bv_style = "yellow"
        elif bv_color < 1.0:
            bv_style = "bright_red"
        else:
            bv_style = "red"
        table.add_row("B-V Color", f"[{bv_style}]{bv_color:+.2f}[/{bv_style}]")

    table.add_row("Constellation", constellation)

    console.print(table)
    console.print()

    # Astrometric data section
    if parallax is not None or distance_ly is not None or proper_motion_ra is not None:
        console.print("  [bold]Astrometric Data[/bold]")
        astro_table = Table(show_header=False, box=None, padding=(0, 2))
        astro_table.add_column(style=COLORS['label'])
        astro_table.add_column(style=COLORS['value'])

        if distance_ly is not None:
            if distance_ly < 50:
                dist_style = "bold green"
            elif distance_ly < 200:
                dist_style = "green"
            else:
                dist_style = "white"
            astro_table.add_row("Distance", f"[{dist_style}]{distance_ly:.1f} light-years[/{dist_style}]")

        if parallax is not None:
            astro_table.add_row("Parallax", f"{parallax:.2f} mas")

        if proper_motion_ra is not None and proper_motion_dec is not None:
            astro_table.add_row("Proper Motion",
                f"RA: {proper_motion_ra:+.2f} mas/yr  Dec: {proper_motion_dec:+.2f} mas/yr")

        if radial_velocity is not None:
            rv_style = "green" if radial_velocity < 0 else "red"
            astro_table.add_row("Radial Velocity", f"[{rv_style}]{radial_velocity:+.1f} km/s[/{rv_style}]")

        console.print(astro_table)
    console.print()


def print_stars_stats(stats: dict) -> None:
    """
    Print styled Hipparcos catalog statistics.

    Args:
        stats: Dictionary with catalog statistics
    """
    console.print()
    console.print("[bold cyan]Hipparcos Catalog Statistics[/bold cyan]")
    console.rule(style="dim")
    console.print()

    # Summary table
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column(style=COLORS['label'])
    summary.add_column(style=COLORS['value'])

    summary.add_row("Total Stars", f"[bold]{stats['total']:,}[/bold]")
    summary.add_row("With Common Name", str(stats.get('with_common_name', 0)))

    # Brightest star
    brightest = stats.get('brightest')
    if brightest:
        summary.add_row("Brightest Star",
            f"[yellow]{brightest['name']}[/yellow] (mag {brightest['magnitude']:.2f})")

    # Magnitude range
    mag_range = stats.get('magnitude_range', {})
    if mag_range:
        summary.add_row("Magnitude Range",
            f"{mag_range.get('min', '?'):.2f} to {mag_range.get('max', '?'):.2f}")

    console.print(summary)
    console.print()

    # Stars by spectral class
    console.print("  [bold]Stars by Spectral Class[/bold]")
    by_spectral = stats.get('by_spectral_class', {})
    spectral_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    spectral_table.add_column(style="cyan")
    spectral_table.add_column(style=COLORS['value'], justify="right")

    # Sort by standard spectral order
    spectral_order = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    for sp in spectral_order:
        if sp in by_spectral:
            spectral_table.add_row(f"Class {sp}", str(by_spectral[sp]))
    # Add any others
    for sp, count in sorted(by_spectral.items()):
        if sp not in spectral_order:
            spectral_table.add_row(f"Class {sp}", str(count))

    console.print(spectral_table)
    console.print()

    # Top constellations
    top_const = stats.get('top_constellations', {})
    if top_const:
        console.print("  [bold]Top Constellations[/bold]")
        const_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        const_table.add_column(style="cyan")
        const_table.add_column(style=COLORS['value'], justify="right")

        for const, count in list(top_const.items())[:5]:
            const_table.add_row(const, str(count))

        console.print(const_table)
        console.print()


# =============================================================================
# Caldwell Catalog Output
# =============================================================================

def print_caldwell_table(
    title: str,
    objects: list[dict],
    show_constellation: bool = True,
) -> None:
    """
    Print styled table of Caldwell objects.

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

    table.add_column("C", style="bold yellow", justify="right")
    table.add_column("Name", style=COLORS['value'], no_wrap=True)
    table.add_column("Type", style="cyan")
    table.add_column("Mag", justify="right")
    if show_constellation:
        table.add_column("Const", style=COLORS['muted'])
    table.add_column("NGC/IC", style="dim", justify="right")

    for obj in objects:
        # Color magnitude based on brightness
        mag = obj.get('magnitude')
        if mag is None:
            mag_str = "[dim]—[/dim]"
        elif mag <= 5.0:
            mag_str = f"[bold green]{mag:.1f}[/bold green]"
        elif mag <= 8.0:
            mag_str = f"{mag:.1f}"
        else:
            mag_str = f"[dim]{mag:.1f}[/dim]"

        name = obj.get('name') or "[dim]—[/dim]"

        # NGC/IC cross-reference
        cross_ref = ""
        if obj.get('ngc'):
            cross_ref = f"NGC {obj['ngc']}"
        elif obj.get('ic'):
            cross_ref = f"IC {obj['ic']}"

        row = [
            str(obj['number']),
            name,
            obj.get('type', ''),
            mag_str,
        ]
        if show_constellation:
            row.append(obj.get('constellation', ''))
        row.append(cross_ref)

        table.add_row(*row)

    console.print(table)
    console.print()
    console.print(f"  [dim]Total: {len(objects)} objects[/dim]")
    console.print()


def print_caldwell_detail(
    number: int,
    name: Optional[str],
    obj_type: str,
    ra: str,
    dec: str,
    magnitude: Optional[float],
    size: Optional[float],
    size_minor: Optional[float],
    distance: Optional[str],
    constellation: str,
    ngc: Optional[str],
    ic: Optional[str],
    description: str,
) -> None:
    """
    Print styled detail view of a Caldwell object.

    Args:
        number: Caldwell number
        name: Object name or None
        obj_type: Object type
        ra: Right ascension formatted
        dec: Declination formatted
        magnitude: Visual magnitude or None
        size: Angular size in arcmin or None
        size_minor: Minor axis in arcmin or None
        distance: Distance string or None
        constellation: Constellation abbreviation
        ngc: NGC designation or None
        ic: IC designation or None
        description: Object description
    """
    console.print()
    title = f"  [bold yellow]C {number}[/bold yellow]"
    if name:
        title += f" [dim]—[/dim] [bold cyan]{name}[/bold cyan]"
    console.print(title)
    console.rule(style="dim")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style=COLORS['label'])
    table.add_column(style=COLORS['value'])

    table.add_row("Type", f"[cyan]{obj_type}[/cyan]")
    table.add_row("Coordinates", f"{ra}  {dec}")

    # Color magnitude
    if magnitude is not None:
        if magnitude <= 5.0:
            mag_style = "bold green"
        elif magnitude <= 8.0:
            mag_style = "white"
        else:
            mag_style = "dim"
        table.add_row("Magnitude", f"[{mag_style}]{magnitude:.1f}[/{mag_style}]")
    else:
        table.add_row("Magnitude", "[dim]Unknown[/dim]")

    # Size
    if size is not None:
        if size_minor is not None:
            size_str = f"{size:.1f} × {size_minor:.1f} arcmin"
        else:
            size_str = f"{size:.1f} arcmin"
        table.add_row("Size", size_str)
    else:
        table.add_row("Size", "[dim]Unknown[/dim]")

    table.add_row("Distance", distance if distance else "[dim]Unknown[/dim]")
    table.add_row("Constellation", constellation)

    if ngc:
        table.add_row("NGC", f"[yellow]{ngc}[/yellow]")

    if ic:
        table.add_row("IC", f"[yellow]{ic}[/yellow]")

    console.print(table)
    console.print()
    if description:
        console.print(f"  [italic]{description}[/italic]")
    console.print()


def print_caldwell_stats(stats: dict) -> None:
    """
    Print styled Caldwell catalog statistics.

    Args:
        stats: Dictionary with catalog statistics
    """
    console.print()
    console.print("[bold cyan]Caldwell Catalog Statistics[/bold cyan]")
    console.rule(style="dim")
    console.print()

    # Summary table
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column(style=COLORS['label'])
    summary.add_column(style=COLORS['value'])

    summary.add_row("Total Objects", f"[bold]{stats['total']:,}[/bold]")
    summary.add_row("With Common Name", str(stats.get('with_common_name', 0)))
    summary.add_row("With NGC ID", str(stats.get('with_ngc_designation', 0)))
    summary.add_row("With IC ID", str(stats.get('with_ic_designation', 0)))

    console.print(summary)
    console.print()

    # Objects by type
    console.print("  [bold]Objects by Type[/bold]")
    by_type = stats.get('by_type', {})
    type_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    type_table.add_column(style="cyan")
    type_table.add_column(style=COLORS['value'], justify="right")

    for obj_type, count in sorted(by_type.items(), key=lambda x: -x[1])[:10]:
        type_name = obj_type.replace("_", " ").title()
        type_table.add_row(type_name, str(count))

    console.print(type_table)
    console.print()

    # Top constellations
    top_const = stats.get('top_constellations', {})
    if top_const:
        console.print("  [bold]Top Constellations[/bold]")
        const_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        const_table.add_column(style="cyan")
        const_table.add_column(style=COLORS['value'], justify="right")

        for const, count in list(top_const.items())[:5]:
            const_table.add_row(const, str(count))

        console.print(const_table)
        console.print()


# =============================================================================
# Finder Output
# =============================================================================

def print_finder_table(
    title: str,
    results: list,
    show_catalog: bool = True,
) -> None:
    """
    Print styled table of finder results.

    Args:
        title: Table title
        results: List of FinderResult objects
        show_catalog: Whether to show catalog column
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

    if show_catalog:
        table.add_column("Cat", style="dim", justify="center")
    table.add_column("Designation", style="bold yellow")
    table.add_column("Name", style=COLORS['value'], no_wrap=True)
    table.add_column("Type", style="cyan")
    table.add_column("Mag", justify="right")
    table.add_column("Const", style=COLORS['muted'])

    for r in results:
        # Color magnitude based on brightness
        mag = r.magnitude
        if mag is None:
            mag_str = "[dim]—[/dim]"
        elif mag <= 5.0:
            mag_str = f"[bold green]{mag:.1f}[/bold green]"
        elif mag <= 8.0:
            mag_str = f"{mag:.1f}"
        else:
            mag_str = f"[dim]{mag:.1f}[/dim]"

        name = r.name or "[dim]—[/dim]"

        # Catalog abbreviation
        cat_abbrev = {
            "ngc": "NGC",
            "ic": "IC",
            "caldwell": "C",
            "hipparcos": "HIP",
            "messier": "M",
        }
        cat_str = cat_abbrev.get(r.catalog.value, r.catalog.value.upper())

        # Type name
        type_name = r.object_type.replace("_", " ").title()
        # Shorten common types
        type_abbrev = {
            "Planetary Nebula": "Plan. Neb.",
            "Emission Nebula": "Em. Neb.",
            "Reflection Nebula": "Refl. Neb.",
            "Globular Cluster": "Glob. Cl.",
            "Open Cluster": "Open Cl.",
            "Star Cluster": "Star Cl.",
            "Supernova Remnant": "SNR",
            "Galaxy Pair": "Gal. Pair",
            "Galaxy Group": "Gal. Grp",
        }
        type_str = type_abbrev.get(type_name, type_name)

        row = []
        if show_catalog:
            row.append(cat_str)
        row.extend([
            r.designation,
            name,
            type_str,
            mag_str,
            r.constellation,
        ])

        table.add_row(*row)

    console.print(table)
    console.print()
    console.print(f"  [dim]Found: {len(results)} objects[/dim]")
    console.print()

# =============================================================================
# Observation List Output
# =============================================================================

def print_lists_table(lists: list) -> None:
    """
    Print styled table of observation lists.

    Args:
        lists: List of ObservationList objects
    """
    console.print()
    console.print("[bold cyan]Observation Lists[/bold cyan]")
    console.rule(style="dim")
    console.print()

    if not lists:
        console.print("  [dim]No lists found. Create one with:[/dim]")
        console.print('  [yellow]starward list create "My List"[/yellow]')
        console.print()
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
    )

    table.add_column("Name", style="bold yellow")
    table.add_column("Objects", justify="right")
    table.add_column("Description", style=COLORS['muted'])
    table.add_column("Updated", style="dim")

    for lst in lists:
        item_count = len(lst)
        count_style = "bold green" if item_count > 0 else "dim"

        table.add_row(
            lst.name,
            f"[{count_style}]{item_count}[/{count_style}]",
            lst.description or "[dim]—[/dim]",
            lst.updated_at.strftime("%Y-%m-%d"),
        )

    console.print(table)
    console.print()
    console.print(f"  [dim]Total: {len(lists)} lists[/dim]")
    console.print()


def print_list_detail(obs_list) -> None:
    """
    Print styled detail view of an observation list.

    Args:
        obs_list: ObservationList object
    """
    console.print()
    title = f"  [bold yellow]{obs_list.name}[/bold yellow]"
    if obs_list.description:
        title += f" [dim]—[/dim] [italic]{obs_list.description}[/italic]"
    console.print(title)
    console.rule(style="dim")
    console.print()

    if not obs_list.items:
        console.print("  [dim]No items in this list. Add objects with:[/dim]")
        console.print(f'  [yellow]starward list add "{obs_list.name}" M31[/yellow]')
        console.print()
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold",
    )

    table.add_column("#", style="dim", justify="right")
    table.add_column("Object", style="bold yellow")
    table.add_column("Name", style=COLORS['value'])
    table.add_column("Notes", style=COLORS['muted'])

    for i, item in enumerate(obs_list.items, 1):
        table.add_row(
            str(i),
            item.designation,
            item.display_name or "[dim]—[/dim]",
            item.notes or "[dim]—[/dim]",
        )

    console.print(table)
    console.print()
    console.print(f"  [dim]{len(obs_list.items)} objects • Created {obs_list.created_at.strftime('%Y-%m-%d')}[/dim]")
    console.print()


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]✗[/bold red] {message}")
