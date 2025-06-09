# Deploy Apache Kyuubi

Charmed Apache Spark can work with [Apache Kyuubi](https://kyuubi.apache.org/), which is a distributed and multi-tenant gateway to provide serverless SQL on lakehouses.
The following guide is to set up Apache Kyuubi for running SQL queries with Charmed Apache Spark.

## Prerequisites

To continue, make sure that you have a properly set up Charmed Apache Spark K8s environment with [Juju](https://documentation.ubuntu.com/juju/3.6/).

See the [How to setup K8s environment](/t/11618) guide for instructions on how to set up with different cloud providers and follow the [Environment setup](/t/13233) page in our Tutorial to set up a service account.

## Initial setup

Add a new Juju model:

```bash
juju add-model kyuubi
```

Deploy the Apache Kyuubi charm:

```bash
juju deploy kyuubi-k8s --trust --channel=latest/edge
```

Open a new terminal window/tab and run the following for a persistent view of the model status:

```bash
juju status --watch=1s
```

Wait for the `kyuubi-k8s` app to have the `blocked` status.

Get back to the previous terminal, then deploy the `spark-integration-hub-k8s`:

```bash
juju deploy spark-integration-hub-k8s --trust --channel=latest/edge
```

Wait for it to initialise (change its status from `waiting` to `active`) and integrate the two charms:

```bash
juju integrate kyuubi-k8s spark-integration-hub-k8s
```

You should see the `blocked` status with the `Missing Object Storage backend` message.

## Object storage setup

Kyuubi currently supports two mutually-exclusive backends for the object storage:

* S3-compatible storage
* Azure DataLake storage

Please see the following sections for guidance on how to configure each.

### S3

For S3-compliant storage, deploy [S3 integrator](https://charmhub.io/s3-integrator):

```bash
juju deploy s3-integrator
```

Configure S3 integrator to use your S3 object storage by setting up endpoint address, bucket, path to folder, and credentials:

```text
juju config s3-integrator endpoint=<ADDRESS> bucket=<BUCKET-NAME> path=<FOLDER-NAME>
juju run s3-integrator/leader sync-s3-credentials access-key=<ACCESS-KEY> secret-key=<SECRET-KEY>
```

As a result, the message `ok: Credentials successfully updated.` should appear.

Now it's time to integrate the `s3-integrator` charm:

```bash
juju integrate s3-integrator spark-integration-hub-k8s
```

After that, `kyuubi-k8s` app becomes blocked with the `Missing authentication database relation` message.

### Azure DataLake

For Azure DataLake storage, deploy [Azure storage integrator](https://charmhub.io/azure-storage-integrator):

```bash
juju deploy azure-storage-integrator
```

Create a Juju secret containing the Azure Storage account secret key, and grant the charm access to this secret.

```text
juju add-secret azure-storage-secret secret-key=XXXXXXX
juju grant-secret azure-storage-secret azure-storage-integrator
```

Configure the charm to use the newly added secret (secret id is displayed in the `add-secret` command's output) to access your Azure DataLake storage account and container:

```text
juju config azure-storage-integrator credentials=<secret-id>
juju config azure-storage-integrator storage-account=XXXX container=XXXX
```

And finally integrate it with the integration hub:

```bash
juju integrate spark-integration-hub-k8s azure-storage-integrator
```

After that, `kyuubi-k8s` app becomes blocked with the `Missing authentication database relation` message.

## Authentication database setup

For the Apache Kyuubi to work with Charmed Apache Spark, it needs a `postgresql-k8s` charm deployed and serve as its authentication database.

Deploy and integrate the `postgresql-k8s` charm:

```bash
juju deploy postgresql-k8s --channel=14/stable --trust kyuubi-users
juju integrate kyuubi-k8s:auth-db kyuubi-users
```

Wait for all statuses to become `active`.

## Connect

Expose the `kyuubi-k8s` app for external connection:

```bash
juju config kyuubi-k8s expose-external=loadbalancer
```

Get Apache Kyuubi connection details:

```bash
juju run kyuubi-k8s/leader get-jdbc-endpoint
juju run kyuubi-k8s/leader get-password
```

Finally, use the external endpoint address and database password to connect with your JDBC-compliant tool of choice:

```bash
beeline -u <ENDPOINT> -n admin -p <PASSWORD>
```

### Connection example

For example, you can use the beeline tool that is a part of the Apache Kyuubi charm.
We recommend deploying a new, dedicated Apache Kyuubi app for that:

```bash
juju deploy kyuubi-k8s --channel=latest/edge --trust beeline
```

Wait for the new app to become `blocked`, but don't integrate it to anything.
Instead, open its SSH terminal, enter bash, and run the beeline tool from inside:

```bash
juju ssh --container=kyuubi beeline/0 bash
/opt/kyuubi/bin/beeline -u jdbc:hive2://10.41.189.148:10009/ -n admin -p 06yJY5OkhcxVhQ0C
```

Wait a few minutes for the Apache Kyuubi to start.
You will see log output with `Pending` phase while Kubernetes pods are starting:

```text
25/05/27 18:29:05 INFO LoggingPodStatusWatcherImpl: Application status for spark-7244f14bac9e4e3f9c505143f4dce374 (phase: Pending)
```

After the initialisation is complete, you will get the Beeline version and prompt:

```text
Connected to: Spark SQL (version 3.4.2)
Driver: Kyuubi Project Hive JDBC Client (version 1.10.1)
Beeline version 1.10.1 by Apache Kyuubi
0: jdbc:hive2://10.41.189.148:10009/> 
```

You can run your SQL commands now, for example:

```sql
create database abc;
use abc;
create table users (id int);
insert into users values (1);
select * from users;
```

## Metastore

To make Apache Kyuubi units stateless, we need to set up external storage for metadata, or metastore.

Deploy a new instance of `postgresql-k8s` charm for the metastore:

```bash
juju deploy postgresql-k8s --trust --channel=14/stable metastore
```

Now integrate Apache Kyuubi app with the metastore:

```bash
juju integrate kyuubi-k8s:metastore-db metastore
```

## High availability

For high availability, add more units for the Apache Kyuubi app:

```bash
juju scale-application kyuubi-k8s 3
```

Now the application is blocked, as it requires ZooKeeper to work in a multi-node mode.
Deploy and relate the ZooKeeper charm:

```bash
juju deploy zookeeper-k8s --channel=3/edge --trust -n 1
juju relate kyuubi-k8s zookeeper-k8s
```

Wait for all the units of the `kyuubi-k8s` application to become active.