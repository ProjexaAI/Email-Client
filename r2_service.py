import boto3
from botocore.client import Config
import requests
from typing import Optional
from auth import get_settings

class R2Service:
    def __init__(self):
        pass

    def get_client(self):
        """Get R2 client with settings from database"""
        settings = get_settings()

        account_id = settings.get("r2_account_id", "")
        access_key_id = settings.get("r2_access_key_id", "")
        secret_access_key = settings.get("r2_secret_access_key", "")

        if not all([account_id, access_key_id, secret_access_key]):
            raise Exception("R2 credentials not configured. Please set them in settings.")

        return boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )

    def upload_file(self, file_content: bytes, filename: str, content_type: str) -> str:
        """
        Upload a file to R2 and return the public URL
        """
        try:
            settings = get_settings()
            bucket_name = settings.get("r2_bucket_name", "")
            public_url = settings.get("r2_public_url", "")

            if not bucket_name:
                raise Exception("R2 bucket name not configured")

            s3_client = self.get_client()
            s3_client.put_object(
                Bucket=bucket_name,
                Key=filename,
                Body=file_content,
                ContentType=content_type
            )

            # Return public URL
            return f"{public_url}/{filename}"
        except Exception as e:
            print(f"Error uploading to R2: {e}")
            raise

    def download_and_upload_attachment(self, attachment_url: str, filename: str, content_type: str) -> str:
        """
        Download an attachment from Resend and upload to R2
        """
        try:
            # Download the file
            response = requests.get(attachment_url)
            response.raise_for_status()

            # Upload to R2
            return self.upload_file(response.content, filename, content_type)
        except Exception as e:
            print(f"Error downloading and uploading attachment: {e}")
            raise

r2_service = R2Service()
