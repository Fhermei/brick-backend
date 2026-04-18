"""
Storage Service - Handle file uploads to S3
"""

import uuid
import os
from datetime import datetime
from typing import Optional
import boto3
from botocore.exceptions import ClientError
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket_name = os.getenv("AWS_S3_BUCKET", "brick-spmes-storage")

    def upload_file(self, file_content: bytes, filename: str, content_type: str = "image/jpeg") -> Optional[str]:
        """
        Upload a file to S3 and return the URL
        """
        try:
            # Generate unique filename
            ext = filename.split(".")[-1] if "." in filename else "jpg"
            unique_filename = f"{datetime.utcnow().strftime('%Y/%m/%d')}/{uuid.uuid4()}.{ext}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=unique_filename,
                Body=file_content,
                ContentType=content_type,
                Metadata={"original_filename": filename}
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            return url
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return None

    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from S3
        """
        try:
            # Extract key from URL
            key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            logger.error(f"S3 delete failed: {e}")
            return False


storage_service = StorageService()