"""
Command Line Interface for starward.

Per aspera ad astra — Through hardships to the stars
"""

import click
from typing import Optional

from starward import __version__
from starward.cli.time_cmd import time_group
from starward.cli.coords_cmd import coords_group
from starward.cli.angles_cmd import angles_group
from starward.cli.constants_cmd import constants_group
from starward.cli.sun_cmd import sun_group
from starward.cli.observer_cmd import observer_group
from starward.cli.moon_cmd import moon_group
from starward.cli.vis_cmd import vis_group
from starward.cli.planets_cmd import planets_group
from starward.cli.messier_cmd import messier_group
from starward.core.precision import set_precision, PrecisionLevel


class AliasedGroup(click.Group):
    """Click group with command aliases."""
    
    def get_command(self, ctx, cmd_name):
        # Try exact match first
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        
        # Try aliases
        aliases = {
            't': 'time',
            'c': 'coords',
            'coord': 'coords',
            'a': 'angles',
            'angle': 'angles',
            'const': 'constants',
            's': 'sun',
            'o': 'observer',
            'obs': 'observer',
            'm': 'moon',
            'v': 'vis',
            'visibility': 'vis',
            'p': 'planets',
            'planet': 'planets',
            'mes': 'messier',
        }
        
        if cmd_name in aliases:
            return click.Group.get_command(self, ctx, aliases[cmd_name])
        
        return None


@click.group(cls=AliasedGroup)
@click.option('--verbose', '-v', is_flag=True, help='Show calculation steps')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.option('--output', '-o', type=click.Choice(['plain', 'json', 'rich', 'latex']), default='plain', help='Output format')
@click.option('--precision', '-p', 
              type=click.Choice(['compact', 'display', 'standard', 'high', 'full']),
              default='standard',
              help='Output precision level (default: standard)')
@click.version_option(__version__, prog_name='starward')
@click.pass_context
def main(ctx, verbose: bool, json_output: bool, output: str, precision: str):
    """
    starward — Astronomy Calculation Toolkit

    \b
    ✦ Per aspera ad astra ✦

    A professional toolkit for astronomical calculations.
    Use --verbose to see the math behind each calculation.

    \b
    Examples:
        starward time now
        starward time now --json
        starward coords transform "12h30m +45d" --to galactic
        starward angles sep "10h +30d" "11h +31d"
    
    \b
    Aliases:
        time → t | coords → c | angles → a | constants → const
    
    \b
    Precision Levels:
        compact  (2)  - Quick reference
        display  (4)  - Readable output  
        standard (6)  - Default precision
        high    (10)  - Research applications
        full    (15)  - Maximum precision
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    # --json flag overrides --output
    ctx.obj['output'] = 'json' if json_output else output
    ctx.obj['precision'] = precision
    
    # Set global precision
    set_precision(precision)


# Register command groups
main.add_command(time_group)
main.add_command(coords_group)
main.add_command(angles_group)
main.add_command(constants_group)
main.add_command(sun_group)
main.add_command(observer_group)
main.add_command(moon_group)
main.add_command(vis_group)
main.add_command(planets_group)
main.add_command(messier_group)


@main.command()
def about():
    """Show information about starward."""
    from starward.output.console import print_about_banner
    print_about_banner(__version__)


if __name__ == '__main__':
    main()
