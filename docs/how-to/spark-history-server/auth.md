---
myst:
  html_meta:
    description: "How-to guide for enabling authentication and authorization for Spark History Server using Canonical Identity Platform integration."
---

(how-to-spark-history-server-auth)=
# Enable authentication and authorization with the Spark History Server charm

Charmed Apache Spark includes the Spark History Server charm, which lets users monitor
application workflows and logs. By default, Spark History Server does not provide
authentication or authorization, both of which are essential in production environments.
To address this limitation, you can integrate the Spark History Server charm with the
Canonical Identity Platform bundle.

This guide assumes you already deployed Charmed Apache Spark as
described in the [Charmed Apache Spark deployment guide](how-to-deploy-spark),
including a Spark History Server charm configured with an object storage backend.

## Enable Authentication

Authentication for Spark History Server charm is provided by the
[Canonical Identity Bundle](https://canonical-identity.readthedocs-hosted.com/identity-platform/).

### Deploy the Canonical Identity bundle

Deploy the Canonical Identity bundle by following this
[tutorial](https://canonical-identity.readthedocs-hosted.com/identity-platform/tutorial/canonical-identity-platform/).

The deployment will create two Juju models where Identity Platform charmed applications
and their charm dependencies are deployed, configured and integrated.

The `iam` model contains all the crucial identity applications:

- [Charmed Ory Hydra](https://charmhub.io/hydra): the OAuth/OIDC server.
- [Charmed Ory Kratos](https://charmhub.io/kratos): the user management and authentication.
- [Login UI operator](https://charmhub.io/identity-platform-login-ui-operator): a middleware that routes requests between services and serves login/error pages.

And the `core` model contains all of their shared dependencies:

- [Charmed PostgreSQL](https://charmhub.io/postgresql-k8s): SQL database backend.
- [Charmed Traefik](https://charmhub.io/traefik-k8s): ingress controller.
- [Self Signed Certificates](https://charmhub.io/self-signed-certificates): TLS certificate provider for ingress.

### Configure the identity provider

You must also configure the identity provider you want to use. You can either use the built-in identity provider that is enabled by
default in Charmed Kratos, or use an external identity provider.

This guide uses the local identity provider via Charmed Kratos. Follow [this guide](https://canonical-identity.readthedocs-hosted.com/identity-platform/how-to/manage-external-identity-providers/) if you want to use an external identity provider.

Create your personal admin account:

```bash
juju run -m iam kratos/0 create-admin-account email=<your-email> username=<username>
```

After the account is created, use the provided password reset link to set your password and complete the setup. You can now use this account
to log in to the Spark History Server.

For supported identity providers and additional details, see the
[How to manage external identity providers guide](https://discourse.charmhub.io/t/how-to-manage-external-identity-providers/11910).

### Deploy and integrate Charmed OAuth2 Proxy

The connection between Spark History Server and the Identity Platform is handled by
the Charmed OAuth2 Proxy charm. OAuth2 Proxy protects endpoints exposed through
an ingress (eg, Traefik).

Deploy OAuth2 Proxy charm and integrate it with Spark History Server:

```bash
juju deploy oauth2-proxy-k8s --channel latest/stable --trust
juju integrate oauth2-proxy-k8s spark-history-server-k8s:oauth2-proxy
```

Now, consume the `oauth-offer` offered from the `iam` model, 
and integrate OAuth2 Proxy with it:

```bash
juju consume iam.oauth-offer
juju integrate oauth2-proxy-k8s:oauth oauth-offer
```

Finally, consume the `send-ca-cert` offered from the `core` model, and integrate it with Oauth2 Proxy over
the `receive-ca-cert` relation endpoint:

```bash
juju consume core.send-ca-cert
juju integrate oauth2-proxy-k8s:receive-ca-cert send-ca-cert
```

### Configure ingress

An ingress needs to be deployed and configured such that it forwards authentication requests to 
Charmed OAuth2 Proxy charm, and only the requests that are completely authenticated are
passed to the Spark History Server charm.

Spark History Server charm currently supports two Ingress provider charms (namely the Traefik ingress and the Istio ingress), depending upon whether it is
added to Istio service mesh or not.

#### Traefik Ingress (non meshed setup)

For a non meshed setup, the Traefik ingress that comes already bundled in the Identity Platform bundle can be used.
To use it, first configure the existing Traefik ingress to enable the forward-auth feature, and expose the `forward-auth` offer.

```bash
juju switch core
juju config traefik-public enable_experimental_forward_auth=True
juju offer traefik-public:experimental-forward-auth traefik-forward-auth
```

Also offer the endpoint `ingress` from the `core` module:

```bash
juju offer traefik-public:ingress traefik-ingress
```

Now, switch back to the model containing Spark History Server app and integrate the ingress with the Spark History Server and the OAuth2 Proxy charms.

```bash
juju switch <spark-history-server-model>
juju consume core.traefik-ingress
juju integrate spark-history-server-k8s:ingress traefik-ingress
juju integrate oauth2-proxy-k8s:ingress traefik-ingress
```

Integrate the OAuth2 Proxy charm with the `traefik-forward-auth` offer over the `forward-auth` relation endpoint:

```bash
juju consume core.traefik-forward-auth
juju integrate oauth2-proxy-k8s:forward-auth traefik-forward-auth
```

After integration completes, get the endpoint by running:

```bash
juju run -m core traefik-public/leader show-proxied-endpoints
```

You should see an output similar to the following:

```text
proxied-endpoints: '{"traefik-public": {"url": "https://10.99.99.0"}, "remote-xxxxxxxxxxxx": "http://10.99.99.0/testmodel-spark-history-server-k8s/"}'
```

The URL endpoint for the Spark History Server is the one ending with `spark-history-server-k8s` (or the name of the Spark History Server app).

#### Istio Ingress (Istio service mesh setup)

If the Spark History Server is running behind Istio service mesh, Traefik is not supported as Ingress and therefore,
Istio ingress should be used. Istio ingress requires the Istio control plane to be installed in the cluster.

Deploy `istio-ingress-k8s` charm:

```bash
juju deploy istio-ingress-k8s --channel 2/stable --trust
```

```{note}
The `istio-ingress-k8s` requires `istio-k8s` properly deployed in order to work. It is assumed that if you have a Istio 
service mesh setup, you already have a working `istio-k8s` deployment. If not, deploy it with 
`juju deploy istio-k8s --channel 2/stable --trust` before you deploy `istio-ingress-k8s`.
```

Integrate `istio-k8s` and `istio-ingress-k8s` over the `istio-ingress-config` relation endpoint:

```bash
juju integrate istio-k8s:istio-ingress-config istio-ingress-k8s:ingress-config
```

Integrate `istio-ingress-k8s` with the `certificates` offer, such that HTTPS is enabled:

```bash
juju consume core.certificates
juju integrate istio-ingress-k8s:certificates certificates
```

Integrate the Istio ingress charm with OAuth2Proxy and Spark History Server charms:

```bash
juju integrate istio-ingress-k8s:ingress-unauthenticated oauth2-proxy-k8s:ingress
juju integrate istio-ingress-k8s:forward-auth oauth2-proxy-k8s:forward-auth
juju integrate istio-ingress-k8s:ingress spark-history-server-k8s:ingress
```

After the integration completes and the charms are in active and idle state, get the Juju status
of the `istio-ingress-k8s` app.

```bash
juju status istio-ingress-k8s
```

You will see a message similar to the following under the Message column in the Juju status:

```text
Serving at <ip-address>
```

This is the address for the Ingress gateway. Once you find the ingress gateway address, 
the URL endpoint for the Spark History Server should be at the following path:

```text
https://<ingress-gateway-address>/<juju-model-name>-spark-history-server-k8s
```

### Access Spark History Server UI

Once you find the URL endpoint for the Spark History Server using the ingress of your choice,
open the URL in the browser. When you open the URL, you are redirected to your configured
identity provider for authentication. After successful login, you can access the
Spark History Server UI.

## Authorization Management

By default, all authenticated users can access Spark History Server. To restrict
access, configure an allow-list of authorized users. Provide email addresses as a
comma-separated list:

```bash
juju config spark-history-server-k8s authorized-users="user1@canonical.com,user3@canonical.com"
```

## Oathkeeper integration (deprecated)

Previously, authentication in this guide used the `oathkeeper` charm. `oathkeeper`
is now deprecated in favor of Charmed OAuth2 Proxy.

If your deployment still uses `oathkeeper`, migrate by removing integrations with
`oathkeeper`, updating Identity Platform components as described above, and then
integrating `oauth2-proxy-k8s`.
