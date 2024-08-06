#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import os
import uuid

import pytest

from spark_test.core.azure_storage import Container, Credentials


@pytest.fixture(scope="session")
def azure_credentials():
    yield Credentials(
        storage_account=os.environ["AZURE_STORAGE_ACCOUNT"], 
        secret_key=os.environ["AZURE_STORAGE_KEY"]
    )


@pytest.fixture(scope="module")
def container_name():
    return f"test-container-{uuid.uuid4()}"


@pytest.fixture(scope="module")
def container(azure_credentials, container_name):
    _container = Container.create(container_name, azure_credentials)
    _container.init()
    yield _container
    _container.delete()
