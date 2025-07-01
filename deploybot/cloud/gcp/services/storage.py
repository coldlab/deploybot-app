import tarfile
import os
from deploybot.cloud.gcp.storage import GCPStorage


class GCPStorageService:
    def __init__(self):
        self.client = GCPStorage()

    def upload_directory_as_tar(self, bucket_name: str, source_dir: str, object_name: str) -> str:
        tar_path = f"/tmp/{object_name}.tar.gz"
        with tarfile.open(tar_path, "w:gz") as tar:
            tar.add(source_dir, arcname=".")

        # Upload to GCS
        self.client.upload_file(bucket_name, tar_path, f"{object_name}.tar.gz")
        print(f"Uploaded source to gs://{bucket_name}/{object_name}.tar.gz")
        
        # Clean up temporary tar file
        os.remove(tar_path)
        
        return f"{object_name}.tar.gz"