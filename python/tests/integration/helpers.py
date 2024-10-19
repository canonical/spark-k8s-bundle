# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import logging
import os
import re
import shutil
import subprocess
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Generic, TypeVar
from urllib.parse import urlencode

import boto3
import requests
import yaml
from botocore.exceptions import ClientError, SSLError
from pytest_operator.plugin import OpsTest
from spark8t.domain import ServiceAccount

from spark_test.core.azure_storage import Container
from spark_test.core.s3 import Bucket, Credentials

from .terraform import Terraform

T = TypeVar("T")
S = TypeVar("S")
SECRET_NAME_PREFIX = "integrator-hub-conf-"
COS_ALIAS = "cos"
JMX_EXPORTER_PORT = 9101
JMX_CC_PORT = 9102

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


async def set_azure_credentials(
    ops_test: OpsTest, secret_uri: str, application_name="azure-storage"
) -> Any:
    """Use the charm action to start a password rotation."""

    params = {"credentials": secret_uri}
    await ops_test.model.applications[application_name].set_config(params)


async def get_address(ops_test: OpsTest, app_name, unit_num=0) -> str:
    """Get the address for a unit."""
    status = await ops_test.model.get_status()  # noqa: F821
    address = status["applications"][app_name]["units"][f"{app_name}/{unit_num}"][
        "address"
    ]
    return address


async def get_leader_unit_number(ops_test: OpsTest, application_name: str) -> int:
    """Return the id of the leader unit."""
    leader_unit = None
    for unit in ops_test.model.applications[application_name].units:
        logger.info(unit)
        if await unit.is_leader_from_status():
            unit_name = unit.name
            logger.info(f"Unit name: {unit_name}")
            leader_unit = int(unit_name.split("/")[1])
            logger.info(leader_unit)

    assert leader_unit is not None
    return leader_unit


async def get_kyuubi_credentials(
    ops_test: OpsTest, application_name="kyuubi", num_unit=0
) -> dict[str, str]:
    """Use the charm action to start a password rotation."""

    leader_unit_id = await get_leader_unit_number(ops_test, application_name)
    logger.info(f"Leader unit: {application_name}/{leader_unit_id}")
    action = await ops_test.model.units.get(
        f"{application_name}/{leader_unit_id}"
    ).run_action("get-password")

    results = (await action.wait()).results

    address = await get_address(
        ops_test, app_name=application_name, unit_num=leader_unit_id  # type: ignore
    )

    return {"username": "admin", "password": results["password"], "host": address}


async def fetch_jdbc_endpoint(ops_test):
    """Return the JDBC endpoint for clients to connect to Kyuubi server."""
    logger.info("Running action 'get-jdbc-endpoint' on kyuubi-k8s unit...")
    kyuubi_unit = ops_test.model.applications["kyuubi"].units[0]
    action = await kyuubi_unit.run_action(
        action_name="get-jdbc-endpoint",
    )
    result = await action.wait()

    jdbc_endpoint = result.results.get("endpoint")
    logger.info(f"JDBC endpoint: {jdbc_endpoint}")

    return jdbc_endpoint


async def get_active_kyuubi_servers_list(ops_test: OpsTest) -> list[str]:
    """Return the list of Kyuubi servers that are live in the cluster."""
    jdbc_endpoint = await fetch_jdbc_endpoint(ops_test)
    zookeper_quorum = jdbc_endpoint.split(";")[0].split("//")[-1]

    pod_command = [
        "/opt/kyuubi/bin/kyuubi-ctl",
        "list",
        "server",
        "--zk-quorum",
        zookeper_quorum,
        "--namespace",
        "/kyuubi",
        "--version",
        "1.9.0",
    ]
    kubectl_command = [
        "kubectl",
        "exec",
        "kyuubi-0",
        "-c",
        "kyuubi",
        "-n",
        ops_test.model_name,
        "--",
        *pod_command,
    ]

    process = subprocess.run(kubectl_command, capture_output=True, check=True)
    assert process.returncode == 0

    output_lines = process.stdout.decode().splitlines()
    pattern = r"\?\s+/kyuubi\s+\?\s+(?P<node>[\w\-.]+)\s+\?\s+(?P<port>\d+)\s+\?\s+(?P<version>[\d.]+)\s+\?"
    servers = []

    for line in output_lines:
        match = re.match(pattern, line)
        if not match:
            continue
        servers.append(match.group("node"))

    return servers


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


async def set_memory_constraints(ops_test, model_name):
    """ "Set memory resource constraints on given model."""
    logger.info(f"Setting model constraint mem=500M on model {model_name}...")
    model_constraints_command = [
        "set-model-constraints",
        "--model",
        model_name,
        "mem=500M",
    ]
    retcode, stdout, stderr = await ops_test.juju(*model_constraints_command)
    assert retcode == 0


async def deploy_bundle(ops_test: OpsTest, bundle: Bundle) -> tuple[int, str, str]:
    deploy_command = [
        "deploy",
        "--trust",
        "-m",
        ops_test.model_full_name,
        _local(bundle.main),
    ] + sum([["--overlay", _local(overlay)] for overlay in bundle.overlays], [])

    retcode, stdout, stderr = await ops_test.juju(*deploy_command)

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
        "namespace": ops_test.model_name,  # service_account.namespace,
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

        logger.info(f"bundle_tmp: {bundle_tmp}")
        retcode, stdout, stderr = await deploy_bundle(ops_test, bundle_tmp)

        assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
        logger.info(stdout)

    charms: Bundle[list[str]] = bundle_content.map(
        lambda bundle_data: list(bundle_data["applications"].keys())
    )

    return charms.main + sum(charms.overlays, [])


async def deploy_bundle_yaml_azure_storage(
    bundle: Bundle,
    container: Container,
    cos: str | None,
    ops_test: OpsTest,
) -> list[str]:
    """Deploy the Bundle in YAML format.

    Args:
        bundle: Bundle object
        service_account: Kyuubi service account to be used
        container: Azure Storage container to be used in the deployment
        ops_test: OpsTest class

    Returns:
        list of charms deployed
    """

    data = {
        "namespace": ops_test.model_name,
        "service_account": "kyuubi-test-user",
        "container": container.container_name,
        "storage_account": container.credentials.storage_account,
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

    logger.info(f"tf_vars: {tf_vars}")
    outputs = bundle.apply(tf_vars=tf_vars)

    return list(outputs["charms"]["value"].values())


async def add_juju_secret(
    ops_test: OpsTest, charm_name: str, secret_label: str, data: Dict[str, str]
) -> str:
    """Add a new juju secret."""
    key_values = " ".join([f"{key}={value}" for key, value in data.items()])
    command = f"add-secret {secret_label} {key_values}"
    _, stdout, _ = await ops_test.juju(*command.split())
    secret_uri = stdout.strip()
    command = f"grant-secret {secret_label} {charm_name}"
    _, stdout, _ = await ops_test.juju(*command.split())
    return secret_uri


def construct_azure_resource_uri(container: Container, path: str):
    return os.path.join(
        f"abfss://{container.container_name}@{container.credentials.storage_account}.dfs.core.windows.net",
        path,
    )


async def juju_sleep(ops: OpsTest, time: int, app: str | None = None):
    app_name = app if app else list(ops.model.applications.keys())[0]

    await ops.model.wait_for_idle(
        apps=[app_name],
        idle_period=time,
        timeout=600,
    )


async def get_cos_address(ops_test: OpsTest, cos_model_name: str) -> str:
    """Retrieve the URL where COS services are available."""
    cos_addr_res = subprocess.check_output(
        f"JUJU_MODEL={cos_model_name} juju run traefik/0 show-proxied-endpoints --format json",
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    try:
        cos_addr = json.loads(cos_addr_res)
    except json.JSONDecodeError:
        raise ValueError

    endpoints = cos_addr["traefik/0"]["results"]["proxied-endpoints"]
    return json.loads(endpoints)["traefik"]["url"]


def prometheus_exporter_data(host: str, port: int) -> str | None:
    """Check if a given host has metric service available and it is publishing."""
    url = f"http://{host}:{port}/metrics"
    try:
        response = requests.get(url)
        logger.info(f"Response: {response.text}")
    except requests.exceptions.RequestException:
        return
    if response.status_code == 200:
        return response.text


async def all_prometheus_exporters_data(
    ops_test: OpsTest, check_field, app_name
) -> bool:
    """Check if a all units has metric service available and publishing."""
    result = True
    for unit in ops_test.model.applications[app_name].units:
        unit_name, unit_number = unit.name.split("/")
        unit_ip = await get_address(ops_test, unit_name, int(unit_number))
        result = result and check_field in prometheus_exporter_data(
            unit_ip, JMX_EXPORTER_PORT
        )
    return result


def published_prometheus_data(
    ops_test: OpsTest, cos_model_name: str, host: str, field: str
) -> dict | None:
    """Check the existence of field among Prometheus published data."""
    if "http://" in host:
        host = host.split("//")[1]
    url = f"http://{host}/{cos_model_name}-prometheus-0/api/v1/query?query={field}"
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        return

    if response.status_code == 200:
        return response.json()


async def published_grafana_dashboards(
    ops_test: OpsTest, cos_model_name: str
) -> str | None:
    """Get the list of dashboards published to Grafana."""
    base_url, pw = await get_grafana_access(ops_test, cos_model_name)
    url = f"{base_url}/api/search?query=&starred=false"

    try:
        session = requests.Session()
        session.auth = ("admin", pw)
        response = session.get(url)
    except requests.exceptions.RequestException:
        return
    if response.status_code == 200:
        return response.json()


async def get_grafana_access(ops_test: OpsTest, cos_model_name: str) -> tuple[str, str]:
    """Get Grafana URL and password."""
    grafana_res = subprocess.check_output(
        f"JUJU_MODEL={cos_model_name} juju run grafana/0 get-admin-password --format json",
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    try:
        grafana_data = json.loads(grafana_res)
    except json.JSONDecodeError:
        raise ValueError

    url = grafana_data["grafana/0"]["results"]["url"]
    password = grafana_data["grafana/0"]["results"]["admin-password"]
    return url, password


def published_prometheus_alerts(
    ops_test: OpsTest, cos_model_name: str, host: str
) -> dict | None:
    """Retrieve all Prometheus Alert rules that have been published."""
    if "http://" in host:
        host = host.split("//")[1]
    url = f"http://{host}/{cos_model_name}-prometheus-0/api/v1/rules"
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        return

    if response.status_code == 200:
        return response.json()


async def published_loki_logs(
    ops_test: OpsTest,
    cos_model_name: str,
    host: str,
    field: str,
    value: str,
    limit: int = 300,
) -> str | None:
    """Get the list of dashboards published to Grafana."""
    if "http://" in host:
        host = host.split("//")[1]
    url = f"http://{host}/{cos_model_name}-loki-0/loki/api/v1/query_range"

    try:
        response = requests.get(
            url, params={"query": f'{{{field}=~"{value}"}}', "limit": limit}
        )
    except requests.exceptions.RequestException:
        return {}
    if response.status_code != 200:
        return {}

    json_response = response.json()
    assert json_response["status"] == "success"
    assert len(json_response["data"]["result"]) > 0
    logs = {}
    for chunk in json_response["data"]["result"]:
        log_lines = chunk["values"]
        logs.update({line[0]: line[1] for line in log_lines})
    return logs
