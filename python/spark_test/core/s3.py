import os
from dataclasses import dataclass
from typing import List

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


@dataclass
class Credentials:
    """Class representing S3 credentials."""

    access_key: str
    secret_key: str
    host: str

    @property
    def endpoint(self) -> str:
        """Return the S3 endpoint."""
        return f"http://{self.host}:80"


class Bucket:
    """Class representing a S3 bucket."""

    def __init__(self, s3, bucket_name: str):
        """Create an instance of Bucket class.

        Args:
            s3: boto3 class representing the S3 session
            bucket_name: name of the bucket
        """
        self.s3 = s3
        self.bucket_name = bucket_name

    @classmethod
    def create(cls, bucket_name: str, credentials: Credentials):
        """Create and return an instance of the Bucket class.

        Args:
            bucket_name: name of the bucket
            credentials: S3 credentials

        Returns:
            Bucket object
        """

        config = Config(connect_timeout=60, retries={"max_attempts": 0})
        session = boto3.session.Session(
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
        )

        s3 = session.client("s3", endpoint_url=credentials.endpoint, config=config)

        if cls._exists(bucket_name, s3):
            raise ValueError(f"Cannot create bucket {bucket_name}. Already exists.")

        s3.create_bucket(Bucket=bucket_name)

        return Bucket(s3, bucket_name)

    def init(self):
        """Initialize the bucket to be used with Spark."""
        self.s3.put_object(Bucket=self.bucket_name, Key=("spark-events/"))
        return self

    def delete(self):
        """Delete the current pod."""
        if not self.exists():
            return

        objs = [{"Key": x["Key"]} for x in self.list_objects()]
        self.s3.delete_objects(Bucket=self.bucket_name, Delete={"Objects": objs})
        self.s3.delete_bucket(Bucket=self.bucket_name)

        self.s3.close()
        self.s3 = None

    @staticmethod
    def _exists(bucket_name, s3) -> bool:
        buckets = [
            bucket
            for bucket in s3.list_buckets()["Buckets"]
            if bucket["Name"] == bucket_name
        ]
        return len(buckets) > 0

    def exists(self) -> bool:
        """Check if the bucket exists."""
        return self._exists(self.bucket_name, self.s3)

    def upload_file(self, file_name, object_name=None):
        """Upload a file to an S3 bucket

        Args:
            file_name: File to upload
            object_name: S3 object name. If not specified then file_name is used

        Returns:
             True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file
        try:
            _ = self.s3.upload_file(file_name, self.bucket_name, object_name)
        except ClientError:
            return False
        return True

    def list_objects(self) -> List[dict]:
        """Return the list of object contained in the bucket"""
        return self.s3.list_objects_v2(Bucket=self.bucket_name)["Contents"]
