from deploybot.utils.shell import ShellExecutor
import os

class GCloudExecutor:
    def __init__(self):
        self.shell = ShellExecutor()

    def execute(self, command: str, project_id: str) -> str:
        account = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if account is None:
            raise Exception("GOOGLE_APPLICATION_CREDENTIALS is not set")
        
        gcloud_command = f"gcloud {command} --project {project_id} --format=json --quiet --account={account}"

        stdout, stderr = self.shell.execute(gcloud_command)
        return stdout
