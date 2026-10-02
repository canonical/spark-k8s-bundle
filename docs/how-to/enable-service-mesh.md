---
myst:
  html_meta:
    description: "How-to guide for adding Charmed Apache Spark workload pods into Istio ambient service mesh."
---

(how-to-enable-service-mesh)=
# Add the Charmed Apache Spark workloads to Istio ambient service mesh

The Charmed Apache Spark workload pods (the driver and the executor pods) can be put behind Istio service mesh such that only a specified set of pods are allowed to make connections to them and mTLS encryption is enforced on the traffic between them.

The Charmed Apache Spark workload pods are added to the service mesh by adding the Spark Integration Hub charm to the service mesh. The Spark Integration Hub charm is then responsible for adding necessary labels and authorization policies to the Apache Spark workload pods such that they are also added to the Istio service mesh.

## Adding Istio control plane

Enabling Istio service mesh requires Istio control to be installed in the K8s cluster, which is done by deploying the `istio-k8s` charm. You can skip this step if you already have a working Istio control plane installed in your Kubernetes cluster. If not, create a new Juju model (recommended) named `istio-system` and deploy `istio-k8s` charm to it as follows:

```bash
juju add-model istio-system
juju deploy istio-k8s --channel 2/stable --trust
```

Once the Istio K8s charm is deployed, idle and active, switch back to the model where you deployed Spark Integration Hub charm as follows:

```bash
juju switch <spark-integration-hub-juju-model>
```

## Deploy Istio Beacon charm

The Istio Beacon charm facilitates adding Juju charms to the Istio service mesh. Deploy `istio-beacon-k8s` charm from charmhub as follows:

```bash
juju deploy istio-beacon-k8s --channel 2/stable --trust
```

## Add Spark workload pods to service mesh

Integrate the Spark Integration Hub charm with the Istio Beacon charm over the `service-mesh` relation endpoint:

```bash
juju integrate spark-history-server-k8s:service-mesh istio-beacon-k8s
```

The Spark Integration Hub charm pods will then be restarted, and the Istio labels are added to the pods along with necessary authorization policies. Any Spark workload pods that are created after this will now be meshed automatically.
