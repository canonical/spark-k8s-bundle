---
myst:
  html_meta:
    description: "Learn how to deploy and use Charmed Apache Kyuubi on Kubernetes for serverless SQL queries on data lakes with Apache Spark."
---

(tutorial-6-apache-kyuubi)=
# 6. Using Apache Kyuubi

Apache Kyuubi is a gateway to serverless SQL running on Kubernetes, bridging the gap between Apache Spark as a data processing framework and a datalake platform.

This hands-on tutorial stage aims to help you learn how to use Charmed Apache Kyuubi K8s and become familiar with its available operations.

## Environment variables

At this step of the tutorial, you’ll need some environment variables that were set earlier during the environment setup stage.
If you’ve restarted the VM and lost those variables, refresh them by running the following commands:

```bash
export ACCESS_KEY=$(kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_ACCESS_KEY}' | base64 -d)
export SECRET_KEY=$(kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_SECRET_KEY}' | base64 -d)
export S3_ENDPOINT=$(kubectl get service minio -n minio-operator -o jsonpath='{.spec.clusterIP}')
```

## Initial setup

Let's create a fresh Juju model for the Charmed Apache Kyuubi K8s experiments:

```bash
juju add-model datalake
```

To create our simple, minimal datalake, we need an object storage.

### Object storage

We will use the MinIO, installed in the environment setup stage of this tutorial.
Let's set up a new bucket:

```shell
aws s3 mb s3://datalake
```

Now add the `spark-events` directory to the bucket:

```shell
aws s3api put-object --bucket spark-tutorial --key spark-events/
```

You can check the result of directory creation by calling the list of elements in the bucket:

```shell
aws s3 ls spark-tutorial
```

The resulted output should contain the `spark-events` directory we have just created.

To provide access to our object storage, we can use the [S3-integrator](https://charmhub.io/s3-integrator) charm.
Let's deploy the charm first:

```shell
juju deploy s3-integrator --channel 1/stable
```

Now configure the `s3-integrator` application to have access to our object storage:

```shell
juju config s3-integrator bucket=spark-tutorial path="spark-events" endpoint=http://$S3_ENDPOINT
juju run s3-integrator/0 sync-s3-credentials access-key=$ACCESS_KEY secret-key=$SECRET_KEY
```

We will deploy the [Spark Integration Hub K8s charm](https://charmhub.io/spark-integration-hub-k8s) to manage integrations and configure service accounts on Kubernetes.

To deploy it and integrate with the object storage integrator charm:

```shell
juju deploy spark-integration-hub-k8s --channel 3/stable --trust integration-hub
juju integrate integration-hub s3-integrator
```

### Authentication database

We need a database to hold our users. Let's use the [Charmed PostgreSQL K8s charm](https://charmhub.io/postgresql-k8s) for that:

```shell
juju deploy postgresql-k8s --channel 14/stable --trust auth-db
```

### External access

To enable external clients to connect to our datalake, we need the [Data Integrator charm](https://charmhub.io/data-integrator):

```shell
juju deploy data-integrator --channel latest/stable --config database-name=test
```

## Deploy Charmed Apache Kyuubi K8s

We are now ready to deploy the Charmed Apache Kyuubi K8s charm, and integrate it with the previously prepared charms:

```shell
juju deploy kyuubi-k8s --channel 3.4/stable --trust --config expose-external=loadbalancer
juju integrate kyuubi-k8s integration-hub 
juju integrate kyuubi-k8s:auth-db auth-db
juju integrate kyuubi-k8s data-integrator
```

Check the list of charms that have been deployed and their statuses:

```shell
watch -c juju status --relations --color
```

Wait until the status to be active for each charm:

```text
Model              Controller  Cloud/Region        Version  SLA          Timestamp
datalake           microk8s    microk8s/localhost  3.6.8    unsupported  16:43:19+02:00

App                       Version  Status  Scale  Charm                      Channel        Rev  Address         Exposed  Message
auth-db                   14.15    active      1  postgresql-k8s             14/stable      495  10.152.183.19   no
data-integrator                    active      1  data-integrator            latest/stable  181  10.152.183.94   no
integration-hub                    active      1  spark-integration-hub-k8s  3/stable        67  10.152.183.220  no
kyuubi-k8s                1.10     active      1  kyuubi-k8s                 3.4/stable     109  10.152.183.84   no
s3-integrator                      active      1  s3-integrator              1/stable       146  10.152.183.103  no

Unit                         Workload  Agent  Address       Ports  Message
auth-db/0*                   active    idle   10.1.111.95          Primary
data-integrator/0*           active    idle   10.1.111.66
integration-hub/0*           active    idle   10.1.111.101
kyuubi-k8s/0                 active    idle   10.1.111.80
s3-integrator/0*             active    idle   10.1.111.77
```

## Access Charmed Apache Kyuubi K8s

Apache Kyuubi provides an SQL gateway through [Thrift JDBC/ODBC interface](https://spark.apache.org/docs/latest/sql-distributed-sql-engine.html) for end-users.
Get the JDBC endpoint and its credentials with the following command:

```shell
juju run data-integrator/0 get-credentials
```

The resulted output should look like the following:

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

Check your output and locate the `endpoint`, `username`, and `password` values, that we will use to connect using Beeline and DBeaver clients below.

```{note}
By default, there is no data in a freshly installed system.
If you want to generate and upload a sample dataset, feel free to use this [Kyuubi Dataset generator](https://github.com/deusebio/kyuubi-dataset-generation).
```

### Beeline

[Beeline](https://cwiki.apache.org/confluence/display/hive/hiveserver2+clients#HiveServer2Clients-Beeline%E2%80%93CommandLineShell) is a CLI JDBC client, that is available to you via `spark-client`.

Use the `spark-client.beeline` command with the credentials from previous command to access 
the endpoint with the `beeline` JDBC-compliant client:

```shell
spark-client.beeline -u "jdbc:hive2://<endpoints>/" -n <username> -p <password>
```

For example, using the data from the previous output example, the command should look like that:

```shell
spark-client.beeline -u "jdbc:hive2://10.64.140.43:10009/" -n relation_id_15 -p 31rwWzk8wpnhoZvU
```

The client should welcome you with a prompt where you can run SQL queries.

### (Optional) DBeaver

[DBeaver](https://dbeaver.io/) Community is a free cross-platform database GUI tool.
Since it's using graphical user interface, we won't run it in a Multipass VM.

Install DBeaver on the host machine (outside of the Multipass VM) by using the [Downloads page](https://dbeaver.io/download/) or the following command:

```shell
sudo snap install dbeaver-ce
```

Run DBeaver after installation and open Connect to a database window by clicking
the New Database Connection button or pressing the `Ctrl + Shift + N` key combination.
Select Apache Kyuubi and press Next.

Fill in the following fields:

* Connect by -- select URL
* JDBC URL -- use the `uris` value from before. Alternatively, you can prepend the `endpoints` value with the `jdbc:hive2://` and use it instead.
* Username -- use the `username` value
* Password -- use the `password`

Now press Finish and then, the Connect button in the horizontal ribbon menu.
After a successful connection, you can create and run your SQL queries in the right side of the interface.

## High availability

Apache Kyuubi has two major HA features:

* Horizontal scaling
* External metastore

Let's try using both of them.

### Horizontal scaling

Scale out the Apache Kyuubi cluster up to three nodes:

```shell
juju scale-application kyuubi-k8s 3
```

Wait for the deployment to complete and check the model status with the `juju status` command.
The `kyuubi-k8s` units are all in the `blocked` state now, with a message “Missing ZooKeeper integration”.
That is because multi-node Apache Kyuubi deployments require Apache ZooKeeper for synchronisation.

Now, deploy [Apache ZooKeeper K8s](https://charmhub.io/zookeeper-k8s) charm (three nodes, since we want high availability) and integrate it with Apache Kyuubi:

```shell
juju deploy zookeeper-k8s --channel=3/stable --trust -n 3
juju integrate kyuubi-k8s zookeeper-k8s
```

Wait for the deployment to finish by watching the `juju status` until all workloads are `active` and all agents are `idle`.

### External metastore

By default, Apache Kyuubi units in Juju store metadata on the local pod storage.
This means that if a pod is reset or fails, the metadata is lost.

To make metadata persistent, configure an external metastore by deploying Charmed PostgreSQL and integrating it with the Apache Kyuubi charm using the `metastore-db` interface:

```shell
juju deploy postgresql-k8s --trust --channel=14/stable metastore
juju integrate kyuubi-k8s:metastore-db metastore
```

## Enable TLS encryption

TLS is enabled by integrating with the [Self-signed certificates charm](https://charmhub.io/self-signed-certificates).
This charm centralises TLS certificate management consistently and handles operations like providing, requesting, and renewing TLS certificates.

```{note}
For this tutorial, we are using the `self-signed-certificates` charm.
Avoid using self-signed TLS certificates for production environments.
Please refer to the [X.509 certificates post](https://charmhub.io/topics/security-with-x-509-certificates) for an overview of the TLS certificates provider charms and some guidance on how to choose the right one for your use case.
```

Before enabling TLS on Charmed Apache Kyuubi K8s, deploy the `self-signed-certificates` charm to use as a certificate provider:

```shell
juju deploy self-signed-certificates --config ca-common-name="Tutorial CA"
```

Wait for the charm to settle into an `active/idle` state, as shown by the `juju status`.

To enable TLS on Charmed Apache Kyuubi K8s, integrate the `kyuubi-k8s` charm with the `self-signed-certificates` charm:

```shell
juju integrate kyuubi-k8s self-signed-certificates
```

After the charms settle into `active/idle` states, the Charmed Apache Kyuubi K8s endpoint should now accept encrypted traffic.
Requesting the credentials again should now display the certificate:

```shell
juju run data-integrator/0 get-credentials
```

The resulted output should look like the following:

```yaml
kyuubi:
  data: '{"database": "test", "external-node-connectivity": "true", "provided-secrets":
    "[\"mtls-cert\"]", "requested-secrets": "[\"username\", \"password\", \"tls\",
    \"tls-ca\", \"uris\", \"read-only-uris\"]"}'
  database: test
  endpoints: 10.64.140.43:10009
  password: 31rwWzk8wpnhoZvU
  tls: "True"
  tls-ca: |-
    -----BEGIN CERTIFICATE-----
    MIIDMTCCAhmgAwIBAgIUTM5oAAEAuCDfu/gmUnbZ0ei5ZSUwDQYJKoZIhvcNAQEL
    BQAwHjELMAkGA1UEBhMCVVMxDzANBgNVBAMMBmt5dXViaTAeFw0yNTA3MTcxNDM4
    NDRaFw0yNjA3MTcxNDM4NDRaMB4xCzAJBgNVBAYTAlVTMQ8wDQYDVQQDDAZreXV1
    YmkwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDcpvObLJIhUhKaNHbP
    Ju4+XDjHRk6hMJhNdOo76mQHnbJR0c3ZlN8XSdZJ3ekgJOtUe4VY9stVZMZI3LGb
    5/CcxSYZ8oYeWaQ06ST3v7bwZvyJMoInSRMYzLnCIzzXDSVajfLO9bqDKBhw7sPq
    cW5j+FYhLlvqDhU1wXgwwf5KfhIpN70PQnBh1UhdYryU0Qg11caf4N8s+6TN39qu
    hWewhAtADlWrbba/s34yHDSNxl1VVO3cxPmFmYp0UvraecEOsbhRhoX7ZfUlxF+t
    OVjiB/LwWulDgTTFwOPEBku1Zqwuq1Bgl+VD6wGRC2uRsPy2lekDDfi4lDmBREdN
    V6hvAgMBAAGjZzBlMB8GA1UdDgQYBBYEFC5E5p+5CDMi8lwiDZKG4RHRNxVYMCEG
    A1UdIwQaMBiAFgQULkTmn7kIMyLyXCINkobhEdE3FVgwDgYDVR0PAQH/BAQDAgKk
    MA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAEZCONjNJw22Fox/
    7YCRMgb8TTLjybl5aFnpISVe+DbDiceBHrwcP+gJxHTh6cWs8tBrqi2v9ghcYo7S
    Ux7MnRzc4qQTSravR+07guGDeQjaSNk6FX2I5J8shrUD4167ZbPDMoYmcawr4wAZ
    NpIeRGN8IkezA5nMCY0iSrBsrpMYUepDmIPWck8MvrgPGjrR+hZSBq3EJc5J91Os
    QLWGr1RlSjFOfsP8s8n0dkC2UqXmOBN7NZogizGS2mbQvLAg0dSOvueaJsh8dPBU
    eN0aIQcZSPwCK/6iPokfO/afCYZIEmr5LBs81i5B8bQXqnxpltmcNbOQICfqA9XK
    m/BZ6OU=
    -----END CERTIFICATE-----
  uris: jdbc:hive2://10.64.140.43:10009/
  username: relation_id_15
  version: 1.10.2
ok: "True"
```

Test the server certificate by requesting it using `openssl` on the endpoint returned above:

```shell
sudo snap install yq
openssl s_client -showcerts -connect $(juju run data-integrator/0 get-credentials | yq ".kyuubi.endpoints") < /dev/null
```

The resulted output should include issuer CN `Tutorial CA`.

To connect to Charmed Apache Kyuubi K8s using the spark-client's bundled `beeline` client, import the certificate in the spark-client snap:

```shell
juju run data-integrator/0 get-credentials | yq ".kyuubi.tls-ca" > cert.pem
spark-client.import-certificate tutorial-cert cert.pem
```

Then, add `;ssl=true` to the JDBC endpoint you got from the data-integrator charm, for example:

```shell
spark-client.beeline -u "jdbc:hive2://10.64.140.43:10009/;ssl=true" -n relation_id_15 -p 31rwWzk8wpnhoZvU
```

The client should welcome you once again with a prompt where you can run SQL queries.

Congratulations! You are now connected to Charmed Apache Kyuubi K8s using TLS.

