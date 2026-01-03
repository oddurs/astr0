"""
Command Line Interface for astr0.

Per aspera ad astra — Through hardships to the stars
"""

import click
from typing import Optional

from astr0 import __version__
from astr0.cli.time_cmd import time_group
from astr0.cli.coords_cmd import coords_group
from astr0.cli.angles_cmd import angles_group
from astr0.cli.constants_cmd import constants_group
from astr0.cli.sun_cmd import sun_group
from astr0.cli.observer_cmd import observer_group
from astr0.cli.moon_cmd import moon_group
from astr0.cli.vis_cmd import vis_group


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
        }
        
        if cmd_name in aliases:
            return click.Group.get_command(self, ctx, aliases[cmd_name])
        
        return None


@click.group(cls=AliasedGroup)
@click.option('--verbose', '-v', is_flag=True, help='Show calculation steps')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.option('--output', '-o', type=click.Choice(['plain', 'json', 'latex']), default='plain', help='Output format')
@click.version_option(__version__, prog_name='astr0')
@click.pass_context
def main(ctx, verbose: bool, json_output: bool, output: str):
    """
    astr0 — Astronomy Calculation Toolkit
    
    \b
    ✦ Per aspera ad astra ✦
    
    A professional toolkit for astronomical calculations.
    Use --verbose to see the math behind each calculation.
    
    \b
    Examples:
        astr0 time now
        astr0 time now --json
        astr0 coords transform "12h30m +45d" --to galactic
        astr0 angles sep "10h +30d" "11h +31d"
    
    \b
    Aliases:
        time → t | coords → c | angles → a | constants → const
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    # --json flag overrides --output
    ctx.obj['output'] = 'json' if json_output else output


# Register command groups
main.add_command(time_group)
main.add_command(coords_group)
main.add_command(angles_group)
main.add_command(constants_group)
main.add_command(sun_group)
main.add_command(observer_group)
main.add_command(moon_group)
main.add_command(vis_group)


@main.command()
def about():
    """Show information about astr0."""
    click.echo(f"""
    ╭───────────────────────────────────────╮
    │                                       │
    │       __ _ ___| |_ _ __ ___           │
    │      / _` / __| __| '__/ _ \\          │
    │     | (_| \\__ \\ |_| | | (_) |         │
    │      \\__,_|___/\\__|_|  \\___/          │
    │                                       │
    │     Astronomy Calculation Toolkit     │
    │     ─────────────────────────────     │
    │                                       │
    │     Version: {__version__:<25}│
    │     License: MIT                      │
    │                                       │
    │     "Per aspera ad astra"             │
    │     Through hardships to the stars    │
    │                                       │
    ╰───────────────────────────────────────╯
    """)


if __name__ == '__main__':
    main()
