#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""Azure storage fixtures."""

import os
import uuid

import pytest

from spark_test.core.azure_storage import Container, Credentials


@pytest.fixture(scope="session")
def azure_credentials():
    """Azure storage credentials."""
    yield Credentials(
        storage_account=os.environ["AZURE_STORAGE_ACCOUNT"],
        secret_key=os.environ["AZURE_STORAGE_KEY"],
    )


@pytest.fixture(scope="module")
def container_name():
    """Azure storage container name."""
    return f"test-container-{uuid.uuid4()}"


@pytest.fixture(scope="module")
def container(azure_credentials, container_name, request):
    """Get or create azure storage container."""
    try:
        _container = Container.create(container_name, azure_credentials)
        _container.init()
    except FileExistsError:
        _container = Container.get(container_name, azure_credentials)

    yield _container

    keep_models = bool(request.config.getoption("--keep-models"))
    if not keep_models:
        _container.delete()
