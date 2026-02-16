---
myst:
  html_meta:
    description: "Understand the components of Charmed Apache Spark: spark8t, OCI images, spark-client snap, and Juju charms for Kubernetes deployments."
---

(explanation-component-overview)=
# Components overview

The Charmed Apache Spark solution bundles the following components:

* [spark8t](https://github.com/canonical/spark-k8s-toolkit-py), which is a Python package to enhance
  Apache Spark capabilities allowing to manage Spark jobs and service accounts, with hierarchical
  level of configuration
* [Charmed Apache Spark
  Rock](https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark) OCI-compliant
  Image, that bundles Apache Spark binaries together with Canonical tooling to be used to start your
  Apache Spark workload on Kubernetes, to use Charmed Apache Spark CLI tooling or derive your own
  images from secured and supported bases;
* [Apache Spark Client Snap](https://snapcraft.io/spark-client), to simplify Apache Spark
  installation on edge nodes or local machines, by leveraging on confined
  [snaps](https://snapcraft.io/) and exposing simple Snap commands to run and manage Spark jobs
* [Charmed Bundle](https://charmhub.io/spark-k8s-bundle) to deploy, manage and operate Charmed
  Apache Spark using [Juju](https://juju.is/). This includes:
  * [Spark History Server](https://charmhub.io/spark-history-server-k8s) to expose a web UI for
    analysing the logs of previous Spark jobs
  * [Charmed Apache Kyuubi](https://charmhub.io/kyuubi-k8s) to provide a JDBC/ODBC endpoint for
    running Hive powered by Apache Spark engines
  * [Integration Hub for Apache Spark](https://charmhub.io/spark-integration-hub-k8s) to enable easy
    configuration of Apache Spark service accounts, providing a native Juju integration with [S3
    Integrator](https://charmhub.io/s3-integrator) and [Azure Storage
    Integrator](https://charmhub.io/azure-storage-integrator) for enabling object-storage
    persistence and with the [Canonical Observability Stack (COS)](https://charmhub.io/cos-lite) for
    enabling resource usage monitoring and alerting.

The following image shows how the different artifacts interacts with each other:

```{mermaid}
flowchart TD
    spark8t["`**spark8t** 
    (*python package*)
    exposes functionalities to create, configure and manage Apache Spark users via a Python SDK`"]
    
    spark-rock["`**Charmed Apache Spark Rock** 
    (*OCI Image*)
    provides a reliable Apache Spark image to run Apache Spark applications and Apache Spark CLI tooling`"]

    spark-client["`**Spark Client Snap** 
    (*snap*)
    simplify client integration with an Apache Spark Kubernetes cluster via a snap package to be installed in edge nodes or locally`"]

    spark-k8s-bundle["`**Charmed Apache Spark** 
    (*Charmed Operator*)
    manages the entire lifecycle of Spark jobs`"]

    spark8t --> spark-rock
    spark8t --> spark-client
    spark-rock --> spark-client
    spark-rock --> spark-k8s-bundle
```

The Charmed Apache Spark solution can be used to deploy and manage Apache Spark workloads using the
provided distribution on any conformant Kubernetes (reccomended versions 1.32 and above), like:

* [MicroK8s](https://microk8s.io/), which is the simplest production-grade conformant K8s.
Lightweight and focused. Single command install on Linux, Windows and macOS. See the
[installation guide](https://microk8s.io/#install-microk8s) for more information.
* [Charmed Kubernetes](https://ubuntu.com/kubernetes/charmed-k8s), which is a platform independent,
  model-driven distribution of Kubernetes powered by [Juju](https://juju.is/)
* [AWK EKS](https://ubuntu.com/kubernetes/charmed-k8s), which is the managed Kubernetes service
  provided by Amazon Web Services to run Kubernetes in the AWS cloud and on-premises data centers.

Setup instructions are available in the [Tutorial](tutorial-introduction), specifically
the [environment setup](tutorial-1-environment-setup) page.
