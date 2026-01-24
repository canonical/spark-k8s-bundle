---
myst:
  html_meta:
    description: "Learn about cryptography practices in Charmed Apache Spark including resource checksums, image verification, and source code integrity."
---

(explanation-cryptography)=
# Cryptography

This document describes the cryptography used by Charmed Apache Spark K8s.

## Resource checksums

All three charms in the Charmed Apache Spark solution employ pinned revisions of the workload images they operate on:

* Spark History Server
* Integration Hub for Apache Spark
* Charmed Apache Kyuubi

The Spark History Server and Charmed Apache Kyuubi use different flavours of the
[Charmed Apache Spark Rock image](https://github.com/canonical/charmed-spark-rock/) whereas the Integration Hub for
Apache Spark uses the [Integration Hub for Apache Spark Rock image](https://github.com/canonical/spark-integration-hub-rock).

The Charmed Apache Spark K8s Bundle is a bundle of charms and relations necessary for preparing an end-to-end tested
Apache Spark cluster ready for use. The bundle also pins the revisions of all individual charms and the revisions of
the workload images used by those charms. In Terraform bundles, the pinning of workload images is done with a
revision number, whereas in the YAML bundle, this is done with a SHA252 digest of the image.

All artifacts, that are bundled into Charmed Apache Spark Rock image, Apache Spark Client snap, and Integration Hub
for Apache Spark Rock image are verified against their MD5, SHA256 or SHA512 checksums after the download.
The Spark8t Python library in the rock image is installed from the GitHub repository itself with the version pinned.

## Sources verification

The source code for various Charmed Apache Spark components is stored as follows:

| SN | Component                                                                                               | Source Code |
|----|---------------------------------------------------------------------------------------------------------|-------------|
| 1  | [Charmed Apache Spark Rock](https://github.com/canonical/charmed-spark-rock)                                   | GitHub      |
| 2  | [Apache Spark Client Snap](https://github.com/canonical/spark-client-snap)                                     | GitHub      |
| 3  | [Spark8t Python Library](https://github.com/canonical/spark-k8s-toolkit-py)                             | GitHub      |
| 4  | [Spark History Server Charm](https://github.com/canonical/spark-history-server-k8s-operator)            | GitHub      |
| 5  | [Apache Kyuubi Charm](https://github.com/canonical/kyuubi-k8s-operator)                                        | GitHub      |
| 6  | [Integration Hub for Apache Spark Rock](https://github.com/canonical/spark-integration-hub-rock)                   | GitHub      |
| 7  | [Integration Hub for Apache Spark Charm](https://github.com/canonical/spark-integration-hub-k8s-operator)          | GitHub      |
| 8  | [Apache Spark source code](https://code.launchpad.net/soss/charmed-spark)                               | LaunchPad   |
| 9  | [Apache Hadoop source code](https://code.launchpad.net/soss/hadoop)                                     | LaunchPad   |
| 10 | [Spark History Server Authentication Servlet](https://launchpad.net/soss/charmed-spark-servlet-filters) | LaunchPad   |
| 11 | [Apache Spark Metrics Plugin](https://launchpad.net/soss/spark-metrics)                                        | LaunchPad   |

### LaunchPad

Distributions are built using private repositories only, hosted as part of the
[SOSS namespace](https://launchpad.net/soss) to eventually integrate with Canonical’s standard process for fixing CVEs.
Branches associated with releases are mirrored to a public repository, hosted in the
[Data Platform namespace](https://launchpad.net/~data-platform) to provide the community with the patched source code.

### GitHub

All Charmed Apache Spark artifacts are published and released programmatically using release pipelines implemented via
GitHub Actions. Distributions are published as both GitHub and LaunchPad releases via the
[central-uploader repository](https://github.com/canonical/central-uploader), while charms,
snaps and rocks are published using the workflows of their respective repositories.

All repositories in GitHub are set up with branch protection rules, requiring:

* new commits to be merged to main branches via Pull-Request with at least 2 approvals from repository maintainers
* new commits to be signed (e.g. using GPG keys)
* developers to sign the [Canonical Contributor License Agreement (CLA)](https://ubuntu.com/legal/contributors)

## Encryption

The Spark8t Python library client authenticates to the underlying Kubernetes cluster using a variety of authentication
mechanisms (depending upon how the underlying K8s server is configured) with the use of the `kubeconfig` file.
The communication between K8s and Spark8t is always encrypted by default with authentication enforced.
Since Apache Spark Client snap is a wrapper around this library, the communication between the snap and the K8s cluster
is also authenticated and encrypted.

The Spark8t Python library stores Apache Spark properties as Kubernetes Secrets because these properties may contain
credentials like database password, AWS S3 access key, secret keys, etc.
These are encrypted both at rest and in transit by default by the underlying K8s engine.

Spark History Server, Charmed Apache Kyuubi, and Integration Hub for Apache Spark have capabilities to connect to
S3-compliant cloud storage as an object storage backend, using the S3 Integrator charm, or to an Azure storage,
using the Azure Storage Integrator charm. For providing encryption in transit, S3 and Azure endpoints
should be configured to enable encryption and HTTPS support.

The Apache Kyuubi charm may use PostgreSQL to store the metadata and user/authentication information.
The communication between the charm and the PostgreSQL can be encrypted using TLS certificates.

The Apache Kyuubi charm has capabilities to connect to Apache ZooKeeper for Apache Spark engine discovery.
The communication between Apache Kyuubi and Apache ZooKeeper can be encrypted using a TLS certificate.

The Apache Kyuubi charm exposes a JDBC-compliant endpoint which can be connected using JDBC-compliant clients, like Beeline.
Encryption is currently not supported and it is planned for 25.04.

Apache Spark uses RPC connections for the communication between Driver and Executors.
To secure the communication. Apache Spark provides capabilities to authenticate and encrypt the channels using
shared secrets, that can be configured using dedicated
[Apache Spark properties](https://spark.apache.org/docs/latest/security.html#ssl-configuration).

Encryption for Spark History Server is provided via integration with Traefik, allowing encrypted connections
terminated at the ingress level.

## Authentication

In Charmed Apache Spark, the authentication mechanism exists at the following places:

1. Connection with Apache ZooKeeper
2. Connection with PostgreSQL
3. Connection with object storage 
4. Connection between Spark Driver and Executors
5. Connection with Kubernetes Substrate
6. Kyuubi Client <> Kyuubi Server connection
7. Spark History Server web interface
 
### Connection with Apache Zookeeper

Kyuubi Server authenticates to Apache ZooKeeper using a hash digest mechanism using digested MD5 hashes of username
and password. Usernames and passwords are exchanged using a databag of the relation between Apache Kyuubi
and Apache ZooKeeper. These credentials are stored unencrypted in configuration files in the `/opt/kyuubi/conf`
directory inside the Apache Kyuubi workload container.

### Connection with PostgreSQL

Kyuubi Server authenticates to PostgreSQL using username and password that are exchanged using relation data when the two
applications are integrated. These credentials are stored by Apache Kyuubi in configuration files in the directory
`/opt/kyuubi/conf` inside the workload container. For more information, see the
[Apache Kyuubi official documentation](https://kyuubi.readthedocs.io/en/master/security/jdbc.html).

### Connection to object storage

Authentication is required for Spark jobs, Spark History Server, and Apache Kyuubi to connect to either S3 or
Azure object storages. Credentials are stored in peer-relation data for S3 Integrator and in Juju secrets for
the Azure Object storage, and they are communicated to other charms (Spark History Server, Integration Hub
and Apache Kyuubi) via relation databag.

Integration Hub stores the credentials into Kubernetes Secrets to be made available for Spark jobs.
Driver and executors store configuration files (where credential information is stored) unencrypted in `/etc/spark8t/conf`.
Apache Kyuubi stores credentials in unencrypted configuration files in `/opt/spark/conf`, to be used to configure
Apache Spark Engine, and `/opt/kyuubi/conf`, to be used to configure the Kyuubi Server.
Spark History Server stores credentials in unencrypted configuration files in `/etc/spark/conf`.

### Connection between Spark Driver and Executors

Apache Spark internally has a capability to use a shared secret based RPC authentication mechanism for connection
between driver and executors to establish a secure channel. The authentication is not required but can be enabled
through dedicated [Apache Spark properties](https://spark.apache.org/docs/latest/security.html#network-encryption).

### Connection with Kubernetes Substrate

The connection between Charmed Apache Spark and Kubernetes Substrate can be authenticated using various mechanisms
like certificate based authentication, password based authentication, etc. which depends on how the underlying
Kubernetes substrate is configured.

### Kyuubi Client <> Kyuubi Server Connection

The Kyuubi Client (aka JDBC Client) can connect with the Kyuubi Server endpoint (aka JDBC endpoint) using
a pair of username and password provided in the query. Apache Kyuubi charm internally implements this authentication
by storing the list of users and their passwords stored as plain text in a PostgreSQL database.
For more information about the Kyuubi Client, see the
[Apache Kyuubi official documentation](https://kyuubi.readthedocs.io/en/master/client/index.html).

### Spark History Server web interface

The Spark History Server provides authentication integrated using the Canonical Identity Platform in combination
with a custom design [servlet filter](https://code.launchpad.net/~data-platform/soss/+source/charmed-spark-servlet-filters/+git/charmed-spark-servlet-filters).
This feature can be enabled by following the steps in the
[Spark History Server authorisation How-to guide](https://charmhub.io/spark-k8s-bundle/docs/h-history-server-authorization).
