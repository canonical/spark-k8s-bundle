#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def exists(self) -> bool:
        """Check if the bucket exists."""
        pass

    @abstractmethod
    def upload_file(self, file_name, object_name=None):
        pass

    @abstractmethod
    def get_uri(self, file: str):
        pass

    @abstractmethod
    def list(self) -> list[str]:
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        pass
