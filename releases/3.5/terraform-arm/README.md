# Mixed architecture bundle deployment exploration

This folder copies part of the amd64 Terraform deployment as a convenient way to try various approaches.
The final result should be merged with the existing bundle following CC008: Charm Terraform Standards.

This temporary bundle differs from the existing one by:

- Removing COS Juju model, the COS "internal" bundle and its integrations to the Observability module
- Removing the Observability module and its integrations to the Spark module
- Removing the Azure Storage module and its integrations to the Spark module
- Removing the Manual TLS operator module
- Replacing the existing amd64 arch constraint with arm64 wherever possible
- Updating the channel and revision for charms with arm64 support
- Updating the OCI resources for the charms recently supporting arm64
- Updating all risks to edge for the charms recently supporting arm64

This bundle was successfully tested on PS7 using the following variables file:

```json
K8S_CLOUD="mixed"
K8S_CREDENTIAL="mixed"
zookeeper_units=1
kyuubi_driver_pod_template="s3://mybucket/pod_template.yaml"
kyuubi_executor_pod_template="s3://mybucket/pod_template.yaml"
s3={
  bucket="mybucket"
  region="default"
  endpoint="http://10.152.77.205:80"
}
```

The IP above referring to a MicroCeph RGW instance running on one of the nodes.

## Highlights

Here is a summary of the changes required to deploy and operate the bundle in a mixed architecture setting.

### Architecture constraints

Each charm must explicitly specify the target node architecture.
No specific action is required to declare that a node is using a specific architecture.
This constraint works in a somewhat similar way as a taint, since a charmed application declaring a specifying architecture cannot be schedule on an incompatible node.

Following CC008, this constraint will be specified in the mandatory `constraints` input.

### Node selector and taints

It is fairly straightforward to manage the scheduling of the pods.
By labelling one or more nodes with `kubectl label node <node> pool=worker` and using the following pod template:

```yaml
apiVersion: v1
kind: Pod
spec:
  nodeSelector:
    pool: worker
```

We ensure that spark pods (driver and/or executors based on the spark properties we set) are scheduled on the proper nodes.

By tainting one or more nodes with `kubectl taint nodes <node> pool=worker:NoSchedule`, we prevent pod without the matching toleration from being schedule on this node.
This is done by the following pod template:

```yaml
apiVersion: v1
kind: Pod
spec:
  tolerations:
    - effect: NoSchedule
      key: pool
      operator: Equal
      value: worker
```

By mixing the two approaches, we ensure that spark pods:

- are scheduled on the "worker" nodes
- are the only pods being scheduled there (unless another resource use the same toleration)

```yaml
apiVersion: v1
kind: Pod
spec:
  tolerations:
    - effect: NoSchedule
      key: pool
      operator: Equal
      value: worker
  nodeSelector:
    pool: worker
```

One caveat is that the pod template file must be accessible from the environment running the `spark-submit` command.
This is not an issue for our data lakehouse story, as the Kyuubi charm would that entrypoint, but this requires a more sensible approach for the spark-client snap.

## What's next

- We need new stable release for arm64 support
- We need to refactor the TF bundle following CC008 to expose the `constraint` input for the arch. We are already providing a variable to configure the pod template.
- We could give the `namespace-node-affinity-operator` charm a try and label users namespace appropriately so that affinities are applied.
- We could also give PodTolerationRestriction a try. For MicroK8s:

1. Open the following file on each node:
   `/var/snap/microk8s/current/args/kube-apiserver`

2. Find the --enable-admission-plugins flag. If it’s already there, add PodTolerationRestriction to the comma-separated list. If it’s not there, add a new line:
   `--enable-admission-plugins=NodeRestriction,PodTolerationRestriction` (include any others you're already using).

3. To pick up the changes, restart the snap services:
   `sudo snap restart microk8s`

Though Mattia's investigation lead to the conclusion that a different approach would be better since it is distribution-specific.
