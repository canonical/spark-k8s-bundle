# spark-k8s-test

The main purpose of the `spark-k8s-test` library is to provide a seemless, user-friendly interface
to implement tests for Charmed Apache Spark. `spark-k8s-test` provides a number of pytest fixtures 
that allow to create, manage and destroy various kind of resources needed for testing, 
such as:

* K8s resources (e.g. namespaces, pods, service accounts)
* S3 Buckets
* `spark8t` managed service accounts / secrets

Moreover, `spark-k8s-test` provides simple API to run spark-jobs within a Python testing 
environment

## Quick start

### Installation

The package can be simply installed from PyPI using

```commandline
pip install spark-k8s-test 
```

or from the source by cloning this repo and then running:

```commandline
pip install .
```

The package assumes that a MicroK8s installation is present in the system, and 
that the deployment is configured with MinIO to provide object storage capabilities.

You can use the following scripts to setup a MicroK8s deployment along with MinIO:

```bash
./spark_test/resources/bin/microk8s.sh setup

./spark_test/resources/bin/microk8s.sh configure dns rbac minio
```

### Basic Usage

You can simply import the fixtures and use them straight away in your tests:

```python
from spark_test.fixtures.pod import admin_pod
from spark_test.fixtures.service_account import registry, service_account

def test_pod_admin(admin_pod, service_account):

    output: str = admin_pod.exec(
        ["spark-client.service-account-registry", "list"]
    ).decode("utf-8")

    assert output.strip("\n") == service_account.id
```

## Development

For development, we recommend to use [Poetry](https://python-poetry.org/). Once Poetry 
is installed, you can simply setup the project by 

```commandline
poetry install
```

[Tox](https://tox.wiki/) also provide easy short-cut to provide CI/CD capabilities
such as

* Auto-Formatting: `tox -e fmt`
* Linting and Static Typing: `tox -e lint`
* Unittest: `tox -e unittest`
* Integration tests: `tox -e integration`

## User acceptance tests and benchmarks

The tox environments can be run against a live deployment to assert its compliance.
Here is an example running the `benchmarks` environment to stress-test a deployment in a `spark-model` Juju model:
```shell
tox run -e benchmarks -- --backend terraform --backend-storage azure --no-deploy --keep-models --model spark-model
```

## Contributing

Canonical welcomes contributions to the `spark-k8s-test` library. Please check out our [guidelines](./CONTRIBUTING.md) if you're interested in contributing to the solution. Also, if you truly enjoy working on open-source projects like this one and you would like to be part of the OSS revolution, please don't forget to check out the [open positions](https://canonical.com/careers/all) we have at [Canonical](https://canonical.com/).  

## License

The `spark-k8s-test` toolkit is free software, distributed under the Apache Software License, version 2.0. See LICENSE for more information.

See [LICENSE](LICENSE) for more information.
