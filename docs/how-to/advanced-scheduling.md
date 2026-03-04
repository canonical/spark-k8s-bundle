---
myst:
  html_meta:
    description: "How-to guide for scheduling Charmed Apache Spark's components and its jobs on Kubernetes clusters."
---

(how-to-advanced-scheduling)=

# Advanced scheduling

You can optimize infrastructure governance and performance by configuring Charmed Apache Spark with Kubernetes mechanisms, such as node affinity and toleration.

Those mechanisms are used to decouple control plane operations from user-driven workloads, ensuring system services remain stable on cost-effective instance.
Spark executors can benefit from specialized hardware (high-memory nodes, custom hardware resources such as GPU, specific architecture) while maintaining the flexibility to scale idle resources to zero.

## Prerequisites

This section assumes that Charmed Apache Spark is deployed on a multi-nodes Kubernetes cluster.
Advanced scheduling is achieved using [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector), [Affinity](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity) and [Taints](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/).

`nodeSelector` and affinities are notably applied to Kubernetes labels while taints are applied to the nodes themselves.

You may apply a label to a node using the following command:

```shell
kubectl label nodes <node_name> <key>=<value>
```

Tainting a node is achieved using the following:

```shell
kubectl taint nodes <node_name> <key>=<value>:<effect>
```

```{note}
We recommend exclusively using `NoSchedule` effects rather than `NoExecute` to avoid disrupting pre-existing workloads.
```

Finally, you may use

```shell
kubectl describe node <node_name>
```

to verify that taints and labels were properly applied to the node.

This guide will demonstrate how to allow pod to be scheduled on tainted nodes and how to assign them to those nodes, ensuring that Spark pods:

- are scheduled on the nodes dedicated to running user workloads
- are the only pods being scheduled there (unless another resource use the same toleration)

## Scheduling jobs

### Deploying the Namespace Node Affinity Operator (recommended)

Charmed Apache Spark can be configured to schedule driver and executor pod on specific nodes.
This section details how to set up and configure the advanced scheduling of Spark jobs to mutually segregate control-plane workloads from user workloads and allocate pods on mixed architectures clusters.

We can deploy the [Namespace Node Affinity Operator](https://github.com/canonical/namespace-node-affinity-operator) charm in the Juju model dedicated to running Charmed Apache Spark components.
To do so, run the following command:

```shell
juju deploy -m <charmed_spark_juju_model> namespace-node-affinity --trust
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
The example below will apply a `nodeSelector` to the pods in the namespace to assign them to a node with the matching label and a toleration to run on said tainted node.

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
<namespace_2>: |
  ...
```

You may save this file under `namespaces_settings.yaml` and configure the charm using:

```shell
juju config namespace-node-affinity settings_yaml="$(<namespaces_settings.yaml)"
```

This is it, you may now run a Spark job using the `spark-client` and see that the driver and executor pods are scheduled on the node(s) with the matching label, while the taint prevents other workloads from being scheduled there.

```shell
spark-client.spark-submit \
    --username <service_account> --namespace <namespace_1> \
    ...
```

You can verify that the Spark job pods are scheduled on the right node(s) by running:

```shell
kubectl get pods -n <namespace_1> -o wide
```

The node running the pod is displayed under the `Node` column.

This setup presented above can also be used for a mixed-architectures cluster, as the nodes' architectures are provided by a label.
To restrict Spark jobs in `namespace_1` to only run on `arm64` nodes, use the following `nodeSelector` configuration:

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
Charmed Apache Spark provides multi-architecture rock images supporting amd64 and arm64.
```

### Defining a Pod template (alternative)

While we recommend using Namespace Node Affinity Operator for common scenarios, one downside is that it cannot discriminate between driver and executor pods, should they have different hardware needs or resource quotas.
[Enabling GPU acceleration](how-to-use-gpu) presents such a case, where we do not want to reserve costly resources for driver pods if they do not need it.\
This section presents an alternative way to schedule Spark jobs using Pod templates.

The example below is the equivalent of the first `namespaces_settings.yaml` presented in the previous section, as it applies a `nodeSelector` and a toleration matching a previously applied taint:

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

Pod templates can also be used to schedule pods on specific architecture.
The example below will schedule the driver and/or executors pods (depending on the Spark property used) only on `arm64` nodes.

```yaml
apiVersion: v1
kind: Pod
spec:
  nodeSelector:
    kubernetes.io/arch: arm64
```

The [Integration Hub charm](how-to-service-accounts-integration-hub) can be used to enforce Pod templates properties on integrated application by means of [charm configuration options](https://charmhub.io/spark-integration-hub-k8s/configurations#driver-pod-template).

```{note}
Please note that the template files must be accessible from the 'spark-submit' command, **not** from where the pods are actually running.
```

## Scheduling Charmed Apache Spark components

While the two previous sections already take care of segregating control-plane workloads from user-driven workloads, this guide details a few strategies on how to also separate the Charmed Apache Spark component from third party workloads (neither Charmed Apache Spark nor the Spark jobs) and take advantage of specific architectures.

To target a specific architecture, a Juju constraint can be applied to the Charmed Apache Spark model itself, or to each individual charm.
To apply the constraint to the model, run:

```shell
juju -m <charmed_spark_juju_model> set-model-constraints arch=arm64
```

All Juju applications to be deployed on said model will then use the constraint.
To apply the constraint to a single charm, run:

```shell
juju deploy -m <charmed_spark_juju_model> kyuubi-k8s --trust --channel=3.5/edge --constraints="arch=arm64"
```

One Juju model of multiple applications can be deployed over different architectures.

```{note}
You may check if a charm supports a specific architecture on [Charmhub](https://charmhub.io/).
```

Constraints tags may also be used to set affinity/anti-affinity of the charms' pods.
Please note that they are no native Juju mechanisms for setting tolerations, so the deployments examples here are limited to **untainted** nodes.

The following command:

```shell
juju deploy -m <charmed_spark_juju_model> kyuubi-k8s --constraints "tags=<label_key>=<label_value>"
```

results in a pod with a `nodeSelector` expression similar to what we did in the previous sections for the Spark jobs.

This mechanism can be used to improve availability.
To deploy three units of the Charmed Apache Kyuubi charm on three distinct nodes of a cluster, run:

```shell
export APP_NAME="kyuubi"
juju deploy -m <charmed_spark_juju_model> kyuubi-k8s $APP_NAME -n 3 \
 --constraints="tags=anti-pod.app.kubernetes.io/name=${APP_NAME},anti-pod.topology-key=kubernetes.io/hostname"
```

You may check with `kubectl get pod kyuubi-0 -n <charmed_spark_juju_model> -o yaml` that the proper anti-affinity rule was applied to the pod:

```yaml
...
spec:
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values:
                  - kyuubi
          topologyKey: kubernetes.io/hostname
...
```

```{warning}
It is not possible to deploy a single charm on heterogeneous architectures.
All units must be deployed on nodes of the same architecture.
```
