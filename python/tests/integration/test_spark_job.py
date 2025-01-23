import asyncio
import json
import logging
import time
import urllib.request

import pytest
from pytest_operator.plugin import OpsTest
from spark8t.domain import PropertyFile
from tenacity import Retrying, stop_after_attempt, wait_fixed

from spark_test.fixtures.k8s import envs, interface, kubeconfig
from spark_test.fixtures.pod import Pod, pod
from spark_test.fixtures.service_account import (
    registry,
    service_account,
    small_profile_properties,
)
from spark_test.utils import get_spark_drivers

from .helpers import (
    all_prometheus_exporters_data,
    assert_logs,
    get_cos_address,
    get_secret_data,
    juju_sleep,
    published_grafana_dashboards,
    published_loki_logs,
    published_prometheus_alerts,
    published_prometheus_data,
)

logger = logging.getLogger(__name__)

COS_ALIAS = "cos"
HISTORY_SERVER = "history-server"
PUSHGATEWAY = "pushgateway"
PROMETHEUS = "prometheus"
LOKI = "loki"


@pytest.mark.skip_if_deployed
@pytest.mark.abort_on_fail
async def test_deploy_bundle(ops_test: OpsTest, spark_bundle):
    await spark_bundle
    await asyncio.sleep(0)  # do nothing, await deploy_cluster


@pytest.mark.abort_on_fail
async def test_active_status(ops_test):
    """Test whether the bundle has deployed successfully."""
    for app_name in ops_test.model.applications:
        assert ops_test.model.applications[app_name].status == "active"


@pytest.fixture
def spark_properties(small_profile_properties, image_properties):
    return small_profile_properties + image_properties


@pytest.fixture(scope="module")
def tmp_folder(tmp_path_factory):
    return tmp_path_factory.mktemp("data")


@pytest.mark.abort_on_fail
async def test_run_job(
    ops_test: OpsTest,
    registry,
    service_account,
    pod,
    credentials,
    object_storage,
    spark_properties,
    tmp_folder,
):
    """Run a spark job."""

    # upload data
    object_storage.upload_file("tests/integration/resources/example.txt")

    # upload script
    object_storage.upload_file("tests/integration/resources/spark_test.py")

    registry.set_configurations(service_account.id, spark_properties)

    initial_driver_pods = set(
        pod.pod_name
        for pod in get_spark_drivers(
            registry.kube_interface.client, service_account.namespace
        )
    )

    pod.exec(
        [
            "spark-client.spark-submit",
            "--username",
            service_account.name,
            "--namespace",
            service_account.namespace,
            "-v",
            object_storage.get_uri("spark_test.py"),
            f"-f {object_storage.get_uri('spark_test.py')}",
        ]
    )

    driver_pods = get_spark_drivers(
        registry.kube_interface.client, service_account.namespace
    )
    assert len(driver_pods) == len(initial_driver_pods) + 1

    driver_pod = [pod for pod in driver_pods if pod.pod_name not in initial_driver_pods]

    assert len(driver_pod) == 1

    logger.info(f"Driver pod: {driver_pod[0].pod_name}")
    logger.info("\n".join(driver_pod[0].logs()))

    line_check = filter(lambda line: "Number of lines" in line, driver_pod[0].logs())

    assert next(line_check)

    # write out spark_job_id to be used elsewhere
    driver_pod[0].write(tmp_folder / "spark-job-driver.json")


@pytest.mark.abort_on_fail
async def test_job_logs_are_persisted(
    ops_test: OpsTest,
    registry,
    service_account,
    credentials,
    object_storage,
    tmp_folder,
):

    driver_pod = Pod.load(tmp_folder / "spark-job-driver.json")

    # Test that logs are persisted in S3
    integration_hub_conf = get_secret_data(
        service_account.namespace, service_account.name
    )
    logger.info(f"Integration Hub confs: {integration_hub_conf}")

    confs = registry.get(service_account.id).configurations
    logger.info(f"Configurations: {confs.props}")
    log_folder = confs.props["spark.eventLog.dir"]

    logger.info(f"Log folder: {log_folder}")
    logger.info(f"Objects: {object_storage.list_content()}")

    logger.info(f"metadata: {driver_pod.metadata}")

    spark_app_selector = driver_pod.labels["spark-app-selector"]

    logs_discovered = False
    for obj in object_storage.list_content():
        if spark_app_selector in obj:
            logs_discovered = True

    assert logs_discovered


@pytest.mark.abort_on_fail
async def test_job_in_history_server(ops_test: OpsTest, tmp_folder):
    driver_pod = Pod.load(tmp_folder / "spark-job-driver.json")

    # check that spark-history server contains the application entry
    status = await ops_test.model.get_status()

    address = status["applications"][HISTORY_SERVER]["units"][f"{HISTORY_SERVER}/0"][
        "address"
    ]

    show_unit_cmd = ["show-unit", f"{HISTORY_SERVER}/0"]

    _, stdout, _ = await ops_test.juju(*show_unit_cmd)

    logger.info(f"Show unit: {stdout}")

    spark_id = driver_pod.labels["spark-app-selector"]
    logger.info(f"Spark ID: {spark_id}")

    for i in range(0, 5):
        try:
            logger.info(f"try n#{i} time: {time.time()}")
            raw_apps = json.loads(
                urllib.request.urlopen(
                    f"http://{address}:18080/api/v1/applications"
                ).read()
            )

            apps = [app for app in raw_apps if app["id"] == spark_id]
        except Exception:
            apps = []

        if len(apps) > 0:
            break
        else:
            await juju_sleep(ops_test, 30, HISTORY_SERVER)  # type: ignore

    logger.info(f"Number of apps: {len(apps)}")

    assert len(apps) == 1


@pytest.mark.abort_on_fail
async def test_job_in_prometheus_pushgateway(ops_test: OpsTest, cos):
    async for cos_model_name in cos:
        if not cos_model_name:
            pytest.skip("Not possible to test without cos")
        # check that logs are sent to prometheus pushgateway

        show_status_cmd = ["status"]

        _, stdout, _ = await ops_test.juju(*show_status_cmd)

        logger.info(f"Show status: {stdout}")

        status = await ops_test.model.get_status()
        pushgateway_address = status["applications"][PUSHGATEWAY]["units"][
            f"{PUSHGATEWAY}/0"
        ]["address"]

        for i in range(0, 5):
            try:
                logger.info(f"try n#{i} time: {time.time()}")

                metrics = json.loads(
                    urllib.request.urlopen(
                        f"http://{pushgateway_address}:9091/api/v1/metrics"
                    ).read()
                )
            except Exception:
                break
            if "data" in metrics and len(metrics["data"]) > 0:
                break
            else:
                await juju_sleep(ops_test, 30, HISTORY_SERVER)  # type: ignore

        assert len(metrics["data"]) > 0


@pytest.mark.abort_on_fail
async def test_spark_metrics_in_prometheus(
    ops_test: OpsTest, registry, service_account, cos, tmp_folder
):
    async for cos_model_name in cos:

        if not cos_model_name:
            pytest.skip("Not possible to test without cos")

        driver_pod = Pod.load(tmp_folder / "spark-job-driver.json")

        show_status_cmd = ["status"]

        _, stdout, _ = await ops_test.juju(*show_status_cmd)

        logger.info(f"Show status: {stdout}")
        with ops_test.model_context(COS_ALIAS) as cos_model:
            status = await cos_model.get_status()
            prometheus_address = status["applications"][PROMETHEUS]["units"][
                f"{PROMETHEUS}/0"
            ]["address"]

            query = json.loads(
                urllib.request.urlopen(
                    f"http://{prometheus_address}:9090/api/v1/query?query=push_time_seconds"
                ).read()
            )

            logger.info(f"query: {query}")
            spark_ids = [
                result["metric"]["exported_job"] for result in query["data"]["result"]
            ]
            logger.info(f"Spark ids: {spark_ids}")

            assert driver_pod.labels["spark-app-selector"] in spark_ids


@pytest.mark.abort_on_fail
async def test_spark_logforwaring_to_loki(
    ops_test: OpsTest, registry, service_account, cos
):
    async for cos_model_name in cos:
        if not cos_model_name:
            pytest.skip("Not possible to test without cos")

        _, stdout, _ = await ops_test.juju("status")

        logger.info(f"Show status: {stdout}")
        with ops_test.model_context(COS_ALIAS) as cos_model:
            status = await cos_model.get_status()
            loki_address = status["applications"][LOKI]["units"][f"{LOKI}/0"]["address"]
            assert_logs(loki_address)


@pytest.mark.abort_on_fail
async def test_history_server_metrics_in_cos(ops_test: OpsTest, cos):
    async for cos_model_name in cos:

        if not cos_model_name:
            pytest.skip("Not possible to test without cos")

        # Prometheus data is being published by the app
        assert await all_prometheus_exporters_data(
            ops_test, check_field="jmx_scrape_duration_seconds", app_name=HISTORY_SERVER
        )

        # We should leave time for Prometheus data to be published
        for attempt in Retrying(stop=stop_after_attempt(5), wait=wait_fixed(30)):
            with attempt:

                cos_address = await get_cos_address(
                    ops_test, cos_model_name=cos_model_name
                )
                assert published_prometheus_data(
                    ops_test, cos_model_name, cos_address, "jmx_scrape_duration_seconds"
                )

                # Alerts got published to Prometheus
                alerts_data = published_prometheus_alerts(
                    ops_test, cos_model_name, cos_address
                )
                logger.info(f"Alerts data: {alerts_data}")

                logger.info("Rules: ")
                for group in alerts_data["data"]["groups"]:
                    for rule in group["rules"]:
                        logger.info(f"Rule: {rule['name']}")
                logger.info("End of rules.")

                for alert in [
                    "Spark History Server Missing",
                    "Spark History Server Threads Dead Locked",
                ]:
                    assert any(
                        rule["name"] == alert
                        for group in alerts_data["data"]["groups"]
                        for rule in group["rules"]
                    )

                # Grafana dashboard got published
                dashboards_info = await published_grafana_dashboards(
                    ops_test, cos_model_name
                )
                logger.info(f"Dashboard info {dashboards_info}")
                assert any(
                    board["title"] == "Spark History Server JMX Dashboard"
                    for board in dashboards_info
                )

                # Loki logs are ingested
                logs = await published_loki_logs(
                    ops_test,
                    cos_model_name,
                    cos_address,
                    "juju_application",
                    HISTORY_SERVER,
                )
                logger.info(f"Retrieved logs: {logs}")

                # check for non empty logs
                assert len(logs) > 0
                # check if startup messages are there
                c = 0
                for timestamp, message in logs.items():
                    if "INFO FsHistoryProvider" in message:
                        c = c + 1
                logger.info(f"Number of line found: {c}")
                assert c > 0
