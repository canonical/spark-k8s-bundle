---
myst:
  html_meta:
    description: "How-to guide for enabling authentication and authorization for Spark History Server using Canonical Identity Platform integration."
---

(how-to-spark-history-server-auth)=
# Enable authorization and authentication with the Spark History Server charm

The Charmed Apache Spark solution includes the Spark History charm that enables users to monitor
their applications workflows and logs. Natively, this product does not support authentication and
authorization that is an essential feature in a production environment. To overcome this limitation,
the Spark History Server charm is integrated with the Canonical Identity bundle that offers several
authentication and authorization functionalities with Juju.

## Deploy the Identity Bundle and integrate it with the Spark History Server

In order to enable authentication and authorization on the Spark History Server charm some steps
are needed. Here, we assume that you have already deployed Charmed Apache Spark using
the bundles, as described in the [Charmed Apache Spark deployment guide](how-to-deploy-spark),
that includes a Spark History Server charm, already configured with an object storage backend.


# Deploy the Identity bundle

To enable authentication we rely on the [Canonical Identity Bundle](https://charmhub.io/topics/canonical-identity-platform).
The bundle can be deployed following this [guide](https://charmhub.io/topics/canonical-identity-platform/tutorials/e2e-tutorial) that will deploy all components required by the Identity Bundle.

In particular the following charms will be deployed:
- [Charmed Ory Hydra](https://charmhub.io/hydra): the OAuth/OIDC server.
- [Charmed Ory Kratos](https://charmhub.io/kratos): the user management and authentication component.
- [Login UI operator](https://charmhub.io/identity-platform-login-ui-operator): a middleware which routes calls between the different services and serves the login/error pages.
- [Kratos External Idp Integrator](https://charmhub.io/kratos-external-idp-integrator):for integrating with external idp providers.
- [Charmed Postgresql](https://charmhub.io/postgresql-k8s): the SQL database of choice.
- [Charmed Traefik](https://charmhub.io/traefik-k8s): which will be used for ingress.
- [Self Signed Certificates](https://charmhub.io/self-signed-certificates): for managing the TLS certificates that our ingress will use.

One required step is to configure which identity provider we want to use. 
This can be done by configuring the `kratos-external-idp-integrator` with the configurations and parameters of your identity provider.

The following is an example of configuration for the Azure Identity provider:

```bash
juju config kratos-external-idp-integrator microsoft_tenant_id=<YOUR_TENANT_ID> provider=microsoft client_id=<YOUR_CLIENT_ID> client_secret=<YOUR_CLIENT_SECRETS>.
```

More information about supported identity providers and other useful information can be found in the
[How to manage external identity providers guide](https://discourse.charmhub.io/t/how-to-manage-external-identity-providers/11910).

The relation between the Spark History Server and the Identity bundle is handled by the Charmed OAuth2 Proxy charm that is provided by the Canonical Identity Team.
This charm enables the protection of endpoints that are behind an ingress, more specifically Traefik.


## Enabling Authentication with Charmed OAuth2 Proxy

In order to set up the proxy, you first need to expose the forward-auth offer, enable the feature in Charmed Traefik, and integrate it the Spark History server charm via the ingress relation.

```bash
juju config traefik-public enable_experimental_forward_auth=True
juju offer traefik-public:experimental-forward-auth forward-auth
juju integrate spark-history-server-k8s admin/core.ingress 

```

The next step is to deploy Charmed OAuth2 Proxy and integrate it with Charmed Traefik using the exposed offer:

```bash
juju deploy oauth2-proxy-k8s --channel latest/stable --trust
juju integrate oauth2-proxy:forward-auth admin/core.forward-auth
```

Then, integrate the Spark History Server charm with the proxy by running:
```bash
juju integrate oauth2-proxy-k8s spark-history-server-k8s:oauth2-proxy 
```

Finally, integrate the proxy with the Identity Platform’s OIDC provider—Charmed Hydra:
```bash
juju integrate oauth2-proxy-k8s:oauth hydra
```

Eventually, you can get the endpoint by running this action:

```bash
juju run traefik-public/leader show-proxied-endpoints
```

When you access the link exposed by Traefik, you will be redirected to your desired
identity provider to do the authentication. After a successful authentication,
you will be permitted to access the Spark History server endpoint.


## Authorization Management

By default, all authenticated users can access the Spark History Server endpoint. To limit access to a selected set of users, the Spark History Server charm offers the possibility to specify authorized users. This can be done by updating a configuration option. The authorized users (identified by email address) should be specified as a comma-separated list.

```bash
juju config spark-history-server-k8s authorized-users="user1@canonical.com, user3@canonical.com"
```


## Oauthkeeper integration (DEPRECATED)

Previously, in order to enable authentication we relied on another charm named `oathkeeper`. This charm has been deprecated in favour of a more modern and reliable solution that is the Charmed OAuth2 Proxy.

If the authentication was performed by using the `oathkeeper`charm we suggested to move the to the `oauth2-proxy` charm. In order to do so, the first step consist of removing the integration with the `oathkeeeper` charm and then update the Identity Bundle components following the instruction provided above. Eventually, continue with the integration with the `oauth2-proxy` charm.