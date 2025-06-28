import os
import json
import subprocess
import pulumi.automation as auto
from typing import Dict, Any, Optional, Callable
from deploybot.provisioners.base import BaseProvisioner
from deploybot.provisioners.pulumi_parser import PulumiOutputParser

class PulumiProvisioner(BaseProvisioner):
    def __init__(self, work_dir: str, config: Dict[str, Any]):
        super().__init__(stack_path=os.path.dirname(work_dir), config=config)
        self.work_dir = work_dir
        self.provider = config.get('provider', 'aws')
        self.provider_variables = config.get('provider_variables', {})
        self.variables = config.get('variables', {})
        self.stack_name = config.get('stack_name', 'dev')
        self.project_name = config.get('project_name', 'deploybot-project')
        self.parser = PulumiOutputParser()
        
        # Set environment variables for Pulumi
        os.environ["PULUMI_CONFIG_PASSPHRASE"] = "deploybot-local"
        os.environ["PULUMI_SKIP_UPDATE_CHECK"] = "true"
    
    def validate(self) -> None:
        """Validate that required Pulumi files exist."""
        if not os.path.isfile(os.path.join(self.work_dir, 'Pulumi.yaml')):
            raise FileNotFoundError(f"No Pulumi.yaml found in {self.work_dir}")
        if not os.path.isfile(os.path.join(self.work_dir, '__main__.py')):
            raise FileNotFoundError(f"No __main__.py found in {self.work_dir}")
    
   
    def _get_or_create_stack(self) -> auto.Stack:
        """Get existing stack or create a new one."""
        return auto.create_or_select_stack(stack_name=self.stack_name, work_dir=self.work_dir)
    
    def _set_stack_config(self, stack: auto.Stack) -> None:
        """Set stack configuration from the stack.yaml config structure."""
        for key, value in self.provider_variables.items():
            stack.set_config(key, auto.ConfigValue(value=str(value)))

        for key, value in self.variables.items():
            # print(f"Setting config {key} to {value}")
            stack.set_config(key, auto.ConfigValue(value=str(value)))
    
    def init(self) -> None:
        """Initialize Pulumi workspace and stack."""
        try:
            stack = self._get_or_create_stack()
            self._set_stack_config(stack)
            self.stack = stack
        except Exception as e:
            raise Exception(f"Pulumi init failed: {str(e)}")
    
    def _create_parsed_callback(self, progress_callback: Callable) -> Callable:
        """Create a callback that parses and formats Pulumi output."""
        def parsed_callback(output: str):
            event = self.parser.parse_line(output)
            if event:
                formatted_event = self.parser.format_event(event)
                progress_callback(formatted_event)
            else:
                progress_callback(output)
        return parsed_callback

    def _run_pulumi_command(self, command: str, verbose: bool = False, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Generic method to run Pulumi commands with optional verbose output."""
        try:
            self.init()
            
            if command == "up":
                if verbose and progress_callback:
                    parsed_callback = self._create_parsed_callback(progress_callback)
                    results = self.stack.up(on_output=parsed_callback)
                else:
                    results = self.stack.up()
                return results.outputs
            
            elif command == "destroy":
                if verbose and progress_callback:
                    parsed_callback = self._create_parsed_callback(progress_callback)
                    self.stack.destroy(on_output=parsed_callback)
                else:
                    self.stack.destroy()
                return {}
            
            elif command == "preview":
                if verbose and progress_callback:
                    parsed_callback = self._create_parsed_callback(progress_callback)
                    preview = self.stack.preview(on_output=parsed_callback)
                else:
                    preview = self.stack.preview()
                return {"preview": preview}
            
        except Exception as e:
            raise Exception(f"Pulumi {command} failed: {str(e)}")
    
    def apply(self, verbose: bool = False, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Apply Pulumi configuration with optional verbose output parsing."""
        try:
            return self._run_pulumi_command("up", verbose, progress_callback)
        except Exception as e:
            raise Exception(f"Pulumi apply failed: {str(e)}")
    
    def destroy(self, verbose: bool = False, progress_callback: Optional[Callable] = None) -> None:
        """Destroy Pulumi infrastructure with optional verbose output parsing."""
        try:
            self._run_pulumi_command("destroy", verbose, progress_callback)
            self.remove_stack()
        except Exception as e:
            raise Exception(f"Pulumi destroy failed: {str(e)}")
    
    def plan(self) -> str:
        """Show what will be deployed (Pulumi preview)."""
        try:
            preview_result = self._run_pulumi_command("preview", verbose=False)
            return str(preview_result.get("preview", "No preview available"))
        except Exception as e:
            raise Exception(f"Pulumi plan failed: {str(e)}")
    
    def refresh(self) -> None:
        """Refresh Pulumi state to match real-world resources."""
        try:
            self.stack.refresh()
        except Exception as e:
            raise Exception(f"Pulumi refresh failed: {str(e)}")
    
    def remove_stack(self) -> None:
        """Remove the Pulumi stack from workspace."""
        try:
            self.stack.workspace.remove_stack(self.stack_name)
        except Exception as e:
            raise Exception(f"Pulumi stack removal failed: {str(e)}")

def parse_pulumi_outputs(raw_outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Pulumi outputs to a simple key-value format."""
    parsed = {}
    for key, value in raw_outputs.items():
        if hasattr(value, 'value'):
            parsed[key] = value.value
        else:
            parsed[key] = value
    return parsed