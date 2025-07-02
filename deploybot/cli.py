import click
import time
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

def _setup_stack_and_provisioner(stack: str, target: str, project_id: str, region: str):
    """Helper method to set up stack and provisioner for commands."""
    # Create parameters model
    params = DeployParameters(
        stack=stack,
        target=Target(target) if target else None,
        project_id=project_id,
        region=region,
        # provisioner=Provisioner.PULUMI
    )
    
    # Load stack configuration
    stack_obj = get_stack(params.stack)
    
    # Determine target
    actual_target = params.target or stack_obj.default_target
    
    if params.provisioner is None:
        params.provisioner = stack_obj.default_provisioner
   
    # Create target instance
    target_instance = TargetFactory.create(actual_target, stack_obj.config.config, params)
    target_instance.validate_credentials()
    infrastructure_provisioner = target_instance.get_provisioner(stack_obj)
    infrastructure_provisioner.validate()
    
    return stack_obj, target_instance, infrastructure_provisioner

@cli.command()
@click.option('--stack', required=True, help='Name of the stack (e.g. gcp-web)')
@click.option('--target', help='Deployment target (gcp, aws). Defaults to stack\'s default target if not provided.')
@click.option('--project-id', help='GCP Project ID (required for GCP target)')
@click.option('--region', help='Region to deploy to (overrides stack config)')
# @click.option('--verbose', '-v', is_flag=True, help='Enable verbose output during deployment')
def deploy(stack: str, target: str, project_id: str, region: str):
    """Deploy a stack to the specified target."""
    start_time = time.time()
    ui.print_header()

    try:
        # Setup stack and provisioner
        stack_obj, target_instance, infrastructure_provisioner = _setup_stack_and_provisioner(
            stack, target, project_id, region
        )
        
        # Print stack information
        ui.print_stack_info(stack_obj, target_instance)

        outputs = infrastructure_provisioner.apply()

        # if verbose:
        #     # Define progress callback for real-time updates
        #     def progress_callback(event: str):
        #         ui.console.print(f"  {event}")
            
        #     ui.console.print("[bold blue]🚀 Deploying Infrastructure...[/bold blue]")
        #     outputs = infrastructure_provisioner.apply(verbose=True, progress_callback=progress_callback)
        # else:
        #     with ui.spinner("[bold blue]🚀 Deploying Infrastructure...[/bold blue]"):
        #         outputs = infrastructure_provisioner.apply(verbose=False)
        
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
    
    try:
        # Setup stack and provisioner
        stack_obj, target_instance, infrastructure_provisioner = _setup_stack_and_provisioner(
            stack, target, project_id, region
        )
        
        with ui.spinner("[bold blue]🔎 Generating deployment plan...[/bold blue]"):
            plan_output = infrastructure_provisioner.plan()
        ui.console.print(f"[bold yellow]{plan_output}[/bold yellow]")
    except Exception as e:
        ui.print_error(f"Error: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
@click.option('--stack', required=True, help='Name of the stack to destroy (e.g. gcp-web)')
@click.option('--target', help='Deployment target (gcp, aws). Defaults to stack\'s default target if not provided.')
@click.option('--project-id', help='GCP Project ID (required for GCP target)')
@click.option('--region', help='Region to deploy to (overrides stack config)')
# @click.option('--verbose', '-v', is_flag=True, help='Enable verbose output during destruction')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation prompt')
def destroy(stack: str, target: str, project_id: str, region: str, force: bool):
    """Destroy a deployed stack."""
    start_time = time.time()
    ui.print_header()

    try:
        # Setup stack and provisioner
        stack_obj, target_instance, infrastructure_provisioner = _setup_stack_and_provisioner(
            stack, target, project_id, region
        )
        
        # Print stack information
        ui.print_stack_info(stack_obj, target_instance)

        # Confirmation prompt
        if not force:
            ui.console.print(f"[bold red]⚠️  WARNING: This will destroy all resources in stack '{stack}'![/bold red]")
            if not click.confirm("Are you sure you want to continue?"):
                ui.console.print("[bold yellow]❌ Destruction cancelled.[/bold yellow]")
                return

        infrastructure_provisioner.destroy()

        # if verbose:
        #     # Define progress callback for real-time updates
        #     def progress_callback(event: str):
        #         ui.console.print(f"  {event}")
            
        #     ui.console.print("[bold red]🗑️ Destroying Infrastructure...[/bold red]")
        #     infrastructure_provisioner.destroy(verbose=True, progress_callback=progress_callback)
        # else:
        #     with ui.spinner("[bold red]🗑️ Destroying Infrastructure...[/bold red]"):
        #         infrastructure_provisioner.destroy(verbose=False)
        
        # Print success message
        ui.print_success("✅ Infrastructure destroyed!")
               
    except Exception as e:
        ui.print_error(f"Error: {str(e)}")
        raise click.ClickException(str(e))
    finally:
        end_time = time.time()
        total_time = round(end_time - start_time)
        ui.print_time(total_time)

if __name__ == '__main__':
    cli()