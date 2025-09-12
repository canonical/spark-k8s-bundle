(how-to-index)=
# How-To guides

The following guides cover key processes and common tasks for Charmed Apache Spark.
If you are missing a particular how-to guide, feel free to leave us feedback via the
**Give feedback** button above, or [contact us](reference-contacts) directly.

## Deployment

See guides on how to prepare a K8s environment and deploy
Charmed Apache Kafka and Charmed Apache Kyuubi:

* [Set up K8s environment](how-to-deploy-environment)
* [Spark deployment guide](how-to-deploy-spark)
* [Kyuubi deployment guide](how-to-deploy-kyuubi)

## Manage service account

See guides how to manage service account with different tools:

* [Using Spark Integration Hub](how-to-service-accounts-integration-hub)
* [Using Python](how-to-service-accounts-python)
* [Using Spark-client](how-to-service-accounts-spark-client)

## Charmed Apache Kyuubi guides

We have a series of guides for using Charmed Apache Kyuubi with Charmed Apache Spark:

* [Encryption and password](how-to-apache-kyuubi-encryption-and-passwords)
* [External connections](how-to-apache-kyuubi-external-connections)
* [External metastore](how-to-apache-kyuubi-external-metastore)
* [Integrate with apps](how-to-apache-kyuubi-integrate-with-applications)
* [Backups](how-to-apache-kyuubi-back-up-and-restore)
* [Upgrades](how-to-apache-kyuubi-upgrade)

## Monitoring

Monitoring Charmed Apache Spark is typically done with the
[Canonical Observability Stack](https://charmhub.io/topics/canonical-observability-stack).
See our [Monitoring](how-to-monitoring) guide.

## Spark History Server

We have guides for using Spark History Server with Charmed Apache Spark:

* [Authentication and authorisation](how-to-spark-history-server-auth)
* [Expose web GUI](how-to-spark-history-server-expose-web-gui)

## Security

We have a guide for using [self-signed certificates](how-to-self-signed-certificates).

  See also: our [security overview](explanation-security) page.

## Other guides

Advanced features of Charmed Apache Kafka include:

* [Use K8s pods](how-to-use-k8s-pods)
* [Streaming jobs](how-to-streaming-jobs)
* [Use GPU](how-to-use-gpu)

```{toctree}
:titlesonly:
:hidden:

deploy/index
manage-service-accounts/index
apache-kyuubi/index
Monitoring<enable-monitoring.md>
spark-history-server/index
Use K8s pods<use-k8s-pods.md>
Streaming Jobs<streaming-jobs.md>
Use GPU<use-gpu.md>
Self-signed certificates<self-signed-certificates.md>
```
