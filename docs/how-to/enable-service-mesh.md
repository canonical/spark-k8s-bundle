---
myst:
  html_meta:
    description: "How-to guide for adding Charmed Apache Spark charms and workload pods into Istio ambient service mesh."
---

(how-to-enable-service-mesh)=
# Enable istio service mesh in Charmed Apache Spark

The Charmed Apache Spark charm pods and workload pods can be put behind Istio service mesh such that only a specified set of pods are allowed to make connections to them and mTLS encryption is enforced on the traffic between them.

## Compatibility

The istio service mesh feature is supported only on the revisions greater than the following revisions for respective charms in their respective channels:

<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <thead>
    <tr>
      <th rowspan="2">Charm</th>
      <th rowspan="2">Channel</th>
      <th colspan="2">Minimum Required Revision</th>
    </tr>
    <tr>
      <th>amd64</th>
      <th>arm64</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2"><code>spark-history-server-k8s</code></td>
      <td><code>3/edge</code></td>
      <td>144</td>
      <td>143</td>
    </tr>
    <tr>
      <td><code>4/edge</code></td>
      <td>147</td>
      <td>148</td>
    </tr>
    <tr>
      <td><code>spark-integration-hub-k8s</code></td>
      <td><code>3/edge</code></td>
      <td>164</td>
      <td>165</td>
    </tr>
    <tr>
      <td rowspan="3"><code>kyuubi-k8s</code></td>
      <td><code>3.4/edge</code></td>
      <td>230</td>
      <td>231</td>
    </tr>
    <tr>
      <td><code>3.5/edge</code></td>
      <td>224</td>
      <td>225</td>
    </tr>
    <tr>
      <td><code>4.0/edge</code></td>
      <td>236</td>
      <td>237</td>
    </tr>
  </tbody>
</table>

## Prerequisites

### Deploy Istio control plane

```{note}
You can skip this step if you already have a working Istio control plane installed in your Kubernetes cluster.
```

Enabling Istio service mesh requires Istio control plane to be installed in the K8s cluster, which is done by deploying the `istio-k8s` charm. Create a new Juju model with name `istio-system`, and deploy `istio-k8s` charm:

```bash
juju add-model --no-switch istio-system
juju deploy istio-k8s -m istio-system --channel 2/stable --trust
```

### Deploy Istio Beacon charm

The Istio Beacon charm facilitates adding Juju charms to the Istio service mesh. Deploy `istio-beacon-k8s` charm in the same model as the Charmed Apache Spark charms:

```bash
juju deploy istio-beacon-k8s --channel 2/stable --trust
```

## Add Apache Spark workloads to mesh

Integrate the Spark Integration Hub charm with the Istio Beacon charm over the `service-mesh` relation endpoint:


```sh
juju integrate spark-integration-hub-k8s:service-mesh istio-beacon-k8s
```

The Spark Integration Hub charm pods will then be restarted, and the Istio labels are added to the pods along with necessary authorization policies. Any Spark workload pods that are created after this will now be meshed automatically.

## Add Charmed Apache Kyuubi to mesh

Integrate the Charmed Apache Kyuubi K8s charm with the Istio Beacon charm over the `service-mesh` relation endpoint:

```bash
juju integrate kyuubi-k8s:service-mesh istio-beacon-k8s
```

```{note}
This integration requires the `kyuubi-k8s` charm deployed with `--trust`. If not, you can elevate the permissions to 
an existing charm deployment using `juju trust --scope=cluster kyuubi-k8s`.
```

The Charmed Apache Kyuubi K8s charm pods will then be restarted, and the Istio labels are added to the pods along with necessary authorization policies.

## Add telemetry collector agent to mesh

The telemetry collector charm must be meshed for it to be able to fetch the telemetry from the charms in Charmed Apache Spark solution.

```{note}
The `opentelemetry-collector-k8s` is the only supported telemetry collector for observability in meshed setup and `grafana-agent-k8s` is not supported. For more information on how to enable monitoring, please refer to the [monitoring guide](how-to-monitoring).
```

Integrate OpenTelemetry Collector charm with the Istio Beacon charm over the `service-mesh` relation endpoint:

```bash
juju integrate opentelemetry-collector-k8s:service-mesh istio-beacon-k8s
```

```{note}
This integration requires the `opentelemetry-collector-k8s` charm deployed with `--trust`. If not, you can elevate the permissions to 
an existing charm deployment using `juju trust --scope=cluster opentelemetry-collector-k8s`.
```

The OpenTelemetry Collector charm pods will then be restarted, and the Istio labels are added to the pods along with necessary authorization policies.

## Add Spark History Server to mesh

Integrate the Spark History Server charm with the Istio Beacon charm over the `service-mesh` relation endpoint:

```bash
juju integrate spark-history-server-k8s:service-mesh istio-beacon-k8s
```

```{note}
This integration requires the Spark History Server charm deployed with `--trust`. If not, you can elevate the permissions to an existing charm deployment using `juju trust --scope=cluster spark-history-server-k8s`.
```

The Spark History Server charm pods will then be restarted, and the Istio labels are added to the pods along with the creation of necessary authorization policies.

## Verify the charm and workload pods are meshed

The verification of whether the pods are meshed can be done by listing the pods that have the Istio ambient labels on it using `kubectl`:

```bash
kubectl get pods -A -l istio.io/dataplane-mode=ambient
```

Once the ambient mesh is enabled, the Kyuubi pods should be in this list, and any workload pods created after enabling the mesh should also be in the same list. For example,

```txt
NAMESPACE     NAME                            READY   STATUS    RESTARTS   AGE
spark         kyuubi-k8s-0                    2/2     Running   0          17m
spark         integration-hub-k8s-0           2/2     Running   0          17m
spark         spark-history-server-k8s-0      2/2     Running   0          45s
spark         opentelemetry-collector-k8s-0   2/2     Running   0          45s
```

In addition, to verify that the Spark History Server is indeed protected behind the Istio service mesh, perform a `curl` to the Spark History Server UI address using an ephemeral pod:

```bash
kubectl run test-curl-history-server \
  --rm -i --restart=Never --image=curlimages/curl:8.10.1 \
  -- curl -sS --max-time 10 http://<history-server-unit-address>:18080
```

You should see that the `curl` does not succeed, because the pod `test-curl-history-server` is not inside the service mesh, and no authorization policies exist that allow traffic from it to the Spark History Server pod. You should see an error similar to the following:

```text
curl: (56) Recv failure: Connection reset by peer
```

## Access Spark History Server using Istio Ingress

When the Spark History Server is put behind the Istio service mesh, the Spark History Server UI should be accessed using the Istio Ingress.

```{note}
The `traefik-k8s` ingress cannot be used to access Spark History Server UI in meshed setup.
```

### Deploy and integrate Istio Ingress

Deploy the `istio-ingress-k8s` charm in the same model as the Spark History Server charm:

```bash
juju deploy istio-ingress-k8s --channel 2/stable --trust
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

The address you see here is the address for the Ingress gateway load balancer.

### Access Spark History Server UI

Once you find the ingress gateway address, the URL endpoint for the Spark History Server should be at the following path:

```text
http://<ingress-gateway-address>/<juju-model-name>-spark-history-server-k8s
```

> See also: [Enable authentication and authorization with the Spark History Server](how-to-spark-history-server-auth) guide.
