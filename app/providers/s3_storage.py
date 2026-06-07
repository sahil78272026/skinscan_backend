import boto3
from botocore.exceptions import ClientError
import logging
from app.providers.base_storage import StorageService
from app.config import settings

logger = logging.getLogger(__name__)

class S3StorageService(StorageService):
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
            region_name="auto"
        )
        self.bucket = settings.r2_bucket

    async def upload(self, file_bytes: bytes, object_name: str, content_type: str) -> str:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=object_name,
                Body=file_bytes,
                ContentType=content_type
            )
            return object_name
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            raise Exception("Storage upload failed")

    async def delete(self, object_name: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=object_name)
            return True
        except ClientError as e:
            logger.error(f"Failed to delete from S3: {e}")
            return False

    async def signed_url(self, object_name: str) -> str | None:
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": object_name},
                ExpiresIn=settings.signed_url_expiry_seconds
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate signed url: {e}")
            return None
