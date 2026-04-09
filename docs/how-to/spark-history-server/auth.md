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

## Deploy the Identity Bundle and integrate it with the Spark History Server

To enable authentication and authorization for Spark History Server, complete the
following steps. This guide assumes you already deployed Charmed Apache Spark as
described in the [Charmed Apache Spark deployment guide](how-to-deploy-spark),
including a Spark History Server charm configured with an object storage backend.

## Deploy the Identity bundle

Authentication is provided by the
[Canonical Identity Bundle](https://charmhub.io/topics/canonical-identity-platform).
Deploy it by following this
[tutorial](https://charmhub.io/topics/canonical-identity-platform/tutorials/e2e-tutorial),
which installs all required Identity Platform components.

The deployment includes these charms:

- [Charmed Ory Hydra](https://charmhub.io/hydra): the OAuth/OIDC server.
- [Charmed Ory Kratos](https://charmhub.io/kratos): user management and authentication.
- [Login UI operator](https://charmhub.io/identity-platform-login-ui-operator): middleware that routes requests between services and serves login/error pages.
- [Kratos External IdP Integrator](https://charmhub.io/kratos-external-idp-integrator): integration with external identity providers.
- [Charmed PostgreSQL](https://charmhub.io/postgresql-k8s): SQL database backend.
- [Charmed Traefik](https://charmhub.io/traefik-k8s): ingress controller.
- [Self Signed Certificates](https://charmhub.io/self-signed-certificates): TLS certificate provider for ingress.

You must also configure the identity provider you want to use. Configure
`kratos-external-idp-integrator` with the parameters for your provider.

Example configuration for Microsoft Entra ID (Azure AD):

```bash
juju config kratos-external-idp-integrator microsoft_tenant_id=<YOUR_TENANT_ID> provider=microsoft client_id=<YOUR_CLIENT_ID> client_secret=<YOUR_CLIENT_SECRET>
```

For supported identity providers and additional details, see the
[How to manage external identity providers guide](https://discourse.charmhub.io/t/how-to-manage-external-identity-providers/11910).

The connection between Spark History Server and the Identity Platform is handled by
the Charmed OAuth2 Proxy charm. OAuth2 Proxy protects endpoints exposed through
ingress (Traefik).

## Enable authentication with Charmed OAuth2 Proxy

To set up OAuth2 Proxy, first enable the feature in Traefik, expose the forward-auth
offer, and integrate it with Spark History Server through the ingress relation.

```bash
juju config traefik-public enable_experimental_forward_auth=True
juju offer traefik-public:experimental-forward-auth forward-auth
juju integrate spark-history-server-k8s admin/core.ingress
```

Next, deploy OAuth2 Proxy and integrate it with Traefik using the exposed offer:

```bash
juju deploy oauth2-proxy-k8s --channel latest/stable --trust
juju integrate oauth2-proxy-k8s:forward-auth admin/core.forward-auth
```

Then integrate Spark History Server with OAuth2 Proxy:

```bash
juju integrate oauth2-proxy-k8s spark-history-server-k8s:oauth2-proxy
```

Finally, integrate OAuth2 Proxy with the Identity Platform OIDC provider
(Charmed Hydra):

```bash
juju integrate oauth2-proxy-k8s:oauth hydra
```

After integration completes, get the endpoint by running:

```bash
juju run traefik-public/leader show-proxied-endpoints
```

When you open the URL exposed by Traefik, you are redirected to your configured
identity provider for authentication. After successful login, you can access the
Spark History Server endpoint.

## Authorization Management

By default, all authenticated users can access Spark History Server. To restrict
access, configure an allow-list of authorized users. Provide email addresses as a
comma-separated list:

```bash
juju config spark-history-server-k8s authorized-users="user1@canonical.com, user3@canonical.com"
```

## Oathkeeper integration (deprecated)

Previously, authentication in this guide used the `oathkeeper` charm. `oathkeeper`
is now deprecated in favor of Charmed OAuth2 Proxy.

If your deployment still uses `oathkeeper`, migrate by removing integrations with
`oathkeeper`, updating Identity Platform components as described above, and then
integrating `oauth2-proxy-k8s`.
