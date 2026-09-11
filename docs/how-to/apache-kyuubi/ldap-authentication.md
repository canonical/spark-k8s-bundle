---
myst:
  html_meta:
    description: "How-to guide for configuring LDAP authentication for Charmed Apache Kyuubi K8s instead of JDBC authentication."
---

(how-to-apache-kyuubi-ldap-authentication)=
# LDAP Authentication

The Lightweight Directory Access Protocol (LDAP) enables centralised authentication for Kyuubi. This guide shows how to enable LDAP authentication in Charmed Apache Kyuubi K8s charm, so that the users in a LDAP directory can be used to authenticate and run SQL queries with Apache Kyuubi. This guide will also show how such users can be managed with Juju.

## Enable LDAP Authentication

The Charmed Apache Kyuubi K8s charm implements the `ldap-credentials` relation endpoint over the `ldap` interface, which can be used to integrate LDAP provider charms such as GlAuth K8s to enable LDAP authentication.

To enable LDAP authentication, first deploy the GlAuth K8s charm which is a standalone LDAP server:

```shell
juju deploy glauth-k8s glauth --channel latest/stable --trust
```

Then, integrate it with the Charmed Apache Kyuubi K8s charm on the `ldap-credentials` relation:

```shell
juju integrate kyuubi-k8s:ldap-credentials gauth-k8s:ldap
```

The Kyuubi charm by design only supports LDAPS (LDAP with TLS), and thus will stay blocked until it receives LDAPS credentials over the relation. To unblock, enable LDAPS in the GlAuth K8s charm:

```shell
juju config glauth-k8s ldaps_enabled=true
```

For LDAPS to work, GlAuth K8s needs TLS certificates, which is provided by any charm that provides a relation over `tls-certificates` interface. For instance, deploy the `self-signed-certificates` charm, and integrate it with GlAuth K8s:

```shell
juju deploy self-signed-certificates 
juju integrate glauth-k8s:certificates self-signed-certificates
```

```{dropdown} Do **not** use self-signed certificates in production.
:class-container: dropdown-caution
:icon: alert-fill
:class-title: sd-font-weight-normal

In this guide, we use [self-signed certificates](https://en.wikipedia.org/wiki/Self-signed_certificate) provided by the [`self-signed-certificates` operator](https://github.com/canonical/self-signed-certificates-operator).

**This is not recommended for a production environment.**

Check the collection of [Charmhub operators](https://charmhub.io/?q=tls-certificates) that implement the `tls-certificate` interface.
```

The GlAuth K8s uses PostgreSQL database to store the users in the backend. Deploy `postgresql-k8s` charm, and integrate it with GlAuth K8s charm to enable it to store the user information.

```shell
juju deploy postgresql-k8s --channel 16/stable --trust ldap-db
juju integrate glauth-k8s:pg-database ldap-db:database
```

Since the Kyuubi charm needs to connect to GlAuth LDAP server internally, it needs to know the CA certificate to initiate LDAPS connection. Integrate Kyuubi charm with GlAuth K8s charm using `receive-ca-cert` relation endpoint, such that this CA certificate is passed to Kyuubi charm.

```shell
juju integrate kyuubi-k8s:receive-ca-cert glauth-k8s
```

Once the all charms are settled to `active/idle` status, the LDAP users are now able to authenticate with the Charmed Apache Kyuubi K8s charm.

## Manage LDAP Users

The user management in GlAuth K8s charm is done using the `glauth-utils` charm. Deploy the `glauth-utils` charm and integrate it with GlAuth K8s charm:

```shell
juju deploy glauth-utils 
juju integrate glauth-k8s:glauth-auxiliary glauth-utils:glauth-auxiliary
```

The creation, modification and deletion of the users in GlAuth K8s is performed by writing the desired operations in a LDIF (LDAP Data Interchange Format) file, and applying it using the `glauth-utils` charm. For example, the following LDIF content creates an Organization Unit (OU) named `users` and a user named `testuser`, with password `testpassword`.

```ldif
# Create a OU named 'users'
dn: ou=users,dc=glauth,dc=com
objectClass: posixGroup
ou: users
gidNumber: 5511

# Create a user named 'testuser' with password 'testpassword' that belongs to OU 'users'
dn: cn=testuser,ou=users,dc=glauth,dc=com
changetype: add
objectClass: posixAccount
uidNumber: 5512
gidNumber: 5511
cn: testuser
sn: testuser
uid: testuser
mail: testuser@glauth.com
givenName: testuser
userPassword: {SHA256}9f735e0df9a1ddc702bf0a1a7b83033f9f7153a00c29de82cedadc9957289b05
```

```{note}
Note that the value for the key `userPassword` is not the password itself, but the SHA256 hash of the password.
```

For more information on LDIF and additional examples, refer to [these samples](https://github.com/canonical/glauth-utils/blob/main/SAMPLES.md).

Save the LDIF content to a file named `operations.ldif`. Then copy it to `glauth-utils` charm unit, and apply it:

```shell
juju scp operations.ldif glauth-utils/0:/tmp/operations.ldif
juju run glauth-utils/0 apply-ldif path=/tmp/operations.ldif
```

The output similar to the following can be seen in the shell, if the operation is successful:

```text
Sample LDIF file applied successfully
```

Once the LDIF has been applied successfully, the username `testuser` with the password `testpassword` can be used to authenticate with Kyuubi charm.

```shell
spark-client.beeline -u "jdbc://<kyuubi-host>:<kyuubi-port>/" -n testuser -p testpassword
```

### Using custom LDAP search filter

The LDAP authentication can be used to authenticate with Kyuubi charm using custom attributes of the LDAP users. This can be done by providing custom LDAP search filter using the `ldap-search-filter` config option in the Kyuubi charm.

The default search filter used by Kyuubi to for LDAP user discovery is `(|(uid=%s)(cn=%s)(mail=%s))`. This filters the LDAP users that any one of `uid`, `cn` or `mail` attributes matching the provided username.  The `%s` is the placeholder for the username provided during authentication.

For instance, to enable authentication using either of custom attributes `firstName` or `lastName`, a custom search filter `(|(firstName=%s)(lastName=%s))` can be used:

```shell
juju config kyuubi-k8s ldap-search-filter="(|(firstName=%s)(lastName=%s))"
```

## Disable LDAP authentication

The LDAP authentication can be disabled by removing the relation between Kyuubi and GlAuth K8s charm:

```shell
juju remove-relation kyuubi-k8s:ldap-credentials glauth-k8s
juju remove-relation kyuubi-k8s:receive-ca-cert glauth-k8s
```

The Kyuubi charm will then go to `Blocked` state, waiting for authentication relation. As an alternative authentication mode, JDBC authentication can be used with the relation with `postgresql-k8s` charm.
