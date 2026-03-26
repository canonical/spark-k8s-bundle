---
myst:
  html_meta:
    description: "How-to guide for scheduling Charmed Apache Spark's components and its jobs on Kubernetes clusters."
---

(how-to-advanced-scheduling)=

# How to use advanced scheduling

This guide shows how to configure Charmed Apache Spark with Kubernetes mechanisms such as node affinity and toleration to optimize infrastructure governance and performance.

Those mechanisms are used to decouple control plane operations from user-driven workloads, ensuring system services remain stable on cost-effective instance.
Spark Executor pods can benefit from specialized hardware (high-memory nodes, custom hardware resources such as GPU, specific architecture) while maintaining the flexibility to scale idle resources to zero.

## Prerequisites

This guide assumes that Charmed Apache Spark is deployed on a multi-node Kubernetes cluster.

To configure advanced scheduling, use [nodeSelector](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector), [affinity rules](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity), and [taints](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/).
`nodeSelector` and affinity rules work with Kubernetes labels, while taints are applied directly to nodes.

To apply a label to a node:

```shell
kubectl label nodes <node_name> <key>=<value>
```

To taint a node:

```shell
kubectl taint nodes <node_name> <key>=<value>:<effect>
```

```{note}
We recommend exclusively using `NoSchedule` effects rather than `NoExecute` to avoid disrupting pre-existing workloads.
```

Verify that taints and labels were properly applied to the node:

```shell
kubectl describe node <node_name>
```


This guide shows how to schedule pods on tainted nodes and assign them to specific nodes, ensuring that:

- Spark Driver and Executor pods are scheduled on the nodes dedicated to running user workloads
- Charmed Apache Spark components are scheduled on control-plane nodes and/or specific architecture

## Scheduling jobs

Charmed Apache Spark can be configured to schedule Driver and Executor pod on specific nodes.
This section details how to set up and configure the advanced scheduling of Spark jobs to mutually segregate control-plane workloads from user workloads and allocate pods on mixed architectures clusters.

### Deploying the Namespace Node Affinity Operator (recommended)

The [Namespace Node Affinity Operator](https://github.com/canonical/namespace-node-affinity-operator) adds a given set of node affinities and/or tolerations to all pods deployed in a namespace.
This works well with Charmed Apache Spark, because user workloads are best run in a dedicated namespace rather than in the namespace used by the Charmed Apache Spark Juju model.
To deploy the Namespace Node Affinity Operator, run the following command:

```shell
juju deploy -m <charmed_spark_juju_model> namespace-node-affinity --trust
```

By default, the WebHook is not configured to modify pods in any namespace.
First, label each namespace that contains pods you want the webhook to modify by applying node affinity and toleration settings:

```shell
kubectl label ns <namespace_1> namespace-node-affinity=enabled
```

Repeat for all namespaces which will contain Spark service accounts.

```{note}
Note that those namespaces need to exist before you label them.
```

Then, provide the webhook configuration to apply to pods in those namespaces.
The following example applies a `nodeSelector` to pods in the namespace so that they are scheduled onto nodes with the specified label. It also adds a toleration so that the pods can run on nodes with the specified taint.

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

Save this file as `namespaces_settings.yaml`, then configure the charm:

```shell
juju config -m <charmed_spark_juju_model> namespace-node-affinity settings_yaml="$(<namespaces_settings.yaml)"
```

To verify the configuration, run a Spark job using the `spark-client` snap. The Driver and Executor pods are scheduled on nodes with the matching label, while the taint prevents other workloads from being scheduled on those nodes.

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
Charmed Apache Spark provides multi-architecture manifests for rock images supporting `amd64` and `arm64`.
Therefore, your container runtime should be able to use the proper image based on the node architecture without any further intervention.
```

Two Namespace Node Affinity Operator applications can work alongside one another to enforce distinct configurations on the Driver and Executor pods.
The solution is to use the `excludedLabels` to avoid applying the Driver pod configuration to the Executor pods and vice-versa.
To apply a toleration to the non Driver (ergo, Executor) pods on the first Namespace Node Affinity Operator:

```yaml
<namespace>: |
  excludedLabels:
    spark-role: driver
  tolerations:
  - key: <taint_key>
    operator: Equal
    value: <taint_value>
    effect: <taint_effect>
```

Respectively, doing the same thing on the second one by excluding `spark-role: executor` will result in a configuration applied to non Executor pods.

###  (Alternative) Defining a Pod template

While we recommend using Namespace Node Affinity Operator for common scenarios, one downside is that it is limited to adding affinities and tolerations.
Apache Spark on Kubernetes offers a native way of customising the deployments: [Pod templates](https://spark.apache.org/docs/latest/running-on-kubernetes.html#pod-template).

Pod templates are more complex and versatile than the Namespace Node Affinity Operator configuration and can be used to schedule pods with different hardware needs or resource quotas.
[Enabling GPU acceleration](how-to-use-gpu) presents such a case, where we do not want to reserve costly resources for Driver pods if they do not need it.\
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

You may omit one of the two Spark properties above, or point to a different file in each property to schedule Driver and Executors pods differently.

Pod templates can also be used to schedule pods on specific architecture.
The example below will schedule the Driver and/or Executors pods (depending on the Spark property used) only on `arm64` nodes.

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

### Using Juju commands

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

A single Juju model can contain applications deployed over different architectures.

```{note}
You may check if a charm supports a specific architecture on [Charmhub](https://charmhub.io/).
```

Constraints tags may also be used to set affinity/anti-affinity of the charms' pods.
Please note that they are no native Juju mechanisms for setting tolerations, so the deployments examples in this section are limited to **untainted** nodes.

The following command:

```shell
juju deploy -m <charmed_spark_juju_model> kyuubi-k8s --constraints "tags=<label_key>=<label_value>"
```

results in a pod with a `nodeSelector` expression similar to what we did in the previous sections for the Spark jobs.

The same mechanism can be used to improve service availability.
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

### Deploying the Namespace Node Affinity Operator

You can use Namespace Node Affinity Operator to add toleration to the Charmed Apache Spark components, similar to how we previously did it for the Apache Spark jobs themselves.
The targeted nodes must first be untainted.

Create a new Juju model:

```shell
juju add-model <charmed_spark_juju_model>
```

Then label the newly created namespace with:

```shell
kubectl label ns <charmed_spark_juju_model> namespace-node-affinity=enabled
```

Deploy the Namespace Node Affinity Operator:

```shell
juju deploy -m <charmed_spark_juju_model> namespace-node-affinity --trust
```

Once the charm is up and running, you may then taint the node:

```shell
kubectl taint node <node> <taint_key>=<taint_value>:<taint_effect>
```

In a new `settings.yaml` file, adapt the configuration below to your Juju model and node taint(s)/affinities:

```yaml
<charmed_spark_juju_model>: |
  tolerations:
  - key: <taint_key>
    operator: Equal
    value: <taint_value>
    effect: <taint_effect>
```

You may now configure the operator to apply the respective toleration to any new charm:

```shell
juju config -m <charmed_spark_juju_model> namespace-node-affinity settings_yaml="$(<settings.yaml)"
```

This is it! Any new Juju application deployment will now get the desired tolerations and affinities:

```shell
juju deploy -m <charmed_spark_juju_model> s3-integrator s3
```

You can check that the configuration is properly applied using:

```shell
kubectl get pod s3-0 -n <charmed_spark_juju_model> -o yaml | yq '.spec.tolerations'
```

```{note}
Please note that with the setup above, the modeloperator pod created by the addition of a new Juju model and the Namespace Node Affinity Operator might be deployed on a different node since they were scheduled before the Namespace Node Affinity Operator could apply the configuration.
```
