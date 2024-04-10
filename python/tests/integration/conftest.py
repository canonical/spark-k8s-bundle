import os

import pytest

integration_test_flag = bool(int(os.environ.get("IE_TEST", "0")))


@pytest.fixture
def integration_test():
    if not integration_test_flag:
        pytest.skip(
            reason="Integration test, to be skipped when running unittests",
        )
