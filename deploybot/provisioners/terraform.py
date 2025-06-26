import os
import json
import subprocess
from typing import Dict, Any
from .base import BaseProvisioner
from .terraform_parser import TerraformOutputParser

class TerraformProvisioner(BaseProvisioner):
    def __init__(self, tf_dir: str, config: Dict[str, Any]):
        super().__init__(stack_path=os.path.dirname(tf_dir), config=config)
        self.tf_dir = tf_dir
        self.provider = config.get('provider', 'aws')
        self.variables = config.get('variables', {})
        self.parser = TerraformOutputParser()
    
    def validate(self) -> None:
        if not os.path.isfile(os.path.join(self.tf_dir, 'main.tf')):
            raise FileNotFoundError(f"No Terraform main.tf found in {self.tf_dir}")
    
    def _write_tfvars(self) -> None:
        """Write terraform.tfvars.json file with provider-specific variables."""
        tfvars_path = os.path.join(self.tf_dir, 'terraform.tfvars.json')
        with open(tfvars_path, 'w') as f:
            json.dump(self.variables, f, indent=2)
    
    def init(self) -> None:
        self._write_tfvars()
        try:
            subprocess.run(['terraform', 'init'], cwd=self.tf_dir, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"Terraform init failed: {e.stderr.strip() if e.stderr else str(e)}")
    
    def _run_terraform_command(self, command: list, verbose: bool = False, progress_callback=None) -> None:
        """Generic method to run any Terraform command with optional verbose output parsing."""
        if not verbose:
            subprocess.run(command, cwd=self.tf_dir, check=True, capture_output=True, text=True)
            return

        # Run terraform command with streaming output
        process = subprocess.Popen(
            command,
            cwd=self.tf_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream and parse output in real-time
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                if not line:
                    continue
                
                # Parse the line for resource events
                event = self.parser.parse_line(line)
                if not event:
                    continue
                
                formatted_event = self.parser.format_event(event)
                if progress_callback:
                    progress_callback(formatted_event)
        
        process.wait()
        if process.returncode == 0:
            return

        raise subprocess.CalledProcessError(process.returncode, ' '.join(command))
    
    def apply(self, verbose: bool = False, progress_callback=None) -> Dict[str, Any]:
        """Apply Terraform configuration with optional verbose output parsing."""
        try:
            self.init()
            
            self._run_terraform_command(['terraform', 'apply', '-auto-approve'], verbose, progress_callback)
            
            # Get outputs
            result = subprocess.run(
                ['terraform', 'output', '-json'],
                cwd=self.tf_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            output = json.loads(result.stdout)
            return parse_terraform_outputs(output)
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip() if e.stderr else str(e)
            raise Exception(f"Terraform command failed: {error_output}")
    
    def destroy(self, verbose: bool = False, progress_callback=None) -> None:
        """Destroy Terraform infrastructure with optional verbose output parsing."""
        try:
            self.init()
            
            self._run_terraform_command(['terraform', 'destroy', '-auto-approve'], verbose, progress_callback)
            
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip() if e.stderr else str(e)
            raise Exception(f"Terraform destroy failed: {error_output}")
    
    def plan(self) -> str:
        self.init()  # Make sure tfvars and init are done
        try:
            result = subprocess.run(
                ['terraform', 'plan', '-no-color'],
                cwd=self.tf_dir,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip() if e.stderr else str(e)
            raise Exception(f"Terraform plan failed: {error_output}")

def parse_terraform_outputs(raw_outputs):
    """Flatten terraform output dict to key: value, hiding sensitive if needed."""
    parsed = {}
    for key, meta in raw_outputs.items():
        if meta.get("sensitive"):
            parsed[key] = "[SENSITIVE]"
        else:
            parsed[key] = meta.get("value")
    return parsed 