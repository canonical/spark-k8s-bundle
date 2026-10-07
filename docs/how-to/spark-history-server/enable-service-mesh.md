---
myst:
  html_meta:
    description: "How-to guide for adding Apache Spark History Server into Istio ambient service mesh."
---

(how-to-spark-history-server-enable-service-mesh)=
# Add Spark History Server to Istio service mesh

The Spark History server charm can be put behind Istio service mesh such that only specified set of pods are allowed to make connections to it and mTLS encryption is enforced on the traffic between the Spark History Server and other meshed pods. The Istio service mesh is supported in the ambient mode only, and therefore the legacy istio sidecar mode is not supported.

## Prerequisites

### Deploy Istio control plane

Enabling Istio service mesh requires Istio control to be installed in the K8s cluster, which is done by deploying the `istio-k8s` charm. You can skip this step if you already have a working Istio control plane installed in your Kubernetes cluster. If not, deploy `istio-k8s` charm as follows:

```bash
juju deploy istio-k8s --channel 2/stable --trust
```

### Deploy Istio Beacon charm

The Istio Beacon charm facilitates adding Juju charms to the Istio service mesh. Deploy `istio-beacon-k8s` charm as follows:

```bash
juju deploy istio-beacon-k8s --channel 2/stable --trust
```

## Enable Istio service mesh

Integrate the Spark History Server charm with the Istio Beacon charm over the `service-mesh` relation endpoint, which will add the Spark History server charm pods to the Istio service mesh:

```bash
juju integrate spark-history-server-k8s:service-mesh istio-beacon-k8s
```

The Spark History Server charm pods will then be restarted, and the Istio labels are added to the pods along with the creation of necessary authorization policies.

## Verify the charm pods are meshed

In order to verify that the Spark History Server is indeed protected behind the Istio service mesh, perform a `curl` to the Spark History Server UI address using an ephemeral pod:

```bash
kubectl run test-curl-history-server --rm -i --restart=Never --image=curlimages/curl:8.10.1 \
    -- curl -sS --max-time 10 http://<history-server-unit-address>:18080
```

You should see that the `curl` does not succeed, because the pod `test-curl-history-server` is not inside the service mesh, and no authorization policies exist that allow traffic from it to the Spark History Server pod.

## Access Spark History Server using Istio Ingress

When the Spark History Server is put behind the Istio service mesh, the Spark History Server UI should be accessed using the Istio Ingress.

### Deploy and integrate Istio Ingress

Deploy the `istio-ingress-k8s` charm in the same model as the Spark History Server charm:

```bash
juju deploy istio-ingress-k8s --channel 2/stable --trust
```

Integrate `istio-ingress-k8s` with the `istio-k8s` charm over the `istio-ingress-config` relation:

```bash
juju integrate istio-ingress-k8s:istio-ingress-config istio-k8s
```

Integrate `istio-ingress-k8s` with the Spark History Server charm over the `ingress` relation interface.

```bash
juju integrate spark-history-server-k8s:ingress istio-ingress-k8s:ingress
```

### Find the Ingress gateway address

After the integration completes and the charms are in active and idle state, get the Juju status
of the `istio-ingress-k8s` app.

```bash
juju status istio-ingress-k8s
```

You will see a message similar to the following under the Message column in the Juju status:

```text
Serving at <ip-address>
```

This is the address for the Ingress gateway load balancer.

### Access Spark History Server UI

Once you find the ingress gateway address, 
the URL endpoint for the Spark History Server should be at the following path:

```text
http://<ingress-gateway-address>/<juju-model-name>-spark-history-server-k8s
```
