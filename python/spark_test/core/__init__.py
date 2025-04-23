#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""Core module."""

from abc import ABC, abstractmethod


class ObjectStorageUnit(ABC):
    """Object storage abstraction."""

    @abstractmethod
    def init(self):
        """Initialize object storage."""
        pass

    @abstractmethod
    def delete(self):
        """Delete object storage."""
        pass

    @abstractmethod
    def exists(self) -> bool:
        """Check if the bucket exists."""
        pass

    @abstractmethod
    def upload_file(self, file_name, object_name=None):
        """Upload file to object storage."""
        pass

    @abstractmethod
    def get_uri(self, file: str):
        """Get file URI."""
        pass

    @abstractmethod
    def list_content(self) -> list[str]:
        """List resources."""
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup resources."""
        pass
