---
myst:
  html_meta:
    description: "How-to guide for adding Charmed Apache Spark workload pods into Istio ambient service mesh."
---

(how-to-enable-service-mesh)=
# Add Charmed Apache Spark workloads to Istio service mesh

The Charmed Apache Spark workload pods (the driver and the executor pods) can be put behind Istio service mesh such that only a specified set of pods are allowed to make connections to them and mTLS encryption is enforced on the traffic between them.

The Charmed Apache Spark workload pods are added to the service mesh by adding the Spark Integration Hub charm to the service mesh. The Spark Integration Hub charm is then responsible for adding necessary labels and authorization policies to the Apache Spark workload pods such that they are also added to the Istio service mesh.

## Prerequisites

### Deploy Istio control plane

Enabling Istio service mesh requires Istio control plane to be installed in the K8s cluster, which is done by deploying the `istio-k8s` charm. You can skip this step if you already have a working Istio control plane installed in your Kubernetes cluster. If not, deploy `istio-k8s` charm to it as follows:

```bash
juju deploy istio-k8s --channel 2/stable --trust
```

### Deploy Istio Beacon charm

The Istio Beacon charm facilitates adding Juju charms to the Istio service mesh. Deploy `istio-beacon-k8s` charm from charmhub as follows:

```bash
juju deploy istio-beacon-k8s --channel 2/stable --trust
```

## Add charm and workload pods to service mesh

Integrate the Spark Integration Hub charm with the Istio Beacon charm over the `service-mesh` relation endpoint:

```sh
juju integrate spark-integration-hub-k8s:service-mesh istio-beacon-k8s
```

The Spark Integration Hub charm pods will then be restarted, and the Istio labels are added to the pods along with necessary authorization policies. Any Spark workload pods that are created after this will now be meshed automatically.

## Verify the charm and workload pods are meshed

The verification of whether the pods are meshed can be done by listing the pods using `kubectl` that has the Istio ambient labels on it:

```bash
kubectl get pods -A -l istio.io/dataplane-mode=ambient
```

Once the ambient mesh is enabled, the Kyuubi pods should be in this list, and any workload pods created after enabling the mesh should also be in the same list. For example,

```txt
NAMESPACE     NAME                      READY   STATUS    RESTARTS   AGE
test-model    istio-beacon-k8s-0        2/2     Running   0          2m2s
test-model    integration-hub-k8s-0     2/2     Running   0          1m10s
```
