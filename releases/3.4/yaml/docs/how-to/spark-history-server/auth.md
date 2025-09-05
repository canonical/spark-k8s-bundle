(how-to-spark-history-server-auth)=
# Enable authorization and authentication with the Spark History Server charm

The Charmed Apache Spark solution includes the Spark History charm that enables users to monitor their applications workflows and logs. Natively, this product does not support authentication and authorization that is an essential feature in a production environment. To overcome this limitation, the Spark History Server charm is integrated with the Canonical Identity bundle that offers several authentication and authorization functionalities with Juju.

## Deploy the Identity Bundle and integrate it with the Spark History Server 

In order to enable authentication and authorization on the Spark History Server charm some steps are needed. Here, we assume that you have already deployed Charmed Apache Spark using 
the bundles, as described [here](/), that includes a Spark History Server charm, already configured with an object storage backend. 

In order to enable authentication, we first need to deploy the [identity bundle](https://discourse.charmhub.io/t/iam-bundle-deployment-tutorial/11916).

**_NOTE:_** Please take a look at the Identity Platform tutorial to check that your environment is configured correctly.

```bash
juju deploy identity-platform --channel edge --trust
```

After some minutes the different charms will be deployed and ready to use.

One needed step to properly configure the Identity Bundle is to configure which identity provider we want to use.
This can be done by configuring the `kratos-external-idp-integrator` with the configurations and parameters of your identity provider.

The following is an example of configuration for the Azure Identity provider:

```bash
juju config kratos-external-idp-integrator microsoft_tenant_id=<YOUR_TENANT_ID> provider=microsoft client_id=<YOUR_CLIENT_ID> client_secret=<YOUR_CLIENT_SECRETS>.
```

More information about supported identity providers and other useful information can be found in the [How to manage external identity providers guide](https://discourse.charmhub.io/t/how-to-manage-external-identity-providers/11910)

The relation between the Spark History Server and the Identity bundle is handled by another charm (Oathkeeper) that is offered by the Canonical Identity Team.
This charm enables the protection of endpoints that are behind an ingress, more specifically Traefik.
As the next step, we need to integrate the Spark History Server charm with Traefik.

The Identity bundle deployed two instances of Traefik, we will need to use the one named: `traefik-public`

```bash
juju integrate spark-history-server-k8s traefik-public

```

After it, we can deploy, configure and integrate the Oathkeeper charm with `traefik-public`.

```bash
juju deploy oathkeeper --channel edge --trust
juju config oathkeeper dev=True
juju config traefik-public enable_experimental_forward_auth=True
```

Now we need to integrate Oathkeeper with the ingress and with the Spark History Server charm. The Oathkeeper charm will also need to be integrated with the Kratos charm.

```bash
juju integrate oathkeeper spark-history-server-k8s
juju integrate oathkeeper traefik-public:experimental-forward-auth
juju config kratos dev=true
juju integrate oathkeeper kratos
```

Eventually, you can get the endpoint by running this action:

```bash
juju run traefik-public/0 show-proxied-endpoints
```

When you access the link exposed by Traefik, you will be redirected to your desired identity provider to do the authentication. After a successful authentication, you will be permitted to access the Spark History server endpoint.

## Authorization Management

By default, all authenticated users can access the Spark History Server endpoint. To limit access to a selected set of users, the Spark History Server charm offers the possibility to specify authorized users. This can be done by updating a configuration option. The authorized users (identified by email address) should be specified as a comma-separated list.

```
juju config spark-history-server-k8s authorized-users="user1@canonical.com, user3@canonical.com"
```

