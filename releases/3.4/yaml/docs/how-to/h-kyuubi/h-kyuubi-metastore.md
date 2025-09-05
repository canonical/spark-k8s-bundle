# External metastore

By default, Apache Kyuubi uses an embedded database to manage the metadata of persistent relational entities.
However, this database is limited to a single unit and is not persisted should the pod be rescheduled.

In a production environment, we recommend deploying an external metastore shared by all Charmed Apache Kyuubi K8s units, that can be backed up and restored as well.

## Enable external metastore

The Charmed Apache Kyuubi K8s charm provides a `metastore-db` integration through the `postgresql_client` interface.

To use it, deploy a Charmed PostgreSQL K8s charm:

```shell
juju deploy postgresql-k8s metastore --channel 14/stable --trust
```

Then, integrate it with the Charmed Apache Kyuubi K8s charm on the `metastore-db` relation:

```shell
juju integrate kyuubi-k8s:metastore-db metastore
```

Once the two charms are settled in `active/idle` status, the metastore is configured and operational.

## Disable external metastore

To stop using the external metastore, remove the integration:

```shell
juju remove-relation kyuubi-k8s:metastore-db postgresql-k8s
```