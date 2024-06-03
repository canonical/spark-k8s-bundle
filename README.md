# Charmed Spark K8s Bundle

This repository contains relevant artifacts for deploying and testing Charmed Spark bundle. In particular:

* [python](./python) contains the `spark-test` package that provides some utilities and fixtures to easily implement Charmed Spark tests. Find more information [here](./python/README.md)
* [releases](./releases) contains the artifacts for the different channels, supporting the following backends:
  * [yaml](./releases/3.4/yaml) using Juju YAML bundles to easily deploy Charmed Spark on K8s
  * [terraform](releases/3.4/terraform) using Terraforms scripts to deploy Charmed Spark using the Juju Terraform provider

The Charmed Spark K8s bundle is also available on [Charmhub](https://charmhub.io/spark-k8s-bundle).

## Contributing

Canonical welcomes contributions to the `spark8t` toolkit. Please check out our [guidelines](python/CONTRIBUTING.md) if you're interested in contributing to the solution. Also, if you truly enjoy working on open-source projects like this one and you would like to be part of the OSS revolution, please don't forget to check out the [open positions](https://canonical.com/careers/all) we have at [Canonical](https://canonical.com/).  

## License
The `spark-test` toolkit is free software, distributed under the Apache Software License, version 2.0. See LICENSE for more information.

See [LICENSE](LICENSE) for more information.
