---
myst:
  html_meta:
    description: "How-to guide for adding Charmed Apache Kyuubi and its workloads into Istio ambient service mesh."
---

(how-to-apache-kyuubi-enable-service-mesh)=
# Add Charmed Apache Kyuubi to Istio ambient service mesh

The Charmed Apache Kyuubi K8s charm can be put behind Istio service mesh such that only specified set of pods are allowed to make connections to it and mTLS encryption is enforced on the traffic between the Kyuubi charm pods and other meshed pods.

## Adding Istio control plane

Enabling Istio service mesh requires Istio control to be installed in the K8s cluster, which is done by deploying the `istio-k8s` charm. You can skip this step if you already have a working Istio control plane installed in your Kubernetes cluster. If not, create a new Juju model (recommended) named `istio-system` and deploy `istio-k8s` charm to it as follows:

```bash
juju add-model istio-system
juju deploy istio-k8s --channel 2/stable --trust
```

Once the Istio K8s charm is deployed, idle and active, switch back to the model where you deployed Charmed Apache Kyuubi K8s charm as follows:

```bash
juju switch <kyuubi-juju-model>
```

## Deploy Istio Beacon charm

The Istio Beacon charm facilitates adding Juju charms to the Istio service mesh. Deploy `istio-beacon-k8s` charm from charmhub as follows:

```bash
juju deploy istio-beacon-k8s --channel 2/stable --trust
```

## Add Charmed Apache Kyuubi pods to the mesh

Integrate the Charmed Apache Kyuubi K8s charm with the Istio Bacon charm over the `service-mesh` relation endpoint, which will add the charm pods to the Istio service mesh:

```bash
juju integrate kyuubi-k8s:service-mesh istio-beacon-k8s
```

The Charmed Apache Kyuubi K8s charm pods will then be restarted, and the Istio labels are added to the pods along with necessary authorization policies.

## Add Apache Kyuubi workload pods to the mesh

Integrating the Kyuubi charm with the Istio Beacon charm puts the Kyuubi charm pods to the service mesh, but it won't yet put the workload pods (the Apache Spark driver and executor pods) into the mesh. In order to add the workload pods to the mesh, the Spark Integration Hub charm needs to be integrated with the Istio Beacon charm.

Integrate the Spark Integration Hub charm with the Istio Beacon charm:

```bash
juju integrate spark-integration-hub-k8s:service-mesh istio-beacon-k8s
```

## Verifying that the Kyuubi pod and workload pods are meshed

The verification of whether the pods are meshed can be done by listing the pods using `kubectl` that has the Istio ambient labels on it:

```bash
kubectl get pods -A -l istio.io/dataplane-mode=
```

Once the ambient mesh is enabled, the Kyuubi pods should be in this list, and any workload pods created after enabling the mesh should also be in the same list.