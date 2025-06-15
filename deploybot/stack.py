import os

STACKS_DIR = os.path.join(os.path.dirname(__file__), '..', 'stacks')


class StackNotFoundError(Exception):
    pass


def get_stack_path(stack_name):
    stack_path = os.path.join(STACKS_DIR, stack_name)
    if not os.path.isdir(stack_path):
        raise StackNotFoundError(f"Stack '{stack_name}' not found.")
    return os.path.abspath(stack_path)


def validate_stack(stack_name):
    path = get_stack_path(stack_name)
    compose_path = os.path.join(path, 'docker-compose.yml')
    tf_path = os.path.join(path, 'terraform', 'main.tf')

    if not os.path.isfile(compose_path):
        raise FileNotFoundError(f"No docker-compose.yml found in stack '{stack_name}'")
    if not os.path.isfile(tf_path):
        raise FileNotFoundError(f"No Terraform main.tf found in stack '{stack_name}'")

    return {
        'stack': stack_name,
        'path': path,
        'compose': compose_path,
        'terraform': tf_path
    }
