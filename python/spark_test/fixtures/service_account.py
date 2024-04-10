import pytest
from spark8t.domain import ServiceAccount
from spark8t.services import K8sServiceAccountRegistry


def _clearnup_registry(registry):
    [registry.delete(account.id) for account in registry.all()]


@pytest.fixture
def registry(interface):
    registry = K8sServiceAccountRegistry(interface)
    yield registry
    _clearnup_registry(registry)


@pytest.fixture
def service_account(registry, namespace):
    service_account_name = "spark-test"

    sa = ServiceAccount(
        service_account_name, namespace, registry.kube_interface.api_server
    )

    registry.create(sa)

    yield sa

    registry.delete(sa.id)
