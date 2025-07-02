import os
import json
import inspect
from abc import ABC, abstractmethod
from pathlib import Path

class BaseRecipe(ABC):
    def __init__(self):
        self.variables = self._load_variables()

    def _load_variables(self):
        child_file = inspect.getfile(self.__class__)
        var_file = Path(child_file).parent / "variables.json"
        # var_file = os.path.join(os.path.dirname(__file__), 'variables.json')
        with open(var_file, 'r') as f:
            return json.load(f)

    @abstractmethod
    def deploy(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def plan(self):
        pass
