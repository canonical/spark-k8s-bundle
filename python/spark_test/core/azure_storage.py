#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import os
from dataclasses import dataclass

from azure.storage.blob import BlobServiceClient


@dataclass
class Credentials:
    """Class representing Azure Storage credentials."""

    secret_key: str
    storage_account: str

    @property
    def connection_string(
        self,
    ) -> str:
        return f"DefaultEndpointsProtocol=https;AccountName={self.storage_account};AccountKey={self.secret_key};EndpointSuffix=core.windows.net"


class Container:
    """Class representing a Azure Storage container."""

    INIT_DIR = "spark-events"
    PLACEHOLDER = ".tmp"

    def __init__(
        self, client: BlobServiceClient, container_name: str, credentials: Credentials
    ):
        """Create an instance of Bucket class.

        Args:
            client: BlobServiceClient class representing the Azure Storage session
            container_name: name of the container
        """
        self.client = client
        self.container_name = container_name
        self.credentials = credentials

    @classmethod
    def get(cls, container_name: str, credentials: Credentials):
        """Return an instance of an existing Container class.

        Args:
            container_name: name of the container
            credentials: Azure Storage credentials

        Returns:
            Container object
        """
        client = BlobServiceClient.from_connection_string(credentials.connection_string)

        if not cls._exists(container_name, client):
            raise FileNotFoundError(f"Bucket {container_name} does not exist.")

        return Container(client, container_name, credentials)

    @classmethod
    def create(cls, container_name: str, credentials: Credentials):
        """Create and return an instance of the Container class.

        Args:
            container_name: name of the container
            credentials: Azure Storage credentials

        Returns:
            Container object
        """
        client = BlobServiceClient.from_connection_string(credentials.connection_string)

        if cls._exists(container_name, client):
            raise FileExistsError(
                f"Cannot create container {container_name}. Already exists."
            )

        client.create_container(container_name)
        return Container(client, container_name, credentials)

    def init(self):
        """Initialize the container to be used with Spark."""
        blob_client = self.client.get_blob_client(
            container=self.container_name, blob=f"{self.INIT_DIR}/{self.PLACEHOLDER}"
        )
        blob_client.upload_blob(b"")

    def delete(self):
        """Delete the current container."""
        if not self.exists():
            return

        container_client = self.client.get_container_client(
            container=self.container_name
        )
        container_client.delete_container()
        self.client.close()
        self.client = None

    @staticmethod
    def _exists(container_name, client: BlobServiceClient) -> bool:
        container_client = client.get_container_client(container=container_name)
        return container_client.exists()

    def exists(self) -> bool:
        """Check if the bucket exists."""
        return self._exists(self.container_name, self.client)

    def upload_file(self, file_name, blob_name=None):
        """Upload a file to an Azure Storage container

        Args:
            file_name: File to upload
            blob_name: Azure container blob name. If not specified then file_name is used

        Returns:
             True if file was uploaded, else False
        """

        # If blob_name was not specified, use file_name
        if blob_name is None:
            blob_name = os.path.basename(file_name)

        # Upload the file
        try:
            container_client = self.client.get_container_client(
                container=self.container_name
            )
            with open(file_name, mode="rb") as data:
                container_client.upload_blob(blob_name, data=data, overwrite=True)
        except Exception:
            return False
        return True

    def list_blobs(self):
        hidden_blobs = [self.INIT_DIR, f"{self.INIT_DIR}/{self.PLACEHOLDER}"]
        container_client = self.client.get_container_client(
            container=self.container_name
        )
        return [
            blob["name"]
            for blob in container_client.list_blobs()
            if blob["name"] not in hidden_blobs
        ]
