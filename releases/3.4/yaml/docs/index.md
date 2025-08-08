# Charmed Apache Spark K8s Documentation

Charmed Apache Spark solution is a set of Canonical supported artefacts (including charms, rocks and snaps) that make operating Apache Spark workloads on Kubernetes seamless, secure and production-ready. This solution includes the Charmed Apache Spark bundle as well as [Client tools snap for Apache Spark](https://snapcraft.io/spark-client) and [spark8t](https://github.com/canonical/spark-k8s-toolkit-py). For more information on the contents of the Charmed Apache Spark bundle and Charmed Apache Spark solution, see the [Components explanation](/t/charmed-spark-documentation-explanation-components/11685) page.

Apache Spark is a free, open-source software project by the Apache Software Foundation. Users can find out more at the [Apache Spark project page](https://spark.apache.org).

The solution helps to simplify user interaction with Apache Spark applications and the underlying Kubernetes cluster whilst retaining the traditional semantics and command line tooling that users already know. Operators benefit from straightforward, automated deployment of Apache Spark components (e.g. Spark History Server) to the Kubernetes cluster, using [Juju](https://juju.is/). 

Deploying Apache Spark applications to Kubernetes has several benefits over other cluster resource managers such as Apache YARN, as it greatly simplifies deployment, operation, authentication while allowing for flexibility and scaling. However, it requires knowledge on Kubernetes, networking and coordination between the different components of the Apache Spark ecosystem in order to provide a scalable, secure and production-ready environment. As a consequence, this can significantly increase complexity for the end user and administrators, as a number of parameters need to be configured and prerequisites must be met for the application to deploy correctly or for using the Spark CLI interface (e.g. pyspark and spark-shell). 

Charmed Apache Spark helps to address these usability concerns and provides a consistent management interface for operations engineers and cluster administrators who need to manage enablers like Spark History Server.

## In this documentation

| | |
|--|--|
|  [Tutorials](/t/13234)</br>  Get started - a hands-on introduction to using Charmed Apache Spark operator for new users </br> |  [How-to guides](/t/11618) </br> Step-by-step guides covering key operations and common tasks |
| [Reference](/t/8962) </br> Technical information - specifications, APIs, architecture | [Explanation](/t/11685) </br> Concepts - discussion and clarification of key topics  |

## Project and community

Charmed Apache Spark is a distribution of Apache Spark. It’s an open-source project that welcomes community contributions, suggestions, fixes and constructive feedback.

- [Read our Code of Conduct](https://ubuntu.com/community/code-of-conduct)
- [Join the Discourse forum](https://discourse.charmhub.io/tag/spark)
- [Contribute and report bugs](https://github.com/canonical/spark-client-snap)

# Contents

1. [Overview](overview.md)
1. [Tutorial](tutorial)
  1. [Introduction](tutorial/t-overview.md)
  1. [1. Environment setup](tutorial/t-setup-environment.md)
  1. [2. Distributed data processing](tutorial/t-data-processing.md)
  1. [3. Data stream processing](tutorial/t-streaming.md)
  1. [4. History Server](tutorial/t-history-server.md)
  1. [5. Monitoring with COS](tutorial/t-cos.md)
  1. [6. Apache Kyuubi](tutorial/t-kyuubi.md)
  1. [7. Wrapping Up](tutorial/t-wrapping-up.md)
1. [How To](how-to)
  1. [Deploy](how-to/h-deploy)
    1. [Set up the environment](how-to/h-deploy/h-setup-k8s.md)
    1. [Deploy Charmed Apache Spark](how-to/h-deploy/h-deploy.md)
    1. [Deploy Charmed Apache Kyuubi](how-to/h-deploy/h-deploy-kyuubi.md)
  1. [Manage service accounts](how-to/h-service-accounts)
    1. [Using spark-client snap](how-to/h-service-accounts/h-manage-service-accounts.md)
    1. [Using Python](how-to/h-service-accounts/h-use-spark-client-from-python.md)
    1. [Using Integration Hub](how-to/h-service-accounts/h-use-integration-hub.md)
  1. [Apache Kyuubi](how-to/h-kyuubi)
    1. [Encryption and passwords](how-to/h-kyuubi/h-kyuubi-encryption.md)
    1. [External connections and metastore](how-to/h-kyuubi/h-kyuubi-connections.md)
    1. [Integrate applications](how-to/h-kyuubi/h-kyuubi-applications.md)
    1. [Upgrade](how-to/h-kyuubi/h-kyuubi-upgrade.md)
  1. [Enable monitoring](how-to/h-spark-monitoring.md)
  1. [Spark History Server](how-to/h-history-server)
    1. [Expose using Ingress](how-to/h-history-server/h-expose-history-server.md)
    1. [Authorization](how-to/h-history-server/h-history-server-authorization.md)
  1. [Use K8s pods](how-to/h-run-on-k8s-pod.md)
  1. [Streaming Jobs](how-to/h-spark-streaming.md)
  1. [Use GPU](how-to/h-spark-gpu.md)
  1. [Self-signed certificates](how-to/h-spark-cert.md)
1. [Reference](reference)
  1. [Releases](reference/r-releases)
    1. [Revision 2](reference/r-releases/r-rev-2.md)
  1. [Requirements](reference/r-requirements.md)
  1. [Contacts](reference/r-contacts.md)
1. [Explanation](explanation)
  1. [Component overview](explanation/e-component-overview.md)
  1. [Security](explanation/e-security.md)
  1. [Cryptography](explanation/e-cryptography.md)
  1. [Configuration](explanation/e-configuration.md)
  1. [Monitoring](explanation/e-monitoring.md)
  1. [Trademarks](explanation/e-trademarks.md)