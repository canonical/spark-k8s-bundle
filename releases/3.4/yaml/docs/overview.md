# Charmed Spark Documentation

Charmed Spark solution is a set of Canonical supported artefacts (including charms, rocks and snaps) that make operating Spark workloads on Kubernetes seamless, secure and production-ready. This solution includes the Charmed Spark bundle as well as [Spark Client Snap](https://snapcraft.io/spark-client) and [spark8t](https://github.com/canonical/spark-k8s-toolkit-py). For more information on the contents of the Charmed Spark bundle and Charmed Spark solution, see the [Components explanation](/t/charmed-spark-documentation-explanation-components/11685) page.

Apache Spark is a free, open-source software project by the Apache Software Foundation. Users can find out more at the [Spark project page](https://spark.apache.org).

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
| 2     | h-setup-k8s                    | [Setup the Environment](/t/charmed-spark-k8s-documentation-how-to-setup-k8s-environment/11618)                                                 |
| 2     | h-deploy                       | [Deploy Charmed Spark](/t/charmed-spark-k8s-documentation-how-to-deploy-charmed-spark/10979)                                                   |
| 2     | h-manage-service-accounts      | [Manage Service Accounts using the snap](/t/spark-client-snap-how-to-manage-spark-accounts/8959)                                               |
| 2     | h-use-spark-client-from-python | [Manage Service Accounts using Python](/t/spark-client-snap-how-to-python-api/8958)                                                            |
| 2     | h-use-integration-hub          | [Manage Service Accounts using Integration Hub](/t/charmed-spark-k8s-documentation-how-to-use-spark-integration-hub/14296)                     |
| 2     | h-spark-monitoring             | [Enable and Configure Monitoring](/t/charmed-spark-k8s-documentation-enable-monitoring/13063)                                                  |
| 2     | h-expose-history-server        | [Expose History Server using Ingress](/t/charmed-spark-k8s-documentation-how-to-expose-history-server/14297)                                   |
| 2     | h-history-server-authorization | [Enable Authorization History Server](/t/charmed-spark-k8s-documentation-how-to-enable-authentication-on-the-spark-history-server-charm/13563) |
| 2     | h-run-on-k8s-pod               | [Use K8s pods to run Charmed Spark](/t/spark-client-snap-how-to-run-on-k8s-in-a-pod/8961)                                                      |
| 2     | h-spark-streaming              | [Run Spark Streaming Jobs](/t/charmed-spark-how-to-run-a-spark-streaming-job/10880)                                                            |
| 2     | h-spark-gpu             | [Run Spark with GPU enabled](/t/charmed-spark-k8s-documentation-enabling-gpu-acceleration-with-charmed-spark/14896)   |
| 2     | h-spark-cert             | [Manage self-signed certificates](/t/charmed-spark-k8s-documentation-using-self-signed-certificates/14898)                                                  |
| 1     | reference                      | [Reference]()                                                                                                                                  |
| 2     | r-requirements                 | [Requirements](/t/spark-client-snap-reference-requirements/8962)                                                                               |
| 2     | r-contacts                     | [Contacts](/t/charmed-spark-k8s-documentation-reference-contacts/14298)                                                                        |
| 1     | explanation                    | [Explanation]()                                                                                                                                |
| 2     | e-component-overview           | [Component Overview](/t/charmed-spark-documentation-explanation-components/11685)                                                              |
| 2     | e-configuration                | [Charmed Spark Hierarchical Configuration](/t/spark-client-snap-explanation-hierarchical-configuration-handling/8956)                          |
| 2     | e-monitoring                   | [Charmed Spark Monitoring](/t/charmed-spark-documentation-explanation-monitoring/14299)                                                        |

# Redirects

[details=Mapping table]
| Path | Location |
| ---- | -------- |
[/details]
