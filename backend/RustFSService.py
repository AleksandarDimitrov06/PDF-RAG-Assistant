import boto3
from botocore.exceptions import ClientError
from backend.config import settings

class RustFSService:
    def __init__(self):
        self.bucket = settings.rustfs_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.rustfs_endpoint,
            aws_access_key_id=settings.rustfs_access_key,
            aws_secret_access_key=settings.rustfs_secret_key,
        )

        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchBucket"}:
                self.client.create_bucket(Bucket=self.bucket)
            else:
                raise


    def upload_pdf(self, file_bytes: bytes, object_key: str):
        self.client.put_object(
            Bucket=self.bucket,
            Key=object_key,
            Body=file_bytes,
            ContentType="application/pdf",
        )