# Charmed Spark Documentation

Charmed Spark is a set of Canonical supported artifacts (including charms, rocks and SNAPs) that makes operating Spark workloads on Kubernetes seamless, secure and production-ready. 

The solution helps to simplify user interaction with Spark applications and the underlying Kubernetes cluster whilst retaining the traditional semantics and command line tooling that users already know. Operators benefit from straightforward, automated deployment of Spark components (e.g. Spark History Server) to the Kubernetes cluster, using [Juju](https://juju.is/). 

Deploying Spark applications to Kubernetes has several benefits over other cluster resource managers such as Apache YARN, as it greatly simplifies deployment, operation, authentication while allowing for flexibility and scaling. However, it requires knowledge on Kubernetes, networking and coordination between the different components of the Spark ecosystem in order to provide a scalable, secure and production-ready environment. As a consequence, this can significantly increase complexity for the end user and administrators, as a number of parameters need to be configured and prerequisites must be met for the application to deploy correctly or for using the Spark CLI interface (e.g. pyspark and spark-shell). 

Charmed Spark helps to address these usability concerns and provides a consistent management interface for operations engineers and cluster administrators who need to manage enablers like Spark History Server.

## Project and community

Charmed Spark is a distribution of Apache Spark. It’s an open-source project that welcomes community contributions, suggestions, fixes and constructive feedback.
- [Read our Code of Conduct](https://ubuntu.com/community/code-of-conduct)
- [Join the Discourse forum](https://discourse.charmhub.io/tag/spark)
- [Contribute and report bugs](https://github.com/canonical/spark-client-snap)


# Navigation

| Level | Path                           | Navlink                                                                                                                                        |
|-------|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| 1     | overview                       | [Overview](/t/spark-client-snap-documentation/8963)                                                                                            | 
| 1     | tutorial                       | [Tutorial]()                                                                                                                                   |
| 2     | t-overview                     | [1. Introduction](/t/charmed-spark-documentation-tutorial-introduction/13234)                                                                  |
| 2     | t-setup-environment            | [2. Set up the environment for the tutorial](/t/charmed-spark-documentation-tutorial-setup-environment/13233)                                  |
| 2     | t-spark-shell                  | [2. Interacting with Spark using Interactive Shell](/t/charmed-spark-documentation-tutorial-spark-shell/13232)                                 |
| 2     | t-spark-submit                 | [3. Submitting Jobs using Spark Submit](/t/charmed-spark-documentation-tutorial-spark-submit/13231)                                            |
| 2     | t-spark-streaming              | [4. Streaming workloads with Charmed Spark](/t/charmed-spark-documentation-tutorial-streaming/13230)                                           |
| 2     | t-spark-monitoring             | [5. Monitoring the Spark cluster](/t/charmed-spark-documentation-tutorial-monitoring/13225)                                                    |
| 2     | t-wrapping-up                  | [6. Wrapping Up](/t/charmed-spark-documentation-tutorial-wrapping-up/13224)                                                                    |
| 1     | how-to                         | [How To]()                                                                                                                                     |
| 2     | h-setup-k8s                    | [Setup Environment](/t/charmed-spark-k8s-documentation-how-to-setup-k8s-environment/11618)                                                     |
| 2     | h-manage-service-accounts      | [Manage Service Accounts](/t/spark-client-snap-how-to-manage-spark-accounts/8959)                                                              |
| 2     | h-use-spark-client-from-python | [Use the Spark Client Python API](/t/spark-client-snap-how-to-python-api/8958)                                                                 |
| 2     | h-run-on-k8s-pod               | [Run on K8s pods](/t/spark-client-snap-how-to-run-on-k8s-in-a-pod/8961)                                                                        |
| 2     | h-deploy-spark-history         | [Deploy Spark History Server](/t/charmed-spark-k8s-documentation-how-to-deploy-spark-history-server/10979)                                     |
| 2     | h-spark-streaming              | [Run Spark Streaming Jobs](/t/charmed-spark-how-to-run-a-spark-streaming-job/10880)                                                            |
| 2     | h-spark-monitoring             | [Enable monitoring](/t/charmed-spark-k8s-documentation-enable-monitoring/13063)                                                                |
| 2     | h-history-server-authorization | [Enable authorization History Server](/t/charmed-spark-k8s-documentation-how-to-enable-authentication-on-the-spark-history-server-charm/13563) |
| 1     | reference                      | [Reference]()                                                                                                                                  |
| 2     | r-requirements                 | [Requirements](/t/spark-client-snap-reference-requirements/8962)                                                                               |
| 1     | explanation                    | [Explanation]()                                                                                                                                |
| 2     | e-component-overview           | [Component Overview](/t/charmed-spark-documentation-explanation-components/11685)                                                                                                                         |
| 2     | e-configuration                | [Spark Client Hierarchical Configuration](/t/spark-client-snap-explanation-hierarchical-configuration-handling/8956)                           |


# Redirects

[details=Mapping table]
| Path | Location |
| ---- | -------- |
[/details]