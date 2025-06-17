import os
import json
import subprocess
from typing import Dict, Any
from .base import BaseProvisioner

class TerraformProvisioner(BaseProvisioner):
    def __init__(self, tf_dir: str, config: Dict[str, Any]):
        super().__init__(stack_path=os.path.dirname(tf_dir), config=config)
        self.tf_dir = tf_dir
        self.provider = config.get('provider', 'aws')
        self.variables = config.get('variables', {})
    
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
    
    def apply(self) -> Dict[str, Any]:
        try:
            self.init()
            subprocess.run(['terraform', 'apply', '-auto-approve'], 
                         cwd=self.tf_dir, check=True, capture_output=True, text=True)
            
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
    
    def destroy(self) -> None:
        try:
            subprocess.run(['terraform', 'destroy', '-auto-approve'], 
                          cwd=self.tf_dir, check=True, capture_output=True, text=True)
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