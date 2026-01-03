"""
Time-related CLI commands.
"""

import click
from datetime import datetime, timezone
from typing import Optional

from astr0.core.time import JulianDate, jd_now, jd_to_mjd
from astr0.verbose import VerboseContext
from astr0.output.formatters import Result, format_output


@click.group(name='time')
def time_group():
    """
    Time conversions and calculations.
    
    \b
    Julian Date, Modified JD, Sidereal Time, and more.
    
    \b
    Examples:
        astr0 time now                    # Current time in all formats
        astr0 time convert 2460000.5      # Convert JD to calendar
        astr0 time jd 2024 1 15 12 0 0    # Calendar to JD
        astr0 time lst -118.25            # Local Sidereal Time
    """
    pass


@time_group.command()
@click.pass_context
def now(ctx):
    """Show current time in all astronomical formats."""
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    jd = jd_now()
    dt = datetime.now(timezone.utc)
    
    if output_fmt == 'json':
        import json
        data = {
            'utc': dt.isoformat(),
            'julian_date': jd.jd,
            'modified_jd': jd.mjd,
            'j2000_centuries': jd.t_j2000,
            'gmst_hours': jd.gmst(verbose=vctx),
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        gmst = jd.gmst(verbose=vctx)
        gmst_h = int(gmst)
        gmst_m = int((gmst - gmst_h) * 60)
        gmst_s = ((gmst - gmst_h) * 60 - gmst_m) * 60
        gmst_str = f"{gmst_h:02d}h {gmst_m:02d}m {gmst_s:05.2f}s"
        
        click.echo(f"""
  ╭────────────────────────────────────────────╮
  │  Current Astronomical Time                 │
  ├────────────────────────────────────────────┤
  │  UTC:          {dt.strftime('%Y-%m-%d %H:%M:%S'):>26} │
  │  Julian Date:  {jd.jd:>26.6f} │
  │  Modified JD:  {jd.mjd:>26.6f} │
  │  T (J2000):    {jd.t_j2000:>26.10f} │
  │  GMST:         {gmst_str:>26} │
  ╰────────────────────────────────────────────╯
""")
        if vctx:
            click.echo(vctx.format_steps())


@time_group.command()
@click.argument('value', type=float)
@click.option('--from', 'from_fmt', type=click.Choice(['jd', 'mjd']), default='jd',
              help='Input format (default: jd)')
@click.pass_context
def convert(ctx, value: float, from_fmt: str):
    """
    Convert a Julian Date or MJD to calendar date.
    
    \b
    Examples:
        astr0 time convert 2460000.5
        astr0 time convert 60000 --from mjd
    """
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    if from_fmt == 'mjd':
        jd = JulianDate.from_mjd(value)
    else:
        jd = JulianDate(value)
    
    dt = jd.to_datetime(verbose=vctx)
    
    if output_fmt == 'json':
        import json
        data = {
            'input': value,
            'input_format': from_fmt,
            'utc': dt.isoformat(),
            'julian_date': jd.jd,
            'modified_jd': jd.mjd,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  Input ({from_fmt.upper()}): {value}
  ─────────────────────────────────
  UTC:          {dt.strftime('%Y-%m-%d %H:%M:%S.%f')}
  Julian Date:  {jd.jd:.10f}
  Modified JD:  {jd.mjd:.10f}
""")
        if vctx:
            click.echo(vctx.format_steps())


@time_group.command()
@click.argument('year', type=int)
@click.argument('month', type=int)
@click.argument('day', type=int)
@click.argument('hour', type=int, default=0)
@click.argument('minute', type=int, default=0)
@click.argument('second', type=float, default=0.0)
@click.pass_context
def jd(ctx, year: int, month: int, day: int, hour: int, minute: int, second: float):
    """
    Convert calendar date (UTC) to Julian Date.
    
    \b
    Examples:
        astr0 time jd 2024 1 15
        astr0 time jd 2024 6 21 12 0 0
    """
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    result = JulianDate.from_calendar(year, month, day, hour, minute, second, verbose=vctx)
    
    if output_fmt == 'json':
        import json
        data = {
            'input': {
                'year': year, 'month': month, 'day': day,
                'hour': hour, 'minute': minute, 'second': second
            },
            'julian_date': result.jd,
            'modified_jd': result.mjd,
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  Input:        {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:06.3f} UTC
  ─────────────────────────────────────────────
  Julian Date:  {result.jd:.10f}
  Modified JD:  {result.mjd:.10f}
  T (J2000):    {result.t_j2000:.12f} centuries
""")
        if vctx:
            click.echo(vctx.format_steps())


@time_group.command()
@click.argument('longitude', type=float)
@click.option('--jd', 'jd_value', type=float, default=None, help='Julian Date (default: now)')
@click.pass_context
def lst(ctx, longitude: float, jd_value: Optional[float]):
    """
    Calculate Local Sidereal Time.
    
    Longitude is in degrees, positive East.
    
    \b
    Examples:
        astr0 time lst -118.25                    # Los Angeles, now
        astr0 time lst 0 --jd 2460000.5           # Greenwich
    """
    verbose = ctx.obj.get('verbose', False)
    output_fmt = ctx.obj.get('output', 'plain')
    
    vctx = VerboseContext() if verbose else None
    
    if jd_value is None:
        jd = jd_now()
    else:
        jd = JulianDate(jd_value)
    
    lst_hours = jd.lst(longitude, verbose=vctx)
    lst_h = int(lst_hours)
    lst_m = int((lst_hours - lst_h) * 60)
    lst_s = ((lst_hours - lst_h) * 60 - lst_m) * 60
    
    gmst_hours = jd.gmst()
    gmst_h = int(gmst_hours)
    gmst_m = int((gmst_hours - gmst_h) * 60)
    gmst_s = ((gmst_hours - gmst_h) * 60 - gmst_m) * 60
    
    if output_fmt == 'json':
        import json
        data = {
            'longitude_deg': longitude,
            'julian_date': jd.jd,
            'gmst_hours': gmst_hours,
            'lst_hours': lst_hours,
            'lst_formatted': f"{lst_h:02d}:{lst_m:02d}:{lst_s:05.2f}",
        }
        if vctx:
            data['steps'] = vctx.to_dict()
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"""
  Longitude:    {longitude:+.4f}° ({'E' if longitude >= 0 else 'W'})
  Julian Date:  {jd.jd:.6f}
  ─────────────────────────────────────────────
  GMST:         {gmst_h:02d}h {gmst_m:02d}m {gmst_s:05.2f}s
  LST:          {lst_h:02d}h {lst_m:02d}m {lst_s:05.2f}s
""")
        if vctx:
            click.echo(vctx.format_steps())
