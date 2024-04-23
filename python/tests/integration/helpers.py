from typing import Any

from pytest_operator.plugin import OpsTest

from spark_test.core.s3 import Credentials


async def set_s3_credentials(
        ops_test: OpsTest, credentials: Credentials,
        application_name="s3", num_unit=0
) -> Any:
    """Use the charm action to start a password rotation."""
    params = {
        "access-key": credentials.access_key,
        "secret-key": credentials.secret_key
    }

    action = await ops_test.model.units.get(f"{application_name}/{num_unit}")\
        .run_action("sync-s3-credentials", **params)

    return await action.wait()
