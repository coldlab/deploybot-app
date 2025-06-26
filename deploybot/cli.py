import click
import time
from pathlib import Path
from deploybot.core.enums import Target
from deploybot.core.stack import get_stack
from deploybot.core.parameters import DeployParameters
from deploybot.targets.factory import TargetFactory
from deploybot.ui.console import ConsoleUI


ui = ConsoleUI()

@click.group()
def cli():
    """DeployBot - Infrastructure Deployment Tool"""
    pass

@cli.command()
@click.option('--stack', required=True, help='Name of the stack (e.g. gcp-web)')
@click.option('--target', help='Deployment target (gcp, aws). Defaults to stack\'s default target if not provided.')
@click.option('--project-id', help='GCP Project ID (required for GCP target)')
@click.option('--region', help='Region to deploy to (overrides stack config)')
def deploy(stack: str, target: str, project_id: str, region: str):
    """Deploy a stack to the specified target."""
    start_time = time.time()
    ui.print_header()

    try:
        # Create parameters model
        params = DeployParameters(
            stack=stack,
            target=Target(target) if target else None,
            project_id=project_id,
            region=region
        )
        
        # Load stack configuration
        stack_obj = get_stack(params.stack)
        
        # Determine target
        actual_target = params.target or stack_obj.default_target
        
        # Create target instance
        target_instance = TargetFactory.create(actual_target, stack_obj.config.config, params)
        target_instance.validate_credentials()
        terraform_provisioner = target_instance.get_provisioner(stack_obj)
        terraform_provisioner.validate()
        
        # Print stack information
        ui.print_stack_info(stack_obj, target_instance)

        with ui.spinner("[bold blue]🚀 Deploying Infrastructure...[/bold blue]"):
            outputs = terraform_provisioner.apply()
        
        # Print outputs
        ui.print_success("✅ Infrastructure deployed!")
        ui.print_outputs(outputs)
               
    except Exception as e:
        ui.print_error(f"Error: {str(e)}")
        raise click.ClickException(str(e))
    finally:
        end_time = time.time()
        total_time = round(end_time - start_time)
        ui.print_time(total_time)

@cli.command()
@click.option('--stack', required=True, help='Name of the stack (e.g. gcp-web)')
@click.option('--target', help='Deployment target (gcp, onprem). Defaults to stack\'s default target if not provided.')
@click.option('--project-id', help='GCP Project ID (required for GCP target)')
@click.option('--region', help='Region to deploy to (overrides stack config)')
def plan(stack: str, target: str, project_id: str, region: str):
    """Show what will be deployed (Terraform plan)."""
    ui.print_header()
    params = DeployParameters(
        stack=stack,
        target=Target(target) if target else None,
        project_id=project_id,
        region=region
    )
    stack_obj = get_stack(params.stack)
    actual_target = params.target or stack_obj.default_target
    target_instance = TargetFactory.create(actual_target, stack_obj.config.config, params)
    target_instance.validate_credentials()
    terraform_provisioner = target_instance.get_provisioner(stack_obj)
    terraform_provisioner.validate()
    with ui.spinner("[bold blue]🔎 Generating deployment plan...[/bold blue]"):
        plan_output = terraform_provisioner.plan()
    ui.console.print(f"[bold yellow]{plan_output}[/bold yellow]")

if __name__ == '__main__':
    cli()