from .client_factory import GCPClientFactory
from google.cloud.storage import Blob

class GCPStorage:
    def __init__(self):
        self.client = GCPClientFactory().get_storage_client()

    def upload_file(self, bucket_name: str, file_path: str, destination_path: str) -> Blob:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(destination_path)
        blob.upload_from_filename(file_path)
        return blob
    
    def delete_file(self, bucket_name: str, file_path: str) -> None:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        blob.delete()

    def file_exists(self, bucket_name: str, file_path: str) -> bool:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        return blob.exists()

    def get_file(self, bucket_name: str, file_path: str) -> Blob:
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        return blob

