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
    
    return target_instance, infrastructure_provisioner

@cli.command()
@click.option('--stack', required=True, help='Name of the stack (e.g. gcp-web)')
@click.option('--target', help='Deployment target (gcp, aws). Defaults to stack\'s default target if not provided.')
@click.option('--project-id', help='GCP Project ID (required for GCP target)')
@click.option('--region', help='Region to deploy to (overrides stack config)')
# @click.option('--verbose', '-v', is_flag=True, help='Enable verbose output during deployment')
def deploy(stack: str, target: str, project_id: str, region: str):
    """Deploy a stack to the specified target."""
    start_time = time.time()

    try:
        # Setup stack and provisioner
        target_instance, infrastructure_provisioner = _setup_stack_and_provisioner(
            stack, target, project_id, region
        )
        
        # Print deployment header
        print("=" * 60)
        print("🚀 DeployBot - Infrastructure Deployment")
        print("=" * 60)
        
        # Print deployment information
        print(f"\n📋 Deployment Information:")
        print(f"   Stack: {stack}")
        print(f"   Target: {target.upper()}")
        print(f"   Region: {target_instance.region}")
        
        print(f"\n⚡ Starting deployment...\n")
        outputs = infrastructure_provisioner.apply()
        
        # Print success summary
        print(f"\n✅ Deployment completed successfully!")
        print(f"   Total time: {round(time.time() - start_time)} seconds")
        
        # Print outputs if available
        if outputs:
            print(f"\n📊 Deployment Outputs:")
            for key, value in outputs.items():
                if key == "app_url":
                    print(f"   🌐 Application URL: {value}")
                elif key == "ssh_access":
                    print(f"   🔒 SSH Access: {value}")
                else:
                    print(f"   {key}: {value}")
        
        print(f"\n" + "=" * 60)
        print("🎉 Deployment finished! Your application is now live.")
        print("=" * 60)
               
    except Exception as e:
        print(f"\n❌ Deployment failed!")
        print(f"   Error: {str(e)}")
        print(f"   Total time: {round(time.time() - start_time)} seconds")
        raise click.ClickException(str(e))

@cli.command()
@click.option('--stack', required=True, help='Name of the stack (e.g. gcp-web)')
@click.option('--target', help='Deployment target (gcp, onprem). Defaults to stack\'s default target if not provided.')
@click.option('--project-id', help='GCP Project ID (required for GCP target)')
@click.option('--region', help='Region to deploy to (overrides stack config)')
def plan(stack: str, target: str, project_id: str, region: str):
    """Show what will be deployed (Terraform plan)."""
    
    try:
        # Setup stack and provisioner
        target_instance, infrastructure_provisioner = _setup_stack_and_provisioner(
            stack, target, project_id, region
        )

        print("=" * 60)
        print("🔍 DeployBot - Deployment Plan")
        print("=" * 60)
        
        print(f"\n📋 Plan Information:")
        print(f"   Stack: {stack}")
        print(f"   Target: {target.upper()}")
        print(f"   Region: {target_instance.region}")
        
        print(f"\n🔎 Generating deployment plan...")
        infrastructure_provisioner.plan()
        
    except Exception as e:
        print(f"\n❌ Plan generation failed!")
        print(f"   Error: {str(e)}")
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

    try:
        # Setup stack and provisioner
        target_instance, infrastructure_provisioner = _setup_stack_and_provisioner(
            stack, target, project_id, region
        )

        # Print destruction header
        print("=" * 60)
        print("🗑️  DeployBot - Infrastructure Destruction")
        print("=" * 60)
        
        # Print destruction information
        print(f"\n📋 Destruction Information:")
        print(f"   Stack: {stack}")
        print(f"   Target: {target.upper()}")
        print(f"   Region: {target_instance.region}")

        # Confirmation prompt
        if not force:
            print(f"\n⚠️  WARNING: This will destroy all resources in stack '{stack}'!")
            print(f"   This action cannot be undone!")
            if not click.confirm("Are you sure you want to continue?"):
                print(f"\n❌ Destruction cancelled.")
                return

        print(f"\n⚡ Starting destruction...")
        infrastructure_provisioner.destroy()
        
        # Print success summary
        print(f"\n✅ Destruction completed successfully!")
        print(f"   Total time: {round(time.time() - start_time)} seconds")
        
        print(f"\n" + "=" * 60)
        print("🎉 All resources have been destroyed.")
        print("=" * 60)
               
    except Exception as e:
        print(f"\n❌ Destruction failed!")
        print(f"   Error: {str(e)}")
        print(f"   Total time: {round(time.time() - start_time)} seconds")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()