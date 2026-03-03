---
myst:
  html_meta:
    description: "How-to guide for scheduling Spark jobs on dedicated worker pools."
---

(how-to-advanced-scheduling-jobs)=

# Advanced scheduling of Spark jobs

Charmed Apache Spark can be configured to schedule driver and executor pod on specific nodes.
This guide details how to set up and configure the advanced scheduling of Spark jobs to mutually segregate control-plane workloads from user workloads and allocate pods on mixed architectures clusters.

## Prerequisites

This section assumes that Charmed Apache Spark is deployed on a multi-nodes Kubernetes cluster.
Advanced scheduling is achieved using [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector), [Affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) and [Taints](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/).

`nodeSelector` and affinities are notably applied to Kubernetes labels and taints are applied to the nodes themselves.

You may apply a label to a node using the following command:

```shell
kubectl label nodes <node_name> <key>=<value>
```

You may apply a taint to a node using the following:

```shell
kubectl taint nodes <node_name> <key>=<value>:<effect>
```

You may use `kubectl describe node <node_name>` to verify that taints and labels were properly applied to the node.

This guide will demonstrate how to allow pod to be scheduled on tainted nodes and how to assign them to those nodes, ensuring that Spark pods:

- are scheduled on the "worker" nodes
- are the only pods being scheduled there (unless another resource use the same toleration)

## Deploy the Namespace Node Affinity Operator (recommended)

We can deploy the [Namespace Node Affinity Operator](https://github.com/canonical/namespace-node-affinity-operator) charm in the Juju model dedicated to running Charmed Apache Spark components.
To do so, run the following command:

```shell
juju deploy -m <charm_spark_juju_model> namespace-node-affinity --trust
```

By default, the WebHook is not configured to modify pods in any namespace.
First, you must label all namespaces that will contain the pods you want to change the affinities/tolerations using:

```shell
kubectl label ns <namespace_1> namespace-node-affinity=enabled
```

Repeat for all namespaces which will contain user-driven Spark service accounts.

```{note}
Note that those namespaces need to exist before you label them.
```

Then, you must also pass the WebHook configuration to be applied to the pods.
The example below will apply a `nodeSelector` to the pods in the namespace to assign them to a node with the matching label and a toleration to allow them to run on said tainted node.

```yaml
<namespace_1>: |
  nodeSelectorTerms:
    - matchExpressions:
      - key: <label_key>
        operator: In
        values:
        - <label_value>
  tolerations:
  - key: <taint_key>
    operator: Equal
    value: <taint_value>
    effect: <taint_effect>
```

You may save this file under `namespaces_settings.yaml` and configure the charm using:

```shell
juju config namespace-node-affinity settings_yaml="$(<namespaces_settings.yaml)"
```

This is it, you may now run a Spark job and see that the driver and executor pods are scheduled on the node(s) with the matching label, while the taint prevents other workloads to be scheduled there.
You can verify that the Spark job pods are scheduled on the right node(s) by running:

```shell
kubectl get pods -n <namespace_1> -o wide
```

The node running the pod is displayed under the `Node` column.

This setup presented above can also be used for a mixed-architectures cluster, as the node's architecture is provided by a label.
To restrict Spark jobs running in `namespace_1` to `arm64` nodes, use the following `nodeSelector` configuration:

```yaml
<namespace_1>: |
  nodeSelectorTerms:
    - matchExpressions:
      - key: kubernetes.io/arch
        operator: In
        values:
        - arm64
```

```{note}
Charmed Apache Spark provides multi-arch rock images supporting amd64 and arm64.
```

## Define a Pod template accessible from the spark-submit command (alternative)

While we recommend using Namespace Node Affinity Operator for common scenarios, one downside is that it cannot discriminate between driver and executor pods, should they have different hardware needs or resource quotas.
[Enabling GPU acceleration](how-to-use-gpu) presented such a case, where we do not want to assign costly resources to driver pods if they do not need it.

The example below is the equivalent of the first `namespaces_settings.yaml` presented in the previous section, as :

```yaml
apiVersion: v1
kind: Pod
spec:
  nodeSelector:
    <label_key>: <label_value>
  tolerations:
    - effect: <taint_effect>
      key: <taint_key>
      operator: Equal
      value: <taint_value>
```

You may save this file under `pod_template.yaml` and apply it to a Spark job using the `spark-client` snap:

```shell
spark-client.spark-submit \
    --username <service_account> --namespace <namespace> \
    --conf spark.kubernetes.driver.podTemplateFile=pod_template.yaml \
    --conf spark.kubernetes.executor.podTemplateFile=pod_template.yaml \
    ...
```

You may omit one of the two properties, or point to a different file to schedule driver and executors pods differently.

```{note}
Please note that the template files must be accessible from the 'spark-submit' command, **not** from where the pods are actually running.
```

Pod templates can also be used to schedule pods on specific architecture.
The example below will schedule the driver and/or executors pods (depending on the Spark property used) only on `arm64` nodes.

```yaml
apiVersion: v1
kind: Pod
spec:
  nodeSelector:
    kubernetes.io/arch: arm64
```
