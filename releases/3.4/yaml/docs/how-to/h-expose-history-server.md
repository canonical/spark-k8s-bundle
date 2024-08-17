## Expose Spark History Server UI

Spark History Server has web GUI but to access it we need to expose its address for external connections.

## Without Ingress (MicroK8s only)

The Spark History Server exposes a UI accessible at `http://<spark-history-server-ip>:18080`. 

If you are running MicroK8s, you can directly expose it to the local network by enabling DNS:

```bash
microk8s enable dns
```

and retrieve the Spark History Server POD IP using:

```bash
IP=$(kubectl get pod spark-history-server-k8s-0 -n spark --template '{{.status.podIP}}')
```

## With Ingress

The Spark History Server can be exposed outside a K8s cluster by means of an ingress. This is the recommended way in production for any K8s distribution. Exposing Kubernetes services through an ingress generally requires the cloud provider/infrastructure to have an external load balancer integrated with the Kubernetes cluster. Most cloud providers (such as AWS, Google and Azure) provide this integration out-of-the-box. If you are running on MicroK8s, make sure that you have enabled `metallb`, as shown in the Spark Tutorial at the "Set up the environment for the tutorial" page. 

Spark History Server can be exposed outside of the K8s cluster using `traefik-k8s` charm.

If COS is enabled, you can use the ingress already provided as part of the COS bundle. Otherwise, you can deploy one using:

```bash
juju deploy traefik-k8s --channel latest/candidate --trust
```

Then, relate with the Spark History Server charm:

```bash
juju relate traefik-k8s spark-history-server-k8s
```

After the charms settle down into `idle/active` states, fetch the URL of the Spark History Server with:

```bash
juju run-action traefik-k8s/0 show-proxied-endpoints --wait
```

This should print a JSON with all the ingress endpoints exposed by the `traefik-k8s` charm. To also exposed the UI outside the local cloud network via a public domain or to enable TLS encryption, please refer to the [Let’s Encrypt certificates in Juju](/t/8704) about integration of `traefik-k8s` with Route53 and Let's Encrypt.

> **Note**: The above is supported on AWS EKS only.
