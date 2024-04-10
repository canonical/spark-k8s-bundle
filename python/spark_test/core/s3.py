import os
from dataclasses import dataclass

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


@dataclass
class Credentials:
    access_key: str
    secret_key: str
    host: str

    @property
    def endpoint(self) -> str:
        return f"http://{self.host}:80"


class Bucket:

    def __init__(self, s3, bucket_name: str):
        self.s3 = s3
        self.bucket_name = bucket_name

    @classmethod
    def create(cls, bucket_name: str, credentials: Credentials):

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
        self.s3.put_object(Bucket=self.bucket_name, Key=("spark-events/"))
        return self

    def delete(self):
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

    def exists(self):
        return self._exists(self.bucket_name, self.s3)

    def upload_file(self, file_name, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
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

    def list_objects(self):
        return self.s3.list_objects_v2(Bucket=self.bucket_name)["Contents"]
