---
myst:
  html_meta:
    description: "Learn how to enable TLS encryption and manage passwords for Charmed Apache Kyuubi K8s using Juju secrets and certificate relations."
---

(how-to-apache-kyuubi-encryption-and-passwords)=
# Manage encryption and passwords

The Charmed Apache Kyuubi K8s charm supports TLS encryption for data in transit and uses [Juju secrets](https://documentation.ubuntu.com/juju/latest/reference/secret/#secret) to securely store and manage passwords.

This guide shows how to enable TLS encryption, manage encryption keys, retrieve certificate chain, and manage passwords.

## Manage encryption

The Charmed Apache Kyuubi K8s charm implements the Requirer side of the [`tls-certificates/v4`](https://charmhub.io/tls-certificates-interface/libraries/tls_certificates) charm relation.

### Enable encryption

To enable encryption, you should first deploy a TLS certificates Provider charm that implements the Provider side of the relation and then, integrate the charms.

For this guide, we will use self-signed certificates, but similar approach can be employed for other TLS certificate providers.

```{note}
Avoid using self-signed TLS certificates in production environments.

Please refer to the [X.509 certificates post](https://charmhub.io/topics/security-with-x-509-certificates) for an overview of the TLS certificates Providers charms and some guidance on how to choose the right charm for your use case.
```

Deploy certificate provider charm, for example:

```shell
juju deploy self-signed-certificates --channel=1/stable
```

Add necessary configuration parameters:

```shell
juju config self-signed-certificates ca-common-name="Test CA"
```

Integrate the certificate provider charm with Charmed Apache Kyuubi:

```shell
juju integrate <tls-certificates> kyuubi-k8s
```

where `<tls-certificates>` is the name of the TLS certificate provider charm deployed.

### Disable encryption

To disable TLS encryption, remove the relation:

```shell
juju remove-relation <tls-certificates> kyuubi-k8s
```

### Manage keys

Updates to private keys for certificate signing requests (CSR) can be made via the `tls-client-private-key` configuration option.

If this configuration option is not set, the charm will generate a new private key and use it instead.

To generate a shared internal key:

```shell
openssl genrsa -out internal-key.pem 3072
```

Create a new Juju secret using the content of the shared key file:

```shell
juju add-secret kyuubi-tls-secret private-key#file=internal-key.pem
```

The above command returns a secret id, for example: `secret:d1seounmp25c76bq4ha0`.

To grant access for an application to the secret, run `juju grant-secret` command, for example:

```shell
juju grant-secret kyuubi-tls-secret kyuubi-k8s
```

Finally, configure the application to use the secret using the secret id from before:

```shell
juju config kyuubi-k8s tls-client-private-key=secret:d1seounmp25c76bq4ha0
```

To rotate a private key, update the associated secret:

```shell
juju update-secret kyuubi-tls-secret private-key#file=new-internal-key.pem
```

> See also: `juju update-secret` command [reference](https://documentation.ubuntu.com/juju/3.6/reference/juju-cli/list-of-juju-cli-commands/update-secret/).

### Retrieve the certificate chain

To retrieve the certificate in use, use the `data-integrator` charm:

```shell
juju run data-integrator/0 get-credentials | yq ".kyuubi.tls-ca"
```

## Manage passwords

Charmed Apache Kyuubi K8s uses [Juju secrets](https://documentation.ubuntu.com/juju/latest/reference/secret/#secret) to manage passwords.

> See also: [Juju | How to manage secrets](https://documentation.ubuntu.com/juju/latest/howto/manage-secrets/#manage-secrets)

### Create a password

Create a secret in Juju containing one or more user passwords:

```shell
juju add-secret <secret_name> admin=<password>
```

The above outputs a secret URI, which you need for configuring `system-users` configuration parameter.

Without a valid secret granted to the application, the admin user uses an automatically created password.

To grant the secret to the `kyuubi-k8s` charm:

```shell
juju grant-secret <secret_name> kyuubi-k8s
```

### Configure the system-users

To set the `system-users` configuration option to the secret URI:

```shell
juju config charm-app system-users=<secret_URI>
```

When the `system-users` configuration option is set, the charm:

* Uses the specified secret instead of the auto generated one.
* Updates the passwords of the internal `system-users` in its user database.

If the configuration option is **not** specified, the charm automatically generates passwords for the internal system-users and store them in a secret.

### Retrieve a password

To retrieve the password of an internal system-user, run the `juju show-secret` command with the respective secret URI.

### Update a password

To update a password, update the associated secret:

```text
juju update-secret <secret_name> admin=<new_password>
```

