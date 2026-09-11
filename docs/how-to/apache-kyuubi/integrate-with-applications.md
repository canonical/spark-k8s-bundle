---
myst:
  html_meta:
    description: "How-to guide for integrating Charmed Apache Kyuubi with charmed and non-charmed applications using data-integrator and kyuubi_client interface."
---

(how-to-apache-kyuubi-integrate-with-applications)=
# Integrate with applications

This guide shows how to integrate Charmed Apache Kyuubi K8s with both charmed and non-charmed applications.

<!-- For developer information about how to integrate your own charmed application with Charmed Kyuubi, see [](). -->

## Charmed applications

Integrations with charmed applications are supported via the `kyuubi_client` interface.

```{note}
You can see which existing charms are compatible with Kyuubi in the [Integrations](https://charmhub.io/kyuubi-k8s/integrations) tab on Charmhub.
```

### The kyuubi_client interface

To integrate, run

```shell
juju integrate kyuubi-k8s:database <charm>
```

To remove the integration, run

```shell
juju remove-relation kyuubi-k8s <charm>
```

## Non-charmed applications

To integrate with an application outside of Juju, use the [`data-integrator` charm](https://charmhub.io/data-integrator) to create the required credentials and endpoints.

Deploy the `data-integrator` charm:

```shell
juju deploy data-integrator --config database-name=<name>
```

Integrate with Charmed Apache Kyuubi K8s:

```shell
juju integrate data-integrator kyuubi-k8s
```

Use the `get-credentials` action to retrieve credentials from `data-integrator`:

```shell
juju run data-integrator/leader get-credentials
```

```{dropdown} Obtaining credentials in LDAP authentication mode
:class-container: dropdown-caution
:icon: alert-fill
:class-title: sd-font-weight-normal

The `data-integrator` charm's `get-credentials` does not return `username` and `password` in when LDAP authentication is used. This is because in LDAP, the users are managed externally, and thus the username and password should be received externally from the LDAP provider.
```

## Rotate application password

To rotate the passwords of a user created for an integrated application, the associated integration must be removed and created again. This process will generate a new user and password for the application.

```shell
juju remove-relation <charm> kyuubi-k8s
juju integrate <charm> kyuubi-k8s
```

For a non-charmed application, the `data-integrator` is the `<charm>` to remove and re-create the integration with.

