import click
from rich import print


@click.group()
def cli():
    pass


@cli.command()
@click.option('--stack', required=True, help='Name of the stack (e.g. nextjs-postgres)')
@click.option('--cloud', default='aws', help='Cloud provider (default: aws)')
@click.option('--region', default='eu-west-1', help='Region to deploy to')
def up(stack, cloud, region):
    print(f"[bold green]🚀 Deploying stack:[/bold green] {stack}")
    print(f"[cyan]→ Cloud:[/cyan] {cloud}")
    print(f"[cyan]→ Region:[/cyan] {region}")
    # TODO: call provisioning + deploy


if __name__ == '__main__':
    cli()
