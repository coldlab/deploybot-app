import os
import json
from typing import Dict, Any
from .base import BaseProvisioner
from deploybot.core.recipie_registry import RecipeRegistry

class NativeProvisioner(BaseProvisioner):
    def __init__(self, recipe_dir: str, config: Dict[str, Any]):
        super().__init__(stack_path=os.path.dirname(recipe_dir), config=config)
        self.recipe_dir = recipe_dir
        self.variables = config.get('variables', {})
        self.stack_name = config.get('stack_name', '')

    def validate(self) -> None:
        if not os.path.isfile(os.path.join(self.recipe_dir, 'recipe.py')):
            raise FileNotFoundError(f"No recipe.py found in {self.recipe_dir}")

    def _write_variables(self) -> None:
        variables_file = os.path.join(self.recipe_dir, 'variables.json')
        with open(variables_file, 'w') as f:
            json.dump(self.variables, f, indent=2)
    
    def init(self) -> None:
        self._write_variables()

    def apply(self) -> None:
        recipe_cls = RecipeRegistry.get(self.stack_name)
        recipe = recipe_cls()
        recipe.deploy()

    def destroy(self) -> None:
        recipe_cls = RecipeRegistry.get(self.stack_name)
        recipe = recipe_cls()
        recipe.destroy()
