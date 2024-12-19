# Charmed Apache Spark

[![CharmHub Badge](https://charmhub.io/spark-k8s-bundle/badge.svg)](https://charmhub.io/spark-k8s-bundle)
[![Tests](https://github.com/canonical/spark-k8s-bundle/actions/workflows/ci-tests.yaml/badge.svg?branch=main)](https://github.com/canonical/spark-k8s-bundle/actions/workflows/ci-tests.yaml?query=branch%3Amain)
[![Docs](https://github.com/canonical/spark-k8s-bundle/actions/workflows/sync_docs.yaml/badge.svg)](https://github.com/canonical/spark-k8s-bundle/actions/workflows/sync_docs.yaml)
<!-- [![Release](https://github.com/canonical/spark-k8s-bundle/actions/workflows/ci-checks.yaml/badge.svg)](https://github.com/canonical/spark-k8s-bundle/actions/workflows/ci-checks.yaml) -->

Charmed Apache Spark is a solution that makes operating Apache Spark workloads on Kubernetes seamless, secure, and production-ready. This solution includes:

* charmed operators for several components in the Apache Spark ecosystems, bundled together in the Charmed Apache Spark bundle: [Charmcraft](https://charmhub.io/spark-k8s-bundle) | GitHub - this repository
* Client tools snap for Apache Spark: [snapcraft](https://snapcraft.io/spark-client) | [GitHub](https://github.com/canonical/spark-client-snap)
* [spark8t](https://github.com/canonical/spark-k8s-toolkit-py) Python library 

This repository contains relevant artifacts for deploying and testing Charmed Apache Spark:

* [python](./python) — contains the `spark-test` package that provides  utilities and fixtures to easily implement Charmed Apache Spark tests. Find more information in its [readme file](./python/README.md)
* [releases](./releases) — contains the artifacts for the different channels, supporting the following backends:
  * [yaml](./releases/3.4/yaml) — using Juju YAML bundles to easily deploy Charmed Apache Spark on K8s
  * [terraform](releases/3.4/terraform) — using Terraform scripts to deploy Charmed Apache Spark using the [Juju Terraform provider](https://github.com/juju/terraform-provider-juju)

Charmed Apache Spark bundle is also available on [Charmhub](https://charmhub.io/spark-k8s-bundle).

## Requirements

The minimum requirements are as follows:

* 8 GB of HDD.
* 2 CPU threads per host.
* Access to the internet for downloading the [Canonical Apache Spark Image](https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark).
* Access to a Kubernetes cluster, e.g. [MicroK8s](https://microk8s.io/) or [Charmed Kubernetes](https://ubuntu.com/kubernetes/charmed-k8s).

A production-ready solution might require more resources.

<!-- ## Relations -->

## Monitoring

Charmed Apache Spark supports native integration with the Canonical Observability Stack (COS). If you want to enable monitoring on top of Charmed Apache Spark, make sure that you have a Juju model with COS correctly deployed and see the [How to enable monitoring guide](https://charmhub.io/spark-k8s-bundle/docs/h-spark-monitoring). To deploy COS on MicroK8s, follow the [step-by-step tutorial](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s). For more information about Charmed Apache Spark and COS integration, refer to the [COS documentation](https://charmhub.io/topics/canonical-observability-stack) and the [monitoring explanation section](/t/charmed-spark-documentation-explanation-monitoring/14299).

## Security

For information on security features and the use of cryptography, see the [Security explanation](https://charmhub.io/spark-k8s-bundle/docs/e-security) page.

Security issues in the Charmed Apache Spark can be reported through [LaunchPad](https://wiki.ubuntu.com/DebuggingSecurity#How%20to%20File). Please do not file GitHub issues about security issues.

## Contributing

Canonical welcomes contributions to Charmed Apache Spark. Please check out our [contribution guidelines](python/CONTRIBUTING.md) if you're interested in contributing to the solution. If you truly enjoy working on open-source projects like this one and you would like to be part of the OSS revolution, please don't forget to check out the [career opportunities](https://canonical.com/careers/all) we have at [Canonical](https://canonical.com/).  

## License

The Charmed Apache Spark is free software, distributed under the Apache Software License, version 2.0.

See [LICENSE](LICENSE) for more information.
