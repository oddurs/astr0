"""
CLI commands for observation list management.
"""

from __future__ import annotations

import click
from typing import Optional

from starward.core.lists import Lists, ListManager


@click.group(name='list')
def list_group():
    """
    Manage observation lists.

    \b
    Create custom lists of astronomical objects for observation planning.
    Objects can be added from any catalog (Messier, NGC, IC, Caldwell, Hipparcos).

    \b
    Examples:
        starward list create "Tonight"
        starward list add "Tonight" M31
        starward list add "Tonight" NGC7000 --notes "Check visibility"
        starward list show "Tonight"
    """
    pass


@list_group.command(name='ls')
@click.pass_context
def list_all(ctx):
    """List all observation lists."""
    from starward.output.console import print_lists_table

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'
    lists = Lists.list_all()

    if output_format == 'json':
        import json
        data = [
            {
                'name': lst.name,
                'description': lst.description,
                'item_count': len(lst),
                'created_at': lst.created_at.isoformat(),
                'updated_at': lst.updated_at.isoformat()
            }
            for lst in lists
        ]
        click.echo(json.dumps(data, indent=2))
    else:
        print_lists_table(lists)


@list_group.command(name='create')
@click.argument('name')
@click.option('--description', '-d', help='List description')
@click.pass_context
def create_list(ctx, name: str, description: Optional[str]):
    """
    Create a new observation list.

    \b
    Examples:
        starward list create "Tonight"
        starward list create "Summer Galaxies" -d "Best galaxies for summer viewing"
    """
    from starward.output.console import print_success, print_error

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'

    try:
        obs_list = Lists.create(name, description)

        if output_format == 'json':
            import json
            click.echo(json.dumps({
                'success': True,
                'name': obs_list.name,
                'description': obs_list.description
            }, indent=2))
        else:
            print_success(f"Created list '{name}'")
    except ValueError as e:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': False, 'error': str(e)}, indent=2))
        else:
            print_error(str(e))


@list_group.command(name='delete')
@click.argument('name')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def delete_list(ctx, name: str, yes: bool):
    """
    Delete an observation list.

    \b
    Examples:
        starward list delete "Tonight"
        starward list delete "Old List" --yes
    """
    from starward.output.console import print_success, print_error

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'

    # Check if list exists
    obs_list = Lists.get(name)
    if not obs_list:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': False, 'error': f"List '{name}' not found"}, indent=2))
        else:
            print_error(f"List '{name}' not found")
        return

    # Confirm deletion
    if not yes:
        item_count = len(obs_list)
        msg = f"Delete list '{name}'"
        if item_count > 0:
            msg += f" with {item_count} items"
        msg += "?"

        if not click.confirm(msg):
            return

    if Lists.delete(name):
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': True, 'deleted': name}, indent=2))
        else:
            print_success(f"Deleted list '{name}'")
    else:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': False, 'error': 'Delete failed'}, indent=2))
        else:
            print_error("Delete failed")


@list_group.command(name='show')
@click.argument('name')
@click.pass_context
def show_list(ctx, name: str):
    """
    Show items in an observation list.

    \b
    Examples:
        starward list show "Tonight"
    """
    from starward.output.console import print_list_detail, print_error

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'

    obs_list = Lists.get(name)
    if not obs_list:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'error': f"List '{name}' not found"}, indent=2))
        else:
            print_error(f"List '{name}' not found")
        return

    if output_format == 'json':
        import json
        data = {
            'name': obs_list.name,
            'description': obs_list.description,
            'item_count': len(obs_list),
            'created_at': obs_list.created_at.isoformat(),
            'updated_at': obs_list.updated_at.isoformat(),
            'items': [
                {
                    'designation': item.designation,
                    'catalog': item.catalog,
                    'display_name': item.display_name,
                    'notes': item.notes,
                    'added_at': item.added_at.isoformat()
                }
                for item in obs_list.items
            ]
        }
        click.echo(json.dumps(data, indent=2))
    else:
        print_list_detail(obs_list)


@list_group.command(name='add')
@click.argument('name')
@click.argument('object')
@click.option('--notes', '-n', help='Notes about this object')
@click.pass_context
def add_item(ctx, name: str, object: str, notes: Optional[str]):
    """
    Add an object to a list.

    \b
    OBJECT can be any catalog designation:
        M31, M 31           - Messier objects
        NGC7000, NGC 7000   - NGC objects
        IC434, IC 434       - IC objects
        C1, Caldwell 1      - Caldwell objects
        HIP32349            - Hipparcos stars

    \b
    Examples:
        starward list add "Tonight" M31
        starward list add "Tonight" NGC7000 --notes "Best after midnight"
    """
    from starward.output.console import print_success, print_error

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'

    try:
        item = Lists.add_item(name, object, notes)

        if output_format == 'json':
            import json
            click.echo(json.dumps({
                'success': True,
                'designation': item.designation,
                'display_name': item.display_name,
                'catalog': item.catalog
            }, indent=2))
        else:
            display = f"{item.designation}"
            if item.display_name:
                display += f" ({item.display_name})"
            print_success(f"Added {display} to '{name}'")
    except ValueError as e:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': False, 'error': str(e)}, indent=2))
        else:
            print_error(str(e))


@list_group.command(name='remove')
@click.argument('name')
@click.argument('object')
@click.pass_context
def remove_item(ctx, name: str, object: str):
    """
    Remove an object from a list.

    \b
    Examples:
        starward list remove "Tonight" M31
        starward list remove "Tonight" NGC7000
    """
    from starward.output.console import print_success, print_error

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'

    if Lists.remove_item(name, object):
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': True, 'removed': object}, indent=2))
        else:
            print_success(f"Removed {object} from '{name}'")
    else:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': False, 'error': f"Object '{object}' not found in list '{name}'"}, indent=2))
        else:
            print_error(f"Object '{object}' not found in list '{name}'")


@list_group.command(name='clear')
@click.argument('name')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
@click.pass_context
def clear_list(ctx, name: str, yes: bool):
    """
    Remove all items from a list.

    \b
    Examples:
        starward list clear "Tonight"
        starward list clear "Tonight" --yes
    """
    from starward.output.console import print_success, print_error

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'

    # Check if list exists
    obs_list = Lists.get(name)
    if not obs_list:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': False, 'error': f"List '{name}' not found"}, indent=2))
        else:
            print_error(f"List '{name}' not found")
        return

    # Confirm
    if not yes and len(obs_list) > 0:
        if not click.confirm(f"Remove all {len(obs_list)} items from '{name}'?"):
            return

    count = Lists.clear(name)

    if output_format == 'json':
        import json
        click.echo(json.dumps({'success': True, 'removed_count': count}, indent=2))
    else:
        print_success(f"Removed {count} items from '{name}'")


@list_group.command(name='rename')
@click.argument('old_name')
@click.argument('new_name')
@click.pass_context
def rename_list(ctx, old_name: str, new_name: str):
    """
    Rename an observation list.

    \b
    Examples:
        starward list rename "Tonight" "Saturday Night"
    """
    from starward.output.console import print_success, print_error

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'

    try:
        if Lists.rename(old_name, new_name):
            if output_format == 'json':
                import json
                click.echo(json.dumps({
                    'success': True,
                    'old_name': old_name,
                    'new_name': new_name
                }, indent=2))
            else:
                print_success(f"Renamed '{old_name}' to '{new_name}'")
        else:
            if output_format == 'json':
                import json
                click.echo(json.dumps({'success': False, 'error': f"List '{old_name}' not found"}, indent=2))
            else:
                print_error(f"List '{old_name}' not found")
    except ValueError as e:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': False, 'error': str(e)}, indent=2))
        else:
            print_error(str(e))


@list_group.command(name='note')
@click.argument('name')
@click.argument('object')
@click.argument('notes', required=False)
@click.option('--clear', '-c', is_flag=True, help='Clear notes')
@click.pass_context
def update_notes(ctx, name: str, object: str, notes: Optional[str], clear: bool):
    """
    Update notes for an object in a list.

    \b
    Examples:
        starward list note "Tonight" M31 "Best target, high priority"
        starward list note "Tonight" M31 --clear
    """
    from starward.output.console import print_success, print_error

    output_format = ctx.obj.get('output', 'plain') if ctx.obj else 'plain'

    if clear:
        notes = None
    elif notes is None:
        print_error("Provide notes text or use --clear to remove notes")
        return

    if Lists.update_item_notes(name, object, notes):
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': True, 'notes': notes}, indent=2))
        else:
            if notes:
                print_success(f"Updated notes for {object}")
            else:
                print_success(f"Cleared notes for {object}")
    else:
        if output_format == 'json':
            import json
            click.echo(json.dumps({'success': False, 'error': 'Object not found'}, indent=2))
        else:
            print_error(f"Object '{object}' not found in list '{name}'")


@list_group.command(name='export')
@click.argument('name')
@click.option('--format', '-f', 'fmt', type=click.Choice(['csv', 'json']), default='csv', help='Export format')
@click.option('--output', '-o', 'output_file', type=click.Path(), help='Output file (default: stdout)')
@click.pass_context
def export_list(ctx, name: str, fmt: str, output_file: Optional[str]):
    """
    Export a list to CSV or JSON.

    \b
    Examples:
        starward list export "Tonight"
        starward list export "Tonight" --format json
        starward list export "Tonight" -o tonight.csv
    """
    from starward.output.console import print_error

    obs_list = Lists.get(name)
    if not obs_list:
        print_error(f"List '{name}' not found")
        return

    if fmt == 'csv':
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Designation', 'Catalog', 'Name', 'Notes', 'Added'])

        for item in obs_list.items:
            writer.writerow([
                item.designation,
                item.catalog,
                item.display_name or '',
                item.notes or '',
                item.added_at.strftime('%Y-%m-%d %H:%M')
            ])

        content = output.getvalue()
    else:  # json
        import json
        data = {
            'name': obs_list.name,
            'description': obs_list.description,
            'exported_at': datetime.now().isoformat(),
            'items': [
                {
                    'designation': item.designation,
                    'catalog': item.catalog,
                    'name': item.display_name,
                    'notes': item.notes,
                    'added_at': item.added_at.isoformat()
                }
                for item in obs_list.items
            ]
        }
        content = json.dumps(data, indent=2)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(content)
        click.echo(f"Exported to {output_file}")
    else:
        click.echo(content)


# Need datetime for export
from datetime import datetime
