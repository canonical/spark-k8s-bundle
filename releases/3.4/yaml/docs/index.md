<!-- markdownlint-disable-next-line -->
(index)=

# Charmed Apache Spark K8s documentation

Charmed Apache Spark solution is a set of Canonical supported artefacts (including charms, rocks and
snaps) that make operating Apache Spark workloads on Kubernetes seamless, secure and
production-ready. This solution includes the Charmed Apache Spark bundle as well as [Client tools
snap for Apache Spark](https://snapcraft.io/spark-client) and
[spark8t](https://github.com/canonical/spark-k8s-toolkit-py). For more information on the contents
of the Charmed Apache Spark bundle and Charmed Apache Spark solution, see the [Components
explanation](/explanation/component-overview) page.

Apache Spark is a free, open-source software project by the Apache Software Foundation. Users can
find out more at the [Apache Spark project page](https://spark.apache.org).

The solution helps to simplify user interaction with Apache Spark applications and the underlying
Kubernetes cluster whilst retaining the traditional semantics and command line tooling that users
already know. Operators benefit from straightforward, automated deployment of Apache Spark
components (e.g. Spark History Server) to the Kubernetes cluster, using [Juju](https://juju.is/).

Deploying Apache Spark applications to Kubernetes has several benefits over other cluster resource
managers such as Apache YARN, as it greatly simplifies deployment, operation, authentication while
allowing for flexibility and scaling. However, it requires knowledge on Kubernetes, networking and
coordination between the different components of the Apache Spark ecosystem in order to provide a
scalable, secure and production-ready environment. As a consequence, this can significantly increase
complexity for the end user and administrators, as a number of parameters need to be configured and
prerequisites must be met for the application to deploy correctly or for using the Spark CLI
interface (e.g. `pyspark` and `spark-shell`).

Charmed Apache Spark helps to address these usability concerns and provides a
consistent management
interface for operations engineers and cluster administrators who need to manage enablers like Spark
History Server.

## In this documentation

| | |
|--|--|
| [Tutorials](/tutorial/introduction)</br>  Get started - a hands-on introduction to using Charmed Apache Spark operator for new users </br> | [How-to guides](/how-to/deploy/set-up-the-environment) </br> Step-by-step guides covering key operations and common tasks |
| [Reference](/reference/requirements) </br> Technical information - specifications, APIs, architecture | [Explanation](/explanation/component-overview) </br> Concepts - discussion and clarification of key topics |

## Project and community

Charmed Apache Spark is a distribution of Apache Spark. It’s an open-source project that welcomes
community contributions, suggestions, fixes and constructive feedback.

- [Read our Code of Conduct](https://ubuntu.com/community/code-of-conduct)
- [Join the Discourse forum](https://discourse.charmhub.io/tag/spark)
- [Contribute and report bugs](https://github.com/canonical/spark-client-snap)

```{toctree}
:titlesonly:
:hidden:

Home <self>
Tutorial <tutorial/index>
how-to/index
reference/index
explanation/index
```
