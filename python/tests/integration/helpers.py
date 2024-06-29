# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import logging
import os
import shutil
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, Optional, TypeVar

import boto3
import yaml
from botocore.exceptions import ClientError, SSLError
from pytest_operator.plugin import OpsTest
from spark8t.domain import ServiceAccount

from spark_test.core.s3 import Bucket, Credentials

from .terraform import Terraform

T = TypeVar("T")
S = TypeVar("S")
SECRET_NAME_PREFIX = "integrator-hub-conf-"
COS_ALIAS = "cos"

logger = logging.getLogger(__name__)


@dataclass
class Bundle(Generic[T]):
    main: T
    overlays: list[T]

    def map(self, f: Callable[[T], S]) -> "Bundle[S]":
        return Bundle(main=f(self.main), overlays=[f(item) for item in self.overlays])


async def set_s3_credentials(
    ops_test: OpsTest, credentials: Credentials, application_name="s3", num_unit=0
) -> Any:
    """Use the charm action to start a password rotation."""
    params = {
        "access-key": credentials.access_key,
        "secret-key": credentials.secret_key,
    }

    action = await ops_test.model.units.get(
        f"{application_name}/{num_unit}"
    ).run_action("sync-s3-credentials", **params)

    return await action.wait()


async def get_address(ops_test: OpsTest, app_name, unit_num=0) -> str:
    """Get the address for a unit."""
    status = await ops_test.model.get_status()  # noqa: F821
    address = status["applications"][app_name]["units"][f"{app_name}/{unit_num}"][
        "address"
    ]
    return address


async def get_kyuubi_credentials(
    ops_test: OpsTest, application_name="kyuubi", num_unit=0
) -> dict[str, str]:
    """Use the charm action to start a password rotation."""

    action = await ops_test.model.units.get(
        f"{application_name}/{num_unit}"
    ).run_action("get-password")

    results = (await action.wait()).results

    address = await get_address(ops_test, app_name=application_name, unit_num=num_unit)

    return {"username": "admin", "password": results["password"], "host": address}


async def get_postgresql_credentials(
    ops_test: OpsTest, application_name, num_unit=0
) -> dict[str, str]:
    """Return the credentials that can be used to connect to postgresql database."""
    action = await ops_test.model.units.get(
        f"{application_name}/{num_unit}"
    ).run_action("get-password")

    results = (await action.wait()).results
    address = await get_address(ops_test, app_name=application_name, unit_num=num_unit)

    return {"username": "operator", "password": results["password"], "host": address}


def render_yaml(file: Path, data: dict, ops_test: OpsTest) -> dict:
    if os.path.splitext(file)[1] == ".j2":
        bundle_file = ops_test.render_bundle(
            file, **{str(k): str(v) for k, v in data.items()}
        )
    else:
        bundle_file = file

    return yaml.safe_load(bundle_file.read_text())


def _local(pointer) -> str:
    return (
        f"./{pointer.relative_to(Path.cwd())}"
        if isinstance(pointer, Path)
        else str(pointer)
    )


async def deploy_bundle(ops_test: OpsTest, bundle: Bundle) -> tuple[int, str, str]:

    cmds = [
        "deploy",
        "--trust",
        "-m",
        ops_test.model_full_name,
        _local(bundle.main),
    ] + sum([["--overlay", _local(overlay)] for overlay in bundle.overlays], [])

    retcode, stdout, stderr = await ops_test.juju(*cmds)

    return retcode, stdout, stderr


@contextmanager
def local_tmp_folder(name: str = "tmp"):
    if (tmp_folder := Path.cwd() / name).exists():
        shutil.rmtree(tmp_folder)
    tmp_folder.mkdir()

    yield tmp_folder

    shutil.rmtree(tmp_folder)


def generate_tmp_file(data: dict, tmp_folder: Path) -> Path:
    import uuid

    (file := tmp_folder / f"{uuid.uuid4().hex}.yaml").write_text(yaml.dump(data))
    return file


def get_secret_data(namespace: str, service_account: str):
    """Retrieve secret data for a given namespace and secret."""
    command = ["kubectl", "get", "secret", "-n", namespace, "--output", "json"]
    secret_name = f"{SECRET_NAME_PREFIX}{service_account}"
    try:
        output = subprocess.run(command, check=True, capture_output=True)
        # output.stdout.decode(), output.stderr.decode(), output.returncode
        result = output.stdout.decode()
        logger.info(f"Command: {command}")
        logger.info(f"Secrets for namespace: {namespace}")
        logger.info(f"Request secret: {secret_name}")
        secrets = json.loads(result)
        data = {}
        for secret in secrets["items"]:
            name = secret["metadata"]["name"]
            logger.info(f"\t secretName: {name}")
            if name == secret_name:
                data = {}
                if "data" in secret:
                    data = secret["data"]
        return data
    except subprocess.CalledProcessError as e:
        return e.stdout.decode(), e.stderr.decode(), e.returncode


async def deploy_bundle_yaml(
    bundle: Bundle,
    # service_account: ServiceAccount,
    bucket: Bucket,
    cos: str | None,
    ops_test: OpsTest,
) -> list[str]:
    """Deploy the Bundle in YAML format.

    Args:
        bundle: Bundle object
        service_account: Kyuubi service account to be used
        bucket: S3 bucket to be used in the deployment
        ops_test: OpsTest class

    Returns:
        list of charms deployed
    """

    data = {
        "namespace": ops_test.model_name, # service_account.namespace,
        "service_account": "kyuubi-test-user",
        "bucket": bucket.bucket_name,
        "s3_endpoint": bucket.s3.meta.endpoint_url,
    } | ({"cos_controller": ops_test.controller_name, "cos_model": cos} if cos else {})

    bundle_content = bundle.map(lambda path: render_yaml(path, data, ops_test))

    with local_tmp_folder("tmp") as tmp_folder:
        logger.info(tmp_folder)

        bundle_tmp = bundle_content.map(
            lambda bundle_data: generate_tmp_file(bundle_data, tmp_folder)
        )

        retcode, stdout, stderr = await deploy_bundle(ops_test, bundle_tmp)

        assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
        logger.info(stdout)

    charms: Bundle[list[str]] = bundle_content.map(
        lambda bundle_data: list(bundle_data["applications"].keys())
    )

    return charms.main + sum(charms.overlays, [])


async def deploy_bundle_terraform(
    bundle: Terraform,
    # service_account: ServiceAccount,
    bucket: Bucket,
    cos: str | None,
    ops_test: OpsTest,
) -> list[str]:
    tf_vars = {
        "s3": {
            "bucket": bucket.bucket_name,
            "endpoint": bucket.s3.meta.endpoint_url,
        },
        "kyuubi_user": "kyuubi-test-user",
        "model": ops_test.model_name,
    } | ({"cos_model": cos} if cos else {})

    outputs = bundle.apply(tf_vars=tf_vars)

    return list(outputs["charms"]["value"].values())
