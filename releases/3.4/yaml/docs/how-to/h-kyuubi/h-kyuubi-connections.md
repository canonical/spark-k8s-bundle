# External connections and metastore

To expose Charmed Apache Kyuubi K8s externally, use the `expose-external` configuration option. Possible values are: `false`, `nodeport`, and `loadbalancer`.

## Enable external connections

By default (when `expose-external=false`), Charmed Apache Kyuubi K8s creates a K8s service of type `ClusterIP` which it provides as endpoints to the related client applications.
These endpoints are only accessible from within the K8s namespace (or Juju model) where the Charmed Apache Kyuubi K8s is deployed.

To make Charmed Apache Kyuubi K8s accessible from outside of Kubernetes, set the `expose-external` parameter to `loadbalancer` or `nodeport`.

[note]
We recommend exposing the service using the `loadbalancer` option.
[/note]

When `expose-external` is set to `loadbalancer`, Charmed Apache Kyuubi K8s will provide as endpoint the K8s LoadBalancer service IP (or hostname, depending on your K8s cluster provider) and port.

```shell
juju config kyuubi-k8s expose-external=loadbalancer
```

Wait for the application to settle up with the `active` / `idle` status and retrieve credentials:

```shell
juju run data-integrator/0 get-credentials
```

The output of this command contains both endpoint and credentials, for example:

```yaml
kyuubi:
  data: '{"database": "test", "external-node-connectivity": "true", "provided-secrets":
    "[\"mtls-cert\"]", "requested-secrets": "[\"username\", \"password\", \"tls\",
    \"tls-ca\", \"uris\", \"read-only-uris\"]"}'
  database: test
  endpoints: 10.64.140.43:10009
  password: 31rwWzk8wpnhoZvU
  tls: "False"
  uris: jdbc:hive2://10.64.140.43:10009/
  username: relation_id_15
  version: 1.10.2
ok: "True"
```

## Enable external metastore

By default, Apache Kyuubi uses an embedded database to manage the metadata of persistent relational entities.
However, this database is limited to a single unit and is not persisted should the pod be rescheduled.

In a production environment, we recommend deploying an external metastore shared by all Charmed Apache Kyuubi K8s units, that can be backed up and restored as well.

The Charmed Apache Kyuubi K8s charm provides a `metastore-db` integration through the `postgresql_client` interface.

To use it, deploy a Charmed PostgreSQL K8s charm:

```shell
juju deploy postgresql-k8s --channel 14/stable --trust
```

Then, integrate it with the Charmed Apache Kyuubi K8s charm on the `metastore-db` relation:

```shell
juju integrate kyuubi-k8s:metastore-db postgresql-k8s
```

Once the two charms are settled in `active/idle` status, the metastore is configured and operational.

<!-- A guide on how to backup and restore the metastore can be find [here](#TODO). -->

## Disable external metastore

To stop using the external metastore, remove the integration:

```shell
juju remove-relation kyuubi-k8s:metastore-db postgresql-k8s
```