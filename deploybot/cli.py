import click
from rich import print

from deploybot.stack import validate_stack, StackNotFoundError


@click.group()
def cli():
    pass


@cli.command()
@click.option('--stack', required=True, help='Name of the stack (e.g. nextjs-postgres)')
@click.option('--cloud', default='aws', help='Cloud provider (default: aws)')
@click.option('--region', default='eu-west-1', help='Region to deploy to')
def up(stack, cloud, region):
    try:
        stack_info = validate_stack(stack)
        print(f"[bold green]✅ Stack validated:[/bold green] {stack}")
        print(f"[blue]📁 Path:[/blue] {stack_info['path']}")
    except StackNotFoundError as e:
        print(f"[red]❌ {str(e)}[/red]")
    except FileNotFoundError as e:
        print(f"[red]❌ {str(e)}[/red]")


if __name__ == '__main__':
    cli()
