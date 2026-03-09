---
myst:
  html_meta:
    description: "Minimum system requirements for deploying Charmed Apache Spark on Kubernetes including CPU, memory, storage, and network needs."
---

(reference-requirements)=
# Minimum system requirements

The following are the minimum system requirements for Charmed Apache Spark:

- 8GB of storage.
- 2 CPU threads per host.
- Access to the internet for downloading the
  [Canonical Apache Spark image](https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark).
- Access to a Kubernetes cluster, e.g. [MicroK8s](https://microk8s.io/) or
  [Charmed Kubernetes](https://ubuntu.com/kubernetes/charmed-k8s).

## Recommended versions

This section lists the recommended versions for deploying Charmed Apache Spark, plus additional versions validated during testing.

### Kubernetes

We recommend deploying Charmed Apache Spark on a Canonical Kubernetes cluster running version `1.32` LTS.

The following table lists the validated combinations of substrate, architecture, and Kubernetes version:

| K8s Distribution | K8s versions                                     | Architecture | GPU Acceleration |
|------------------|--------------------------------------------------|--------------|------------------|
| Canonical K8s    | `1.32`, `1.33`, `1.34`                           | AMD, ARM     | Yes              |
| MicroK8s         | `1.28`,`1.29`,`1.30`,`1.31`,`1.32`,`1.33`,`1.34` | AMD          | No               |
| Azure AKS        | `1.32`                                           | AMD          | No               |
| Amazon EKS       | `1.32`                                           | AMD          | No               |

```{note}
Others combinations of substrate, architecture, and Kubernetes versions may also work, although they are not continuously validated. To validate an architecture, you can deploy the terraform solutions as suggested in the [How-to deploy guide](/how-to/index), and then run the [Charmed Spark UATs](https://github.com/canonical/spark-k8s-bundle/tree/main/python/tests/integration).
```


### Juju 

We recommend deploying Charmed Apache Spark on Juju `3.6.14`.

```{note}
Juju controller versions from `3.9.10` to `3.6.13` are affected by a [regression in Juju](https://github.com/juju/juju/issues/21312) that has been fixed in `3.6.14`.
Support for Juju `3.6.14+` has been addressed by [this issue](https://github.com/canonical/spark-integration-hub-k8s-operator/issues/119). When using Juju controller versions greater or equal to `3.6.14`, make sure you use a charm revision above `107` for `spark-integration-hub-k8s`. On Juju controller versions lower or equal to `3.6.9`, use charm revisions below `107`.
```

