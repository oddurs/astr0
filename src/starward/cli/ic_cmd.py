"""
IC catalog CLI commands.
"""

from __future__ import annotations

import click
from typing import Optional

from starward.core.ic import (
    IC,
    ic_coords,
    ic_altitude,
    ic_airmass,
    ic_rise,
    ic_set,
    ic_transit,
    ic_transit_altitude,
)
from starward.core.ic_types import IC_OBJECT_TYPES, IC_TYPE_NAMES
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
    return IC_TYPE_NAMES.get(obj_type, obj_type.replace("_", " ").title())


# Valid object types for CLI filtering
_CLI_OBJECT_TYPES = [t for t in IC_OBJECT_TYPES if t not in ('nonexistent', 'duplicate', 'unknown')]


@click.group(name='ic')
def ic_group():
    """
    IC catalog browser.

    \b
    Browse and search the ~5,386 IC (Index Catalogue) objects -
    galaxies, nebulae, and star clusters supplementing the NGC.

    \b
    Examples:
        starward ic list                         # List all objects
        starward ic show 434                     # Show IC 434 details
        starward ic search horsehead             # Search by name
        starward ic list --type emission_nebula  # Filter by type
        starward ic stats                        # Show catalog statistics
    """
    pass


@ic_group.command(name='list')
@click.option('--type', 'obj_type', type=click.Choice(_CLI_OBJECT_TYPES, case_sensitive=False),
              help='Filter by object type')
@click.option('--constellation', type=str, help='Filter by constellation (3-letter abbr)')
@click.option('--magnitude', type=float, help='Show objects brighter than magnitude')
@click.option('--named', is_flag=True, help='Only show objects with common names')
@click.option('--limit', type=int, default=50, help='Maximum number of results (default: 50)')
@click.pass_context
def list_cmd(ctx, obj_type: Optional[str], constellation: Optional[str],
             magnitude: Optional[float], named: bool, limit: int):
    """List IC objects with optional filters."""
    output_fmt = ctx.obj.get('output', 'plain')

    # Build filter kwargs
    filter_kwargs = {}
    if obj_type:
        filter_kwargs['object_type'] = obj_type
    if constellation:
        filter_kwargs['constellation'] = constellation
    if magnitude is not None:
        filter_kwargs['max_magnitude'] = magnitude
    if named:
        filter_kwargs['has_name'] = True
    if limit:
        filter_kwargs['limit'] = limit

    if filter_kwargs:
        objects = IC.filter_observable(**filter_kwargs) if 'max_magnitude' in filter_kwargs else IC._db.filter_ic(**filter_kwargs)
        if not isinstance(objects[0] if objects else {}, dict):
            pass
        else:
            from starward.core.ic_types import ICObject
            objects = [ICObject.from_dict(d) for d in objects]
    else:
        objects = IC.list_all(limit=limit)

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
                    'ngc_number': o.ngc_number,
                }
                for o in objects
            ]
        }
        click.echo(json.dumps(data, indent=2))
    else:
        # Build header based on filters
        if obj_type:
            header = f"IC {_format_object_type(obj_type)}s"
        elif constellation:
            header = f"IC Objects in {constellation.upper()}"
        elif named:
            header = "Named IC Objects"
        else:
            header = "IC Catalog"

        if magnitude is not None:
            header += f" (mag ≤ {magnitude:.1f})"

        from starward.output.console import print_ic_table
        objects_data = [
            {
                'number': o.number,
                'name': o.name,
                'type': _format_object_type(o.object_type),
                'magnitude': o.magnitude,
                'constellation': o.constellation,
                'ngc': o.ngc_number,
            }
            for o in objects
        ]
        print_ic_table(header, objects_data)


@ic_group.command(name='show')
@click.argument('number', type=int)
@click.pass_context
def show_cmd(ctx, number: int):
    """Show detailed information about an IC object."""
    output_fmt = ctx.obj.get('output', 'plain')

    try:
        obj = IC.get(number)
    except KeyError:
        raise click.ClickException(f"IC {number} is not in the catalog")

    coords = ic_coords(number)

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
            'size_minor_arcmin': obj.size_minor_arcmin,
            'distance_kly': obj.distance_kly,
            'constellation': obj.constellation,
            'ngc_number': obj.ngc_number,
            'hubble_type': obj.hubble_type,
            'description': obj.description,
        }
        click.echo(json.dumps(data, indent=2))
    else:
        distance_str = f"{obj.distance_kly:,.0f} kly" if obj.distance_kly else None
        ngc_str = f"NGC {obj.ngc_number}" if obj.ngc_number else None

        from starward.output.console import print_ic_detail
        print_ic_detail(
            number=obj.number,
            name=obj.name,
            obj_type=_format_object_type(obj.object_type),
            ra=coords.ra.format_hms(),
            dec=coords.dec.format_dms(),
            magnitude=obj.magnitude,
            size=obj.size_arcmin,
            size_minor=obj.size_minor_arcmin,
            distance=distance_str,
            constellation=obj.constellation,
            ngc=ngc_str,
            hubble_type=obj.hubble_type,
            description=obj.description,
        )


@ic_group.command(name='search')
@click.argument('query')
@click.option('--limit', type=int, default=50, help='Maximum number of results')
@click.pass_context
def search_cmd(ctx, query: str, limit: int):
    """Search IC objects by name, type, or constellation."""
    output_fmt = ctx.obj.get('output', 'plain')

    results = IC.search(query, limit=limit)

    if not results:
        click.echo(f"No IC objects match '{query}'")
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
                    'ngc_number': o.ngc_number,
                }
                for o in results
            ]
        }
        click.echo(json.dumps(data, indent=2))
    else:
        from starward.output.console import print_ic_table
        objects_data = [
            {
                'number': o.number,
                'name': o.name,
                'type': _format_object_type(o.object_type),
                'magnitude': o.magnitude,
                'constellation': o.constellation,
                'ngc': o.ngc_number,
            }
            for o in results
        ]
        print_ic_table(f'Search Results for "{query}"', objects_data)


@ic_group.command(name='stats')
@click.pass_context
def stats_cmd(ctx):
    """Show IC catalog statistics."""
    output_fmt = ctx.obj.get('output', 'plain')

    stats = IC.stats()

    if output_fmt == 'json':
        import json
        click.echo(json.dumps(stats, indent=2))
    else:
        from starward.output.console import print_ic_stats
        print_ic_stats(stats)


@ic_group.command(name='altitude')
@click.argument('number', type=int)
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def altitude_cmd(ctx, number: int, lat: Optional[float], lon: Optional[float],
                 observer_name: Optional[str], jd: Optional[float]):
    """Calculate current altitude of an IC object."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    try:
        obj = IC.get(number)
    except KeyError:
        raise click.ClickException(f"IC {number} is not in the catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    alt = ic_altitude(number, observer, jd_val, vctx)
    air = ic_airmass(number, observer, jd_val)

    if output_fmt == 'json':
        import json
        data = {
            'object': f'IC {number}',
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
        name_str = f" — {obj.name}" if obj.name else ""
        click.echo(f"""
  IC {number}{name_str} Altitude
  {'─' * 45}
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Altitude:   {alt.degrees:+.2f}°
  Airmass:    {airmass_str}
  Status:     {visibility}
""")
        if vctx:
            click.echo(vctx.format_steps())


@ic_group.command(name='rise')
@click.argument('number', type=int)
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def rise_cmd(ctx, number: int, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Calculate rise time of an IC object."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    try:
        obj = IC.get(number)
    except KeyError:
        raise click.ClickException(f"IC {number} is not in the catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    rise_time = ic_rise(number, observer, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'object': f'IC {number}',
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
        name_str = f" — {obj.name}" if obj.name else ""
        if rise_time:
            dt = rise_time.to_datetime()
            click.echo(f"""
  IC {number}{name_str} Rise
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Rise Time:  {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Rise JD:    {rise_time.jd:.6f}
""")
        else:
            click.echo(f"""
  IC {number}{name_str} Rise
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  IC {number} does not rise from this location (circumpolar or never visible).
""")
        if vctx:
            click.echo(vctx.format_steps())


@ic_group.command(name='set')
@click.argument('number', type=int)
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def set_cmd(ctx, number: int, lat: Optional[float], lon: Optional[float],
            observer_name: Optional[str], jd: Optional[float]):
    """Calculate set time of an IC object."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    try:
        obj = IC.get(number)
    except KeyError:
        raise click.ClickException(f"IC {number} is not in the catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    set_time = ic_set(number, observer, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'object': f'IC {number}',
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
        name_str = f" — {obj.name}" if obj.name else ""
        if set_time:
            dt = set_time.to_datetime()
            click.echo(f"""
  IC {number}{name_str} Set
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Set Time:   {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Set JD:     {set_time.jd:.6f}
""")
        else:
            click.echo(f"""
  IC {number}{name_str} Set
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  IC {number} does not set from this location (circumpolar or never visible).
""")
        if vctx:
            click.echo(vctx.format_steps())


@ic_group.command(name='transit')
@click.argument('number', type=int)
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def transit_cmd(ctx, number: int, lat: Optional[float], lon: Optional[float],
                observer_name: Optional[str], jd: Optional[float]):
    """Calculate transit time of an IC object."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    try:
        obj = IC.get(number)
    except KeyError:
        raise click.ClickException(f"IC {number} is not in the catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    trans_time = ic_transit(number, observer, jd_val, vctx)
    trans_alt = ic_transit_altitude(number, observer)

    if output_fmt == 'json':
        import json
        data = {
            'object': f'IC {number}',
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
        name_str = f" — {obj.name}" if obj.name else ""
        click.echo(f"""
  IC {number}{name_str} Transit
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Transit:    {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Transit JD: {trans_time.jd:.6f}
  Max Alt:    {trans_alt.degrees:.1f}°
""")
        if vctx:
            click.echo(vctx.format_steps())
