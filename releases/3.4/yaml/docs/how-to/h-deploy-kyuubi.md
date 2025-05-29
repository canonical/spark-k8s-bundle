# Deploy Apache Kyuubi

Charmed Apache Spark can work with [Apache Kyuubi](https://kyuubi.apache.org/), which is a distributed and multi-tenant gateway to provide serverless SQL on lakehouses.
The following guide is to set up Apache Kyuubi for running SQL queries with Charmed Apache Spark.

## Prerequisites

To continue, make sure that you have a properly set up Charmed Apache Spark K8s environment with [Juju](https://documentation.ubuntu.com/juju/3.6/).

See the [How to setup K8s environment](/t/11618) guide for instructions on how to set up with different cloud providers or follow our the [Environment setup](/t/13233) page in our Tutorial to set up a microk8s environment.

## Initial setup

Check the list of models available:

```bash
juju models
```

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

To set up an object storage backend, deploy S3 integrator:

```bash
juju deploy s3-integrator
```

After the S3 integrator is deployed, you need to configure it to use your S3 object storage by setting up endpoint address, bucket, path to folder, and credentials:

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

## Authentication database setup

For the Apache Kyuubi to work with Charmed Apache Spark, it needs a `postgresql-k8s` charm deployed and serve as its authentication database.

Deploy and integrate the database charm:

```bash
juju deploy postgresql-k8s --channel=14/stable --trust
juju integrate kyuubi-k8s:auth-db postgresql-k8s
```

Wait for all statuses to become `active`.

## Connect

Expose the `kyuubi-k8s` app for external connection:

```bash
juju config kyuubi-k8s expose-external=loadbalancer
```

Get database connection details:

```bash
juju run kyuubi-k8s/leader get-jdbc-endpoint
juju run kyuubi-k8s/leader get-password
```

Finally, use the external endpoint address and database password to connect with your JDBC-compliant tool of choice:

```bash
beeline -u <ENDPOINT> -n admin -p <PASSWORD>
```

### Connection example

For example, you can use the beeline tool that is a part of the Charmed Apache Kyuubi charm.
We recommend deploying a new, dedicated Kyuubi app for that:

```bash
juju deploy kyuubi-k8s --channel=latest/edge --trust beeline
```

Wait for the new app to become `blocked`, but don't integrate it to anything.
Instead, open its SSH terminal, enter bash, and run the beeline tool from inside:

```bash
juju ssh --container=kyuubi beeline/0
bash
/opt/kyuubi/bin/beeline -u jdbc:hive2://10.41.189.148:10009/ -n admin -p 06yJY5OkhcxVhQ0C
```

Wait a few minutes for the Apache Kyuubi to start.
You will see log output with `Pending` phase while kubernetes pods are starting:

```text
25/05/27 18:29:05 INFO LoggingPodStatusWatcherImpl: Application status for spark-7244f14bac9e4e3f9c505143f4dce374 (phase: Pending)
```

After the intialisation is complete, you will get the Beeline version and prompt:

```text
Connected to: Spark SQL (version 3.4.2)
Driver: Kyuubi Project Hive JDBC Client (version 1.10.1)
Beeline version 1.10.1 by Apache Kyuubi
0: jdbc:hive2://10.41.189.148:10009/> 
```

You can run your SQL commands now, for example: `show databases;`.
