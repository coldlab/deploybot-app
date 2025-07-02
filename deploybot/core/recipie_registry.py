from stacks.fastapi_postgres.native.gcp.recipe import FastAPIPostgresRecipe

class RecipeRegistry:
    _registry = {
        'fastapi_postgres': FastAPIPostgresRecipe
    }

    @classmethod
    def register(cls, recipe_name: str, recipe_class: type):
        cls._registry[recipe_name] = recipe_class

    @classmethod
    def get(cls, recipe_name: str) -> type:
        if recipe_name not in cls._registry:
            raise ValueError(f"Recipe {recipe_name} not found in registry")
        return cls._registry[recipe_name]
    
    @classmethod
    def list(cls) -> list[str]:
        return list(cls._registry.keys())
