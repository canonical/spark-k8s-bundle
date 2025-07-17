# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
from __future__ import annotations

import ast
import json
import logging
import os
import re
import shutil
import subprocess
import textwrap
import urllib.parse
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from random import choices
from string import hexdigits
from typing import Callable, Generic, TypeVar, cast

import httpx
import jinja2
import jubilant
import yaml

from spark_test.core.s3 import Credentials
from tests.integration.types import KyuubiCredentials

T = TypeVar("T")
S = TypeVar("S")
SECRET_NAME_PREFIX = "integrator-hub-conf-"
COS_ALIAS = "cos"
JMX_EXPORTER_PORT = 9101
JMX_CC_PORT = 9102
ZOOKEEPER_PORT = 2181
ZOOKEEPER_NAME = "zookeeper"
HA_ZNODE_NAME = "/kyuubi"

logger = logging.getLogger(__name__)


@dataclass
class Bundle(Generic[T]):
    main: T
    overlays: list[T]

    def map(self, f: Callable[[T], S]) -> "Bundle[S]":
        return Bundle(main=f(self.main), overlays=[f(item) for item in self.overlays])


def set_s3_credentials(
    juju: jubilant.Juju, credentials: Credentials, application_name="s3", num_unit=0
) -> None:
    """Use the charm action to start a password rotation."""
    params = {
        "access-key": credentials.access_key,
        "secret-key": credentials.secret_key,
    }

    task = juju.run(f"{application_name}/{num_unit}", "sync-s3-credentials", params)
    assert task.return_code == 0


def get_kyuubi_credentials(
    juju: jubilant.Juju, data_integrator_unit: str = "data-integrator/0"
) -> KyuubiCredentials:
    """Use the charm action to start a password rotation."""
    task = juju.run(data_integrator_unit, "get-credentials")
    assert task.return_code == 0
    kyuubi_info = task.results["kyuubi"]
    endpoint = kyuubi_info["uris"]
    logger.info(endpoint)

    if (
        host_match := re.match(
            r"^(?:jdbc\:hive2\:\/\/)(?P<host>.*)(?:\:\d+/)$", endpoint
        )
    ) is not None:
        address = host_match.group("host")
    else:
        status = juju.status()
        address = None
        for unit in status.apps["kyuubi"].units.values():
            if unit.leader:
                address = unit.address
        assert address

    return {
        "username": kyuubi_info["username"],
        "password": kyuubi_info["password"],
        "host": address,
    }


def get_zookeeper_quorum(juju: jubilant.Juju, zookeeper_name: str) -> str:
    addresses = []
    status = juju.status()
    for unit in status.apps[zookeeper_name].units.values():
        addresses.append(f"{unit.address}:{ZOOKEEPER_PORT}")
    return ",".join(addresses)


def get_active_kyuubi_servers_list(
    juju: jubilant.Juju, zookeeper_name=ZOOKEEPER_NAME
) -> list[str]:
    """Return the list of Kyuubi servers that are live in the cluster."""
    zookeeper_quorum = get_zookeeper_quorum(juju=juju, zookeeper_name=zookeeper_name)
    logger.info(f"Zookeeper quorum: {zookeeper_quorum}")
    pod_command = [
        "/opt/kyuubi/bin/kyuubi-ctl",
        "list",
        "server",
        "--zk-quorum",
        zookeeper_quorum,
        "--namespace",
        HA_ZNODE_NAME,
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
        cast(str, juju.model),
        "--",
        *pod_command,
    ]

    process = subprocess.run(kubectl_command, capture_output=True, check=True)
    assert process.returncode == 0

    output_lines = process.stdout.decode().splitlines()  
    
    # Pattern that matches lines of the output of kyuubi-ctl list command
    pattern = r"\?\s+/kyuubi\s+\?\s+(?P<node>[\w\-.]+)\s+\?\s+(?P<port>\d+)\s+\?\s+(?P<version>[\w\-.]+)\s+\?"

    # A sample output line is of the following format:
    # ? /kyuubi   ? kyuubi-0.kyuubi-endpoints.spark-bundle-test.svc.cluster.local ? 10009 ? 1.10.2-ubuntu1 ?
    #
    # Regex Explanation: 
    # \?\s+                     mathes a '?' character followed by white spaces
    # /kyuubi                   matches literal "/kyuubi"
    # \s+\?\s+                  matches a '?' character surrounded by white spaces
    # (?P<node>[\w\-.]+)        matches a group of alphanumeric characters including '.' and '-', in this case kyuubi node
    # (?P<port>\d+)             matches one or more digits, in this case kyuubi port
    # (?P<version>[\d.\w\-]+)   matches a group of alphanumeric characters including '.' and '-', in this case kyuubi version
    # \s+\?                     matches a '?' preceded by white spaces
    servers = []

    for line in output_lines:
        match = re.match(pattern, line)
        if not match:
            continue
        servers.append(match.group("node"))

    return servers


def get_postgresql_credentials(
    juju: jubilant.Juju, application_name: str, num_unit=0
) -> dict[str, str]:
    """Return the credentials that can be used to connect to postgresql database."""
    task = juju.run(f"{application_name}/{num_unit}", "get-password")
    assert task.return_code == 0

    results = task.results
    status = juju.status()
    address = (
        status.apps[application_name].units[f"{application_name}/{num_unit}"].address
    )

    return {"username": "operator", "password": results["password"], "host": address}


def render_bundle(bundle, context=None, **kwcontext) -> Path:
    """Render a templated bundle using Jinja2.

    This can be used to populate built charm paths or config values.

    :param bundle (str or Path): Path to bundle file or YAML content.
    :param context (dict): Optional context mapping.
    :param **kwcontext: Additional optional context as keyword args.

    Returns the Path for the rendered bundle.
    Adapted from pytest_operator.
    """
    bundles_dst_dir = Path(".build") / "bundles"
    bundles_dst_dir.mkdir(exist_ok=True, parents=True)
    if context is None:
        context = {}
    context.update(kwcontext)
    if re.search(r".yaml(.j2)?$", str(bundle)):
        bundle_path = Path(bundle)
        bundle_text = bundle_path.read_text()
        if bundle_path.suffix == ".j2":
            bundle_name = bundle_path.stem
        else:
            bundle_name = bundle_path.name
    else:
        bundle_text = textwrap.dedent(bundle).strip()
        infix = "".join(choices(hexdigits, k=4))
        bundle_name = f"spark-{infix}.yaml"
    logger.info(f"Rendering bundle {bundle_name}")
    rendered = jinja2.Template(bundle_text).render(**context)
    dst = bundles_dst_dir / bundle_name
    dst.write_text(rendered)
    return dst


def render_yaml(file: Path, data: dict) -> dict:
    if os.path.splitext(file)[1] == ".j2":
        bundle_file = render_bundle(file, **{str(k): str(v) for k, v in data.items()})
    else:
        bundle_file = file

    return yaml.safe_load(bundle_file.read_text())


def _local(pointer) -> str:
    return (
        f"./{pointer.relative_to(Path.cwd())}"
        if isinstance(pointer, Path)
        else str(pointer)
    )


def deploy_bundle(juju: jubilant.Juju, bundle: Bundle) -> str:
    deploy_command = [
        "deploy",
        "--trust",
        _local(bundle.main),
    ] + sum([["--overlay", _local(overlay)] for overlay in bundle.overlays], [])

    stdout = juju.cli(*deploy_command)

    return stdout


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


def get_cos_address(cos_model_name: str) -> str:
    """Retrieve the URL where COS services are available."""
    # FIXME: once jubilant allows to change models, adapt this
    cos_addr_res = subprocess.check_output(
        f"JUJU_MODEL={cos_model_name} juju run traefik/0 show-proxied-endpoints --format json",
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    try:
        cos_addr = json.loads(cos_addr_res)
    except json.JSONDecodeError as e:
        raise ValueError from e

    endpoints = cos_addr["traefik/0"]["results"]["proxied-endpoints"]
    return json.loads(endpoints)["traefik"]["url"]


def prometheus_exporter_data(host: str, port: int) -> str | None:
    """Check if a given host has metric service available and it is publishing."""
    url = f"http://{host}:{port}/metrics"
    try:
        response = httpx.get(url)
        logger.info(f"Response: {response.text}")
    except httpx.RequestError:
        return
    if response.status_code == 200:
        return response.text


def published_prometheus_data(
    cos_model_name: str, host: str, field: str
) -> dict | None:
    """Check the existence of field among Prometheus published data."""
    if "http://" in host:
        host = host.split("//")[1]
    url = f"http://{host}/{cos_model_name}-prometheus-0/api/v1/query?query={field}"
    try:
        response = httpx.get(url)
    except httpx.RequestError:
        return

    if response.status_code == 200:
        return response.json()


def published_grafana_dashboards(cos_model_name: str) -> dict | None:
    """Get the list of dashboards published to Grafana."""
    base_url, pw = get_grafana_access(cos_model_name)
    url = f"{base_url}/api/search?query=&starred=false"

    try:
        response = httpx.get(url, auth=("admin", pw))
    except httpx.RequestError:
        return
    if response.status_code == 200:
        return response.json()


def get_grafana_access(cos_model_name: str) -> tuple[str, str]:
    """Get Grafana URL and password."""
    grafana_res = subprocess.check_output(
        f"JUJU_MODEL={cos_model_name} juju run grafana/0 get-admin-password --format json",
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    try:
        grafana_data = json.loads(grafana_res)
    except json.JSONDecodeError as e:
        raise ValueError from e

    url = grafana_data["grafana/0"]["results"]["url"]
    password = grafana_data["grafana/0"]["results"]["admin-password"]
    return url, password


def published_prometheus_alerts(cos_model_name: str, host: str) -> dict | None:
    """Retrieve all Prometheus Alert rules that have been published."""
    if "http://" in host:
        host = host.split("//")[1]
    url = f"http://{host}/{cos_model_name}-prometheus-0/api/v1/rules"
    try:
        response = httpx.get(url)
    except httpx.RequestError:
        return

    if response.status_code == 200:
        return response.json()


def published_loki_logs(
    cos_model_name: str,
    host: str,
    field: str,
    value: str,
    limit: int = 300,
) -> dict:
    """Get the list of dashboards published to Grafana."""
    if "http://" in host:
        host = host.split("//")[1]
    url = f"http://{host}/{cos_model_name}-loki-0/loki/api/v1/query_range"

    try:
        response = httpx.get(
            url, params={"query": f'{{{field}=~"{value}"}}', "limit": limit}
        )
    except httpx.RequestError:
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


def assert_logs(loki_address: str) -> None:
    """Check the existence of the logs."""
    log_gl = urllib.parse.quote('{app="spark", pebble_service="sparkd"}')
    query = httpx.get(
        f"http://{loki_address}:3100/loki/api/v1/query_range?query={log_gl}"
    ).json()

    # NOTE: This check depends on previous tests, because without the previous ones
    #       there will be no logs.
    logger.info(f"query: {query}")
    assert len(query["data"]["result"]) != 0, "no logs was found"


def get_kyuubi_ca_cert(
    juju: jubilant.Juju, certificates_app_name: str = "certificates"
) -> str:
    """Get the CA certificate used by Kyuubi"""
    status = juju.status()
    self_signed_certificate_unit = next(
        iter(status.apps[certificates_app_name].units.keys())
    )
    task = juju.run(self_signed_certificate_unit, "get-issued-certificates")
    assert task.return_code == 0
    items = ast.literal_eval(task.results["certificates"])
    certificates = json.loads(items[0])
    ca_cert = certificates["ca"]
    return ca_cert
