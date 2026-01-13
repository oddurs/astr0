"""
Hipparcos star catalog CLI commands.
"""

from __future__ import annotations

import click
from typing import Optional

from starward.core.hipparcos import (
    Hipparcos,
    star_coords,
    star_altitude,
    star_airmass,
    star_rise,
    star_set,
    star_transit,
    star_transit_altitude,
)
from starward.core.hipparcos_types import SPECTRAL_CLASSES
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


@click.group(name='stars')
def stars_group():
    """
    Hipparcos bright star catalog.

    \b
    Browse and search the Hipparcos catalog of bright stars with
    precise positions, proper motions, and photometric data.

    \b
    Examples:
        starward stars list                      # List brightest stars
        starward stars show 32349                # Show Sirius details
        starward stars search vega               # Search by name
        starward stars list --constellation Ori  # Orion stars
        starward stars stats                     # Show catalog statistics
    """
    pass


@stars_group.command(name='list')
@click.option('--constellation', type=str, help='Filter by constellation (3-letter abbr)')
@click.option('--magnitude', type=float, help='Show stars brighter than magnitude')
@click.option('--spectral', type=click.Choice(SPECTRAL_CLASSES, case_sensitive=False),
              help='Filter by spectral class (O, B, A, F, G, K, M)')
@click.option('--named', is_flag=True, help='Only show stars with common names')
@click.option('--limit', type=int, default=50, help='Maximum number of results (default: 50)')
@click.option('--order', type=click.Choice(['magnitude', 'hip_number', 'name', 'distance_ly']),
              default='magnitude', help='Sort order (default: magnitude)')
@click.pass_context
def list_cmd(ctx, constellation: Optional[str], magnitude: Optional[float],
             spectral: Optional[str], named: bool, limit: int, order: str):
    """List Hipparcos stars with optional filters."""
    output_fmt = ctx.obj.get('output', 'plain')

    # Build filter kwargs
    filter_kwargs = {}
    if constellation:
        filter_kwargs['constellation'] = constellation
    if magnitude is not None:
        filter_kwargs['max_magnitude'] = magnitude
    if spectral:
        filter_kwargs['spectral_class'] = spectral
    if named:
        filter_kwargs['has_name'] = True
    if limit:
        filter_kwargs['limit'] = limit

    if filter_kwargs:
        from starward.core.hipparcos_types import HIPStar
        stars_data = Hipparcos._db.filter_hipparcos(**filter_kwargs)
        stars = [HIPStar.from_dict(d) for d in stars_data]
    else:
        stars = Hipparcos.list_all(limit=limit, order_by=order)

    if not stars:
        click.echo("No stars match the specified filters.")
        return

    if output_fmt == 'json':
        import json
        data = {
            'count': len(stars),
            'stars': [
                {
                    'hip_number': s.hip_number,
                    'name': s.name,
                    'bayer': s.bayer,
                    'ra_hours': s.ra_hours,
                    'dec_degrees': s.dec_degrees,
                    'magnitude': s.magnitude,
                    'spectral_type': s.spectral_type,
                    'distance_ly': s.distance_ly,
                    'constellation': s.constellation,
                }
                for s in stars
            ]
        }
        click.echo(json.dumps(data, indent=2))
    else:
        # Build header based on filters
        if constellation:
            header = f"Stars in {constellation.upper()}"
        elif spectral:
            header = f"Spectral Class {spectral} Stars"
        elif named:
            header = "Named Stars"
        else:
            header = "Hipparcos Bright Stars"

        if magnitude is not None:
            header += f" (mag <= {magnitude:.1f})"

        from starward.output.console import print_stars_table
        stars_data = [
            {
                'hip': s.hip_number,
                'name': s.name or s.bayer or f"HIP {s.hip_number}",
                'magnitude': s.magnitude,
                'spectral': s.spectral_type,
                'constellation': s.constellation,
                'distance': s.distance_ly,
            }
            for s in stars
        ]
        print_stars_table(header, stars_data)


@stars_group.command(name='show')
@click.argument('identifier')
@click.pass_context
def show_cmd(ctx, identifier: str):
    """
    Show detailed information about a star.

    IDENTIFIER can be a HIP number (e.g., 32349) or a star name (e.g., Sirius).
    """
    output_fmt = ctx.obj.get('output', 'plain')

    # Try to parse as HIP number first
    try:
        hip_number = int(identifier)
        star = Hipparcos.get(hip_number)
    except ValueError:
        # Try by name
        star = Hipparcos.get_by_name(identifier)
        if star is None:
            # Try by Bayer designation
            star = Hipparcos.get_by_bayer(identifier)
        if star is None:
            raise click.ClickException(f"Star '{identifier}' not found in catalog")
    except KeyError:
        raise click.ClickException(f"HIP {identifier} is not in the catalog")

    coords = star_coords(star.hip_number)

    if output_fmt == 'json':
        import json
        data = {
            'hip_number': star.hip_number,
            'name': star.name,
            'bayer': star.bayer,
            'flamsteed': star.flamsteed,
            'ra_hours': star.ra_hours,
            'dec_degrees': star.dec_degrees,
            'ra_formatted': coords.ra.format_hms(),
            'dec_formatted': coords.dec.format_dms(),
            'magnitude': star.magnitude,
            'bv_color': star.bv_color,
            'spectral_type': star.spectral_type,
            'parallax': star.parallax,
            'distance_ly': star.distance_ly,
            'proper_motion_ra': star.proper_motion_ra,
            'proper_motion_dec': star.proper_motion_dec,
            'radial_velocity': star.radial_velocity,
            'constellation': star.constellation,
        }
        click.echo(json.dumps(data, indent=2))
    else:
        from starward.output.console import print_star_detail
        print_star_detail(
            hip_number=star.hip_number,
            name=star.name,
            bayer=star.bayer,
            flamsteed=star.flamsteed,
            ra=coords.ra.format_hms(),
            dec=coords.dec.format_dms(),
            magnitude=star.magnitude,
            bv_color=star.bv_color,
            spectral_type=star.spectral_type,
            parallax=star.parallax,
            distance_ly=star.distance_ly,
            proper_motion_ra=star.proper_motion_ra,
            proper_motion_dec=star.proper_motion_dec,
            radial_velocity=star.radial_velocity,
            constellation=star.constellation,
        )


@stars_group.command(name='search')
@click.argument('query')
@click.option('--limit', type=int, default=50, help='Maximum number of results')
@click.pass_context
def search_cmd(ctx, query: str, limit: int):
    """Search stars by name, Bayer designation, spectral type, or constellation."""
    output_fmt = ctx.obj.get('output', 'plain')

    results = Hipparcos.search(query, limit=limit)

    if not results:
        click.echo(f"No stars match '{query}'")
        return

    if output_fmt == 'json':
        import json
        data = {
            'query': query,
            'count': len(results),
            'stars': [
                {
                    'hip_number': s.hip_number,
                    'name': s.name,
                    'bayer': s.bayer,
                    'magnitude': s.magnitude,
                    'spectral_type': s.spectral_type,
                    'constellation': s.constellation,
                }
                for s in results
            ]
        }
        click.echo(json.dumps(data, indent=2))
    else:
        from starward.output.console import print_stars_table
        stars_data = [
            {
                'hip': s.hip_number,
                'name': s.name or s.bayer or f"HIP {s.hip_number}",
                'magnitude': s.magnitude,
                'spectral': s.spectral_type,
                'constellation': s.constellation,
                'distance': s.distance_ly,
            }
            for s in results
        ]
        print_stars_table(f'Search Results for "{query}"', stars_data)


@stars_group.command(name='stats')
@click.pass_context
def stats_cmd(ctx):
    """Show Hipparcos catalog statistics."""
    output_fmt = ctx.obj.get('output', 'plain')

    stats = Hipparcos.stats()

    if output_fmt == 'json':
        import json
        click.echo(json.dumps(stats, indent=2))
    else:
        from starward.output.console import print_stars_stats
        print_stars_stats(stats)


@stars_group.command(name='altitude')
@click.argument('identifier')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: now)')
@click.pass_context
def altitude_cmd(ctx, identifier: str, lat: Optional[float], lon: Optional[float],
                 observer_name: Optional[str], jd: Optional[float]):
    """Calculate current altitude of a star."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    # Parse identifier
    try:
        hip_number = int(identifier)
        star = Hipparcos.get(hip_number)
    except ValueError:
        star = Hipparcos.get_by_name(identifier)
        if star is None:
            star = Hipparcos.get_by_bayer(identifier)
        if star is None:
            raise click.ClickException(f"Star '{identifier}' not found in catalog")
        hip_number = star.hip_number
    except KeyError:
        raise click.ClickException(f"HIP {identifier} is not in the catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    alt = star_altitude(hip_number, observer, jd_val, vctx)
    air = star_airmass(hip_number, observer, jd_val)

    if output_fmt == 'json':
        import json
        data = {
            'star': f'HIP {hip_number}',
            'name': star.name,
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
        name_str = f" ({star.name})" if star.name else ""
        click.echo(f"""
  HIP {hip_number}{name_str} Altitude
  {'─' * 45}
  Time:       {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Altitude:   {alt.degrees:+.2f}°
  Airmass:    {airmass_str}
  Status:     {visibility}
""")
        if vctx:
            click.echo(vctx.format_steps())


@stars_group.command(name='rise')
@click.argument('identifier')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def rise_cmd(ctx, identifier: str, lat: Optional[float], lon: Optional[float],
             observer_name: Optional[str], jd: Optional[float]):
    """Calculate rise time of a star."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    # Parse identifier
    try:
        hip_number = int(identifier)
        star = Hipparcos.get(hip_number)
    except ValueError:
        star = Hipparcos.get_by_name(identifier)
        if star is None:
            star = Hipparcos.get_by_bayer(identifier)
        if star is None:
            raise click.ClickException(f"Star '{identifier}' not found in catalog")
        hip_number = star.hip_number
    except KeyError:
        raise click.ClickException(f"HIP {identifier} is not in the catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    rise_time = star_rise(hip_number, observer, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'star': f'HIP {hip_number}',
            'name': star.name,
            'observer': observer.name,
            'date_jd': jd_val.jd,
            'rise_jd': rise_time.jd if rise_time else None,
            'rise_utc': rise_time.to_datetime().isoformat() if rise_time else None,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        name_str = f" ({star.name})" if star.name else ""
        if rise_time:
            dt = rise_time.to_datetime()
            click.echo(f"""
  HIP {hip_number}{name_str} Rise
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Rise Time:  {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Rise JD:    {rise_time.jd:.6f}
""")
        else:
            click.echo(f"""
  HIP {hip_number}{name_str} Rise
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  This star does not rise from this location (circumpolar or never visible).
""")
        if vctx:
            click.echo(vctx.format_steps())


@stars_group.command(name='set')
@click.argument('identifier')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def set_cmd(ctx, identifier: str, lat: Optional[float], lon: Optional[float],
            observer_name: Optional[str], jd: Optional[float]):
    """Calculate set time of a star."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    # Parse identifier
    try:
        hip_number = int(identifier)
        star = Hipparcos.get(hip_number)
    except ValueError:
        star = Hipparcos.get_by_name(identifier)
        if star is None:
            star = Hipparcos.get_by_bayer(identifier)
        if star is None:
            raise click.ClickException(f"Star '{identifier}' not found in catalog")
        hip_number = star.hip_number
    except KeyError:
        raise click.ClickException(f"HIP {identifier} is not in the catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    set_time = star_set(hip_number, observer, jd_val, vctx)

    if output_fmt == 'json':
        import json
        data = {
            'star': f'HIP {hip_number}',
            'name': star.name,
            'observer': observer.name,
            'date_jd': jd_val.jd,
            'set_jd': set_time.jd if set_time else None,
            'set_utc': set_time.to_datetime().isoformat() if set_time else None,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        name_str = f" ({star.name})" if star.name else ""
        if set_time:
            dt = set_time.to_datetime()
            click.echo(f"""
  HIP {hip_number}{name_str} Set
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Set Time:   {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Set JD:     {set_time.jd:.6f}
""")
        else:
            click.echo(f"""
  HIP {hip_number}{name_str} Set
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  This star does not set from this location (circumpolar or never visible).
""")
        if vctx:
            click.echo(vctx.format_steps())


@stars_group.command(name='transit')
@click.argument('identifier')
@click.option('--lat', type=float, help='Observer latitude (degrees)')
@click.option('--lon', type=float, help='Observer longitude (degrees)')
@click.option('--observer', 'observer_name', type=str, help='Named observer profile')
@click.option('--jd', type=float, help='Julian Date (default: today)')
@click.pass_context
def transit_cmd(ctx, identifier: str, lat: Optional[float], lon: Optional[float],
                observer_name: Optional[str], jd: Optional[float]):
    """Calculate transit time of a star."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')

    vctx = VerboseContext() if verbose else None

    # Parse identifier
    try:
        hip_number = int(identifier)
        star = Hipparcos.get(hip_number)
    except ValueError:
        star = Hipparcos.get_by_name(identifier)
        if star is None:
            star = Hipparcos.get_by_bayer(identifier)
        if star is None:
            raise click.ClickException(f"Star '{identifier}' not found in catalog")
        hip_number = star.hip_number
    except KeyError:
        raise click.ClickException(f"HIP {identifier} is not in the catalog")

    observer = _get_observer_from_options(lat, lon, observer_name)
    jd_val = JulianDate(jd) if jd else jd_now()

    trans_time = star_transit(hip_number, observer, jd_val, vctx)
    trans_alt = star_transit_altitude(hip_number, observer)

    if output_fmt == 'json':
        import json
        data = {
            'star': f'HIP {hip_number}',
            'name': star.name,
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
        name_str = f" ({star.name})" if star.name else ""
        click.echo(f"""
  HIP {hip_number}{name_str} Transit
  {'─' * 45}
  Observer:   {observer.name} ({observer.lat_deg:.2f}°, {observer.lon_deg:.2f}°)

  Transit:    {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC
  Transit JD: {trans_time.jd:.6f}
  Max Alt:    {trans_alt.degrees:.1f}°
""")
        if vctx:
            click.echo(vctx.format_steps())
