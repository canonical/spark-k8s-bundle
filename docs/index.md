---
myst:
  html_meta:
    description: "Comprehensive documentation for Charmed Apache Spark on Kubernetes with deployment guides, tutorials, and security best practices."
---

(index)=
# Charmed Apache Spark documentation

Charmed Apache Spark solution is a set of Canonical supported artefacts (including charms, rocks and
snaps) that makes operating Apache Spark workloads on Kubernetes seamless, secure and
production-ready.

Charmed Apache Spark solution includes the:

* Charmed operators to deploy and manage Apache Spark-related components, such as [Apache Kyuubi](https://charmhub.io/kyuubi-k8s) and [Spark History Server](https://charmhub.io/spark-history-server-k8s), using [Juju](https://canonical.com/juju)
* [OCI Images](https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark) that benefit from security patching and bug fixing support to run Apache Spark securely 
* Client tools, either in the form of a [snap](https://snapcraft.io/spark-client) or [python package](https://github.com/canonical/spark-k8s-toolkit-py) to simplify the user experience of running Apache Spark on K8s

For an overview of all components in the solution, see the
[Components overview page](explanation-component-overview).

[Apache Spark](https://spark.apache.org) is a free, open-source software project by the Apache Software Foundation.

The solution helps ops teams and administrators automate Apache Spark operations from
[Day 0 to Day 2](https://codilime.com/blog/day-0-day-1-day-2-the-software-lifecycle-in-the-cloud-age/)
with additional capabilities, such as: user management, encryption, password rotation,
easy-to-use application integration, and monitoring.

## In this documentation

| | |
|--|--|
| **Tutorial** | [Introduction](tutorial-introduction) • [Step 1: Environment setup](tutorial-1-environment-setup) |
| **Deployment** | [Environment setup](how-to-deploy-environment) • [Charmed Apache Spark](how-to-deploy-spark) • [Charmed Apache Kyuubi](how-to-deploy-kyuubi) • [Requirements](reference-requirements) |
| **Service account management** | [Integration hub](how-to-service-accounts-integration-hub) • [Python](how-to-service-accounts-python) • [Spark-client](how-to-service-accounts-spark-client) |
| **Operations** | [Monitoring](how-to-monitoring) • Spark History Server: [Auth](how-to-spark-history-server-auth) and [web GUI](how-to-spark-history-server-expose-web-gui) • [Use K8s pods](how-to-use-k8s-pods) • [Streaming jobs](how-to-streaming-jobs) • [Use GPUs](how-to-use-gpu) |
| **Apache Kyuubi** | [External connections](how-to-apache-kyuubi-external-connections) • [Integrate](how-to-apache-kyuubi-integrate-with-applications) • [Metastore](how-to-apache-kyuubi-external-metastore) • [Backups](how-to-apache-kyuubi-back-up-and-restore) • [Upgrades](how-to-apache-kyuubi-upgrade) • [GPU support](how-to-apache-kyuubi-gpu) |
| **Security** | [Overview](explanation-security) • [Enable encryption (Apache Kyuubi)](how-to-apache-kyuubi-encryption-and-passwords) • [Cryptography](explanation-cryptography) • [Self-signed certificates](how-to-self-signed-certificates) |

## How the documentation is organised

[Tutorial](tutorial-introduction): For new users needing to learn how to use Charmed Apache Kafka <br>
[How-to guides](how-to-index): For users needing step-by-step instructions to achieve a practical goal <br>
[Reference](reference-index): For precise, theoretical, factual information to be used while working with the charm <br>
[Explanation](explanation-index): For deeper understanding of key Charmed Apache Kafka concepts <br>

## Project and community

Charmed Apache Spark is a distribution of Apache Spark. It’s an open-source project that welcomes community contributions, suggestions, fixes and constructive feedback.  

- [Read our Code of Conduct](https://ubuntu.com/community/code-of-conduct)  
- [Join the Discourse forum](https://discourse.charmhub.io/tag/spark)  
- [Contribute](https://github.com/canonical/spark-k8s-bundle) and report [issues](https://github.com/canonical/spark-k8s-bundle/issues/new)  
- Explore [Canonical Data Fabric solutions](https://canonical.com/data)  
- [Contact us](https://discourse.charmhub.io/t/13107) for all further questions  

Apache®, Apache Spark, Spark®, and the Apache Spark logo are either registered trademarks or trademarks of the Apache Software Foundation in the United States and/or other countries.  

## License and trademarks

Apache®, [Apache Spark, Spark™](https://spark.apache.org/), [Apache Kyuubi, Kyuubi™](https://kyuubi.apache.org/), and their respective logos are either registered trademarks or trademarks of the [Apache Software Foundation](https://www.apache.org/) in the United States and/or other countries.

The Charmed Apache Spark solution is free software, distributed under the Apache Software License, version 2.0. See [LICENSE](https://github.com/canonical/spark-k8s-bundle/blob/main/LICENSE) for more information.

```{toctree}
:titlesonly:
:hidden:

Overview <self>
Tutorial <tutorial/index>
How To <how-to/index>
Reference <reference/index>
Explanation <explanation/index>
```
