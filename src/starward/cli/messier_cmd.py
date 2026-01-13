"""
Messier catalog CLI commands.
"""

from __future__ import annotations

import click
from typing import Optional

from starward.core.messier import (
    MESSIER,
    OBJECT_TYPES,
    messier_coords,
    messier_altitude,
    messier_airmass,
    messier_rise,
    messier_set,
    messier_transit,
    messier_transit_altitude,
)
from starward.core.observer import Observer, get_observer
from starward.core.time import JulianDate, jd_now
from starward.verbose import VerboseContext


def _get_observer_from_options(lat: Optional[float], lon: Optional[float],
                                observer_name: Optional[str]) -> Optional[Observer]:
    """Get observer from CLI options."""
    if lat is not None and lon is not None:
        return Observer.from_degrees("CLI", lat, lon)
    elif observer_name:
        obs = get_observer(observer_name)
        if obs is None:
            raise click.ClickException(f"Observer '{observer_name}' not found. Use 'starward observer list' to see available observers.")
        return obs
    else:
        obs = get_observer()  # Default observer
        if obs is None:
            raise click.ClickException(
                "No observer specified. Use --lat/--lon or --observer, "
                "or add a default observer with 'starward observer add'"
            )
        return obs


def _format_object_type(obj_type: str) -> str:
    """Format object type for display."""
    return obj_type.replace("_", " ").title()


@click.group(name='messier')
def messier_group():
    """
    Messier catalog browser.

    \b
    Browse and search the 110 Messier objects - galaxies,
    nebulae, and star clusters cataloged by Charles Messier.

    \b
    Examples:
        starward messier list                    # List all objects
        starward messier show 31                 # Show M31 details
        starward messier search orion            # Search by name
        starward messier list --type galaxy      # Filter by type
    """
    pass


@messier_group.command(name='list')
@click.option('--type', 'obj_type', type=click.Choice(OBJECT_TYPES, case_sensitive=False),
              help='Filter by object type')
@click.option('--constellation', type=str, help='Filter by constellation (3-letter abbr)')
@click.option('--magnitude', type=float, help='Show objects brighter than magnitude')
@click.pass_context
def list_cmd(ctx, obj_type: Optional[str], constellation: Optional[str],
             magnitude: Optional[float]):
    """List Messier objects with optional filters."""
    output_fmt = ctx.obj.get('output', 'plain')

    objects = MESSIER.list_all()

    # Apply filters
    if obj_type:
        objects = [o for o in objects if o.object_type.lower() == obj_type.lower()]
    if constellation:
        objects = [o for o in objects if o.constellation.lower() == constellation.lower()]
    if magnitude is not None:
        objects = [o for o in objects if o.magnitude <= magnitude]

    if not objects:
        click.echo("No objects match the specified filters.")
        return

    if output_fmt == 'json':
        import json
        data = {
            'count': len(objects),
            'objects': [
                {
                    'number': o.number,
                    'name': o.name,
                    'type': o.object_type,
                    'ra_hours': o.ra_hours,
                    'dec_degrees': o.dec_degrees,
                    'magnitude': o.magnitude,
                    'size_arcmin': o.size_arcmin,
                    'distance_kly': o.distance_kly,
                    'constellation': o.constellation,
                    'ngc': o.ngc,
                }
                for o in objects
            ]
        }
        click.echo(json.dumps(data, indent=2))
    else:
        # Build header based on filters
        if obj_type:
            header = f"Messier {_format_object_type(obj_type)}s"
        elif constellation:
            header = f"Messier Objects in {constellation.upper()}"
        else:
            header = "Messier Catalog"

        if magnitude is not None:
            header += f" (mag ≤ {magnitude:.1f})"

        from starward.output.console import print_messier_table
        objects_data = [
            {
                'number': o.number,
                'name': o.name,
                'type': _format_object_type(o.object_type),
                'magnitude': o.magnitude,
                'constellation': o.constellation,
            }
            for o in objects
        ]
        print_messier_table(header, objects_data)


@messier_group.command(name='show')
@click.argument('number', type=int)
@click.pass_context
def show_cmd(ctx, number: int):
    """Show detailed information about a Messier object."""
    output_fmt = ctx.obj.get('output', 'plain')

    try:
        obj = MESSIER.get(number)
    except KeyError:
        raise click.ClickException(f"M{number} is not in the Messier catalog (valid range: 1-110)")

    coords = messier_coords(number)

    if output_fmt == 'json':
        import json
        data = {
            'number': obj.number,
            'name': obj.name,
            'type': obj.object_type,
            'ra_hours': obj.ra_hours,
            'dec_degrees': obj.dec_degrees,
            'ra_formatted': coords.ra.format_hms(),
            'dec_formatted': coords.dec.format_dms(),
            'magnitude': obj.magnitude,
            'size_arcmin': obj.size_arcmin,
            'distance_kly': obj.distance_kly,
            'constellation': obj.constellation,
            'ngc': obj.ngc,
            'description': obj.description,
        }
        click.echo(json.dumps(data, indent=2))
    else:
        distance_str = f"{obj.distance_kly:,.0f} kly" if obj.distance_kly else None
        ngc_str = obj.ngc if obj.ngc else None

        from starward.output.console import print_messier_detail
        print_messier_detail(
            number=obj.number,
            name=obj.name,
            obj_type=_format_object_type(obj.object_type),
            ra=coords.ra.format_hms(),
            dec=coords.dec.format_dms(),
            magnitude=obj.magnitude,
            size=obj.size_arcmin,
            distance=distance_str,
            constellation=obj.constellation,
            ngc=ngc_str,
            description=obj.description,
        )


@messier_group.command(name='search')
@click.argument('query')
@click.pass_context
def search_cmd(ctx, query: str):
    """Search Messier objects by name, type, or constellation."""
    output_fmt = ctx.obj.get('output', 'plain')

    results = MESSIER.search(query)

    if not results:
        click.echo(f"No Messier objects match '{query}'")
        return

    if output_fmt == 'json':
        import json
        data = {
            'query': query,
            'count': len(results),
            'objects': [
                {
                    'number': o.number,
                    'name': o.name,
                    'type': o.object_type,
                    'magnitude': o.magnitude,
                    'constellation': o.constellation,
                }
                for o in results
            ]
        }
        click.echo(json.dumps(data, indent=2))
    else:
        from starward.output.console import print_messier_table
        objects_data = [
            {
                'number': o.number,
                'name': o.name,
                'type': _format_object_type(o.object_type),
                'magnitude': o.magnitude,
                'constellation': o.constellation,
            }
            for o in results
        ]
        print_messier_table(f'Search Results for "{query}"', objects_data)


@messier_group.command(name='altitude')
@click.argument('number', type=int)
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def altitude_cmd(ctx, number: int, lat: Optional[float], lon: Optional[float],
                 observer_name: Optional[str], jd: Optional[float]):
    """Calculate current altitude of a Messier object."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    try:
        obj = MESSIER.get(number)
    except KeyError:
        raise click.ClickException(f"M{number} is not in the Messier catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    alt = messier_altitude(number, observer, jd_val, vctx)
    air = messier_airmass(number, observer, jd_val)

    if output_fmt == 'json':
        import json
        data = {
            'object': f'M{number}',
            'name': obj.name,
            'observer': observer.name,
            'jd': jd_val.jd,
            'altitude_degrees': alt.degrees,
            'airmass': air,
            'is_visible': alt.degrees > 0,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = jd_val.to_datetime()
        visibility = "Above horizon" if alt.degrees > 0 else "Below horizon"
        airmass_str = f"{air:.2f}" if air else "N/A"
        click.echo(f"""
  M{number} — {obj.name} Altitude
  {'─' * 45}
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Altitude:   {alt.degrees:+.2f}°
  Airmass:    {airmass_str}
  Status:     {visibility}
""")
        if vctx:
            click.echo(vctx.format_steps())


@messier_group.command(name='rise')
@click.argument('number', type=int)
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def rise_cmd(ctx, number: int, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Calculate rise time of a Messier object."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    try:
        obj = MESSIER.get(number)
    except KeyError:
        raise click.ClickException(f"M{number} is not in the Messier catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    rise_time = messier_rise(number, observer, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'object': f'M{number}',
            'name': obj.name,
            'observer': observer.name,
            'date_jd': jd_val.jd,
            'rise_jd': rise_time.jd if rise_time else None,
            'rise_utc': rise_time.to_datetime().isoformat() if rise_time else None,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        if rise_time:
            dt = rise_time.to_datetime()
            click.echo(f"""
  M{number} — {obj.name} Rise
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Rise Time:  {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Rise JD:    {rise_time.jd:.6f}
""")
        else:
            click.echo(f"""
  M{number} — {obj.name} Rise
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  M{number} does not rise from this location (circumpolar or never visible).
""")
        if vctx:
            click.echo(vctx.format_steps())


@messier_group.command(name='set')
@click.argument('number', type=int)
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def set_cmd(ctx, number: int, lat: Optional[float], lon: Optional[float],
            observer_name: Optional[str], jd: Optional[float]):
    """Calculate set time of a Messier object."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    try:
        obj = MESSIER.get(number)
    except KeyError:
        raise click.ClickException(f"M{number} is not in the Messier catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    set_time = messier_set(number, observer, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'object': f'M{number}',
            'name': obj.name,
            'observer': observer.name,
            'date_jd': jd_val.jd,
            'set_jd': set_time.jd if set_time else None,
            'set_utc': set_time.to_datetime().isoformat() if set_time else None,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        if set_time:
            dt = set_time.to_datetime()
            click.echo(f"""
  M{number} — {obj.name} Set
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Set Time:   {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Set JD:     {set_time.jd:.6f}
""")
        else:
            click.echo(f"""
  M{number} — {obj.name} Set
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  M{number} does not set from this location (circumpolar or never visible).
""")
        if vctx:
            click.echo(vctx.format_steps())


@messier_group.command(name='transit')
@click.argument('number', type=int)
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def transit_cmd(ctx, number: int, lat: Optional[float], lon: Optional[float],
                observer_name: Optional[str], jd: Optional[float]):
    """Calculate transit time of a Messier object."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    try:
        obj = MESSIER.get(number)
    except KeyError:
        raise click.ClickException(f"M{number} is not in the Messier catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    trans_time = messier_transit(number, observer, jd_val, vctx)
    trans_alt = messier_transit_altitude(number, observer)

    if output_fmt == 'json':
        import json
        data = {
            'object': f'M{number}',
            'name': obj.name,
            'observer': observer.name,
            'date_jd': jd_val.jd,
            'transit_jd': trans_time.jd,
            'transit_utc': trans_time.to_datetime().isoformat(),
            'transit_altitude_degrees': trans_alt.degrees,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        dt = trans_time.to_datetime()
        click.echo(f"""
  M{number} — {obj.name} Transit
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Transit:    {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Transit JD: {trans_time.jd:.6f}
  Max Alt:    {trans_alt.degrees:.1f}°
""")
        if vctx:
            click.echo(vctx.format_steps())
