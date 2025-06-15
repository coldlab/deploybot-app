import subprocess
import os


class TerraformProvisionError(Exception):
    pass


def run_terraform(stack_path):
    tf_dir = os.path.join(stack_path, 'terraform')

    # Step 1: terraform init
    init_cmd = ['terraform', 'init']
    apply_cmd = ['terraform', 'apply', '-auto-approve']
    output_cmd = ['terraform', 'output', '-raw', 'public_ip']

    try:
        subprocess.run(init_cmd, cwd=tf_dir, check=True)
        subprocess.run(apply_cmd, cwd=tf_dir, check=True)
        result = subprocess.run(output_cmd, cwd=tf_dir, check=True, capture_output=True, text=True)
        ip = result.stdout.strip()
        return ip
    except subprocess.CalledProcessError as e:
        raise TerraformProvisionError(f"Terraform failed: {e}")
