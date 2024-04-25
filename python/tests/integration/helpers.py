import os
import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

import yaml
from pytest_operator.plugin import OpsTest

from spark_test.core.s3 import Credentials

T = TypeVar("T")
S = TypeVar("S")


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
