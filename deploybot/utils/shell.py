import subprocess

class ShellExecutor:
    def __init__(self):
        pass

    def execute(self, command: str) -> tuple[str, str]:
        print(f"Executing command: {command}")
        try:
            process = subprocess.Popen(
                command,
                 shell=True,
                  stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE
                )

            print("stdout:")
            stdout, stderr = process.communicate()
            standard_out = stdout.decode("utf-8")
            standard_err = stderr.decode("utf-8")
            print(standard_out)

            exit_code = process.returncode

            print(f"exit_code: {exit_code}")
            print(f"stderror: {standard_err}")

            if exit_code != 0:
                msg = f"Failed to execute command '{command}' with exit code '{exit_code}'. Stderr: {standard_err}"
                raise Exception(msg)
            
            return standard_out, standard_err
        except subprocess.SubprocessError as e:
            raise subprocess.SubprocessError(f"Failed to execute command '{command}'. Error: {e}")

