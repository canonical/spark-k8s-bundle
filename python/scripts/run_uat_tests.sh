#!/bin/bash
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

set -euo pipefail

TESTS_PATH="${1:-tests/integration}"
if [ "$#" -gt 0 ]; then
	shift
fi
POSARGS="$*"

UUID=$(uuidgen)
PYTEST_BASE_ARGS="-vv --tb native --log-cli-level=INFO -s -x"
COMMON_UAT_ARGS="--keep-models --model test-uat --cos-model cos"

echo "Using UUID: ${UUID}"

# Run simple tests to make sure backend works and to clean up if needed
echo "[1/6] Running test_object_storage.py..."
poetry run pytest $PYTEST_BASE_ARGS "${TESTS_PATH}/test_object_storage.py" $POSARGS --uuid "${UUID}"

# Sometimes deleting resources on the clouds may take some time
sleep 60

# The first tests deploy the bundle
echo "[2/6] Running test_bundle.py..."
poetry run pytest $PYTEST_BASE_ARGS "${TESTS_PATH}/test_bundle.py" $COMMON_UAT_ARGS $POSARGS --uuid "${UUID}"

# Next we only use --no-deploy flag
echo "[3/6] Running test_kyuubi.py..."
poetry run pytest $PYTEST_BASE_ARGS "${TESTS_PATH}/test_kyuubi.py" --no-deploy $COMMON_UAT_ARGS $POSARGS --uuid "${UUID}"

echo "[4/6] Running test_spark_job.py..."
poetry run pytest $PYTEST_BASE_ARGS "${TESTS_PATH}/test_spark_job.py" --no-deploy $COMMON_UAT_ARGS $POSARGS --uuid "${UUID}"

# Re-run the last tests to make sure that the tests are idempotent
echo "[5/6] Running test_kyuubi.py..."
poetry run pytest $PYTEST_BASE_ARGS "${TESTS_PATH}/test_kyuubi.py" --no-deploy $COMMON_UAT_ARGS $POSARGS --uuid "${UUID}"

echo "[6/6] Running test_spark_job.py..."
poetry run pytest $PYTEST_BASE_ARGS "${TESTS_PATH}/test_spark_job.py" --no-deploy --model test-uat --cos-model cos $POSARGS --uuid "${UUID}"

echo "UAT test sequence completed successfully!"
