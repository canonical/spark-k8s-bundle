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

from spark_test.core.s3 import Credentials

logger = logging.getLogger(__name__)

T = TypeVar("T")
S = TypeVar("S")
SECRET_NAME_PREFIX = "integrator-hub-conf-"


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


def generate_tmp_file(data: dict, tmp_folder: Path) -> Path:
    import uuid

    (file := tmp_folder / f"{uuid.uuid4().hex}.yaml").write_text(yaml.dump(data))
    return file


def list_s3_objects(path: str, bucket: str, credentials: Credentials) -> Optional[str]:
    """List folders inside a specified bucket."""
    session = boto3.session.Session(
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
    )
    s3 = session.client(
        "s3",
        endpoint_url=credentials.endpoint or "https://s3.amazonaws.com",
    )

    try:
        objs = []
        objects = s3.list_objects_v2(Bucket=bucket)
        for ob in objects["Contents"]:
            logger.info(ob)
            objs.append(ob["Key"])
        return objs

    except ClientError:
        logger.error("Invalid S3 credentials...")
        return None
    except SSLError:
        logger.error("SSL validation failed...")
        return None
    except Exception as e:
        logger.error(f"S3 related error {e}")
        return None
