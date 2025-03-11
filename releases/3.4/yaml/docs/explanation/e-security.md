# Security hardening guide

This document provides an overview of security features and guidance for hardening the security of [Charmed Apache Spark K8s](https://github.com/canonical/spark-k8s-bundle), including setting up and managing a secure environment.

## Environment

The environment where applications operate can be divided in two components:

1. Kubernetes
2. Juju 

### Kubernetes

Charmed Apache Spark can be deployed on top of several Kubernetes distributions. 
The following table provides references for the security documentation for the 
main supported cloud platforms.

| Cloud              | Security guide                                                                                                                                                                                                                                                                                                                                   |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Charmed Kubernetes | [Security in Charmed Kubernetes](https://ubuntu.com/kubernetes/docs/security)                                                                                                                                                                                                                                                                    |
| AWS EKS            | [Best Practices for Security, Identity and Compliance](https://aws.amazon.com/architecture/security-identity-compliance), [AWS security credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/security-creds.html#access-keys-and-secret-access-keys), [Security in EKS](https://docs.aws.amazon.com/eks/latest/userguide/security.html) | 
| Azure AKS          | [Azure security best practices and patterns](https://learn.microsoft.com/en-us/azure/security/fundamentals/best-practices-and-patterns), [Managed identities for Azure resource](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/), [Security in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-security)                                                      |

### Juju 

Juju is the component responsible for orchestrating the entire lifecycle, from deployment to Day 2 operations, of 
all applications. Therefore, Juju must be set up securely. For more information, see the
[Juju security page](/t/juju-security/15684) and the [How to harden your deployment guide](https://juju.is/docs/juju/harden-your-deployment).

#### Cloud credentials

When configuring the cloud credentials to be used with Juju, ensure that the users have correct permissions to operate at the required level on the Kubernetes cluster. 
Juju superusers responsible for bootstrapping and managing controllers require elevated permissions to manage several kind of resources. For this reason, the 
K8s user used for bootstrapping and managing the deployments should have full permissions, such as: 

* create, delete, patch, and list:
    * namespaces
    * services
    * deployments
    * stateful sets
    * pods
    * PVCs

In general, it is common practice to run Juju using the admin role of K8s, to have full permissions on the Kubernetes cluster. 

#### Juju users

It is very important that juju users are set up with minimal permissions depending on the scope of their operations. 
Please refer to the [User access levels](https://juju.is/docs/juju/user-permissions) documentation for more information on the access level and corresponding abilities 
that the different users can be granted. 

Juju user credentials must be stored securely and rotated regularly to limit the chances of unauthorized access due to credentials leakage.

## Applications

In the following, we provide guidance on how to harden your deployment using:

1. Base Images
2. Apache Spark Security Upgrades
3. Encryption 
4. Authentication
5. Monitoring and Auditing

### Base images

Charmed Apache Spark K8s runs on top of a set of Rockcraft-based images, all based on the same Apache Spark distribution binaries, 
available in the [Apache Spark release page](https://launchpad.net/spark-releases), on top of Ubuntu 22.04. 
The images that can be found in the [Charmed Apache Spark rock images GitHub repo](https://github.com/canonical/charmed-spark-rock) are used as the base 
images for pods both for Spark jobs and charms. 
The following table summarises the relation between the component and its underlying base image. 

| Component                          | Image                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Spark Job (Driver)                 | [`charmed-spark`](https://github.com/orgs/canonical/packages/container/package/charmed-spark)               |
| Spark Job (Executor)               | [`charmed-spark`](https://github.com/orgs/canonical/packages/container/package/charmed-spark)               |
| Spark History Server               | [`charmed-spark`](https://github.com/orgs/canonical/packages/container/package/charmed-spark)               |
| Charmed Apache Kyuubi                             | [`charmed-spark-kyuubi`](https://github.com/orgs/canonical/packages/container/package/charmed-spark-kyuubi) |
| Spark Job (Driver) - GPU Support   | [`charmed-spark-gpu`](https://github.com/orgs/canonical/packages/container/package/charmed-spark-gpu)       |
| Spark Job (Executor) - GPU Support | [`charmed-spark-gpu`](https://github.com/orgs/canonical/packages/container/package/charmed-spark-gpu)       |
| Integration Hub                    | [`spark-integration-hub`](https://github.com/orgs/canonical/packages/container/package/spark-integration-hub)                    |

New versions of the Charmed Apache Spark images may be released to provide patching of vulnerabilities (CVEs). 

### Charmed operator security upgrades

Charmed Apache Spark K8s operators, including Spark History server, Charmed Apache Kyuubi, and Integration Hub, install a pinned revision of the 
Charmed Apache Spark images outlined in the previous table to provide reproducible and secure environments. 
New versions of Charmed Apache Spark K8s operators may therefore be released to provide patching of vulnerabilities (CVEs). 
It is important to refresh the charm regularly to make sure the workload is as secure as possible. 
<!-- For more information on how to refresh the charm, see the [how-to refresh](https://juju.is/docs/juju/juju-refresh) guide and other data-platform guide -->

### Encryption

We recommend deploying Charmed Apache Spark K8s with encryption enabled for securing the communication between components, whenever available and supported by the server and client applications.
In the following, we provide further information on how to encrypt the various data flow between the different components of the solution:

* Client <> Kubernetes API connections
* Object storage connections
* Apache Kyuubi <> PostgreSQL connection
* Apache Kyuubi <> Apache ZooKeeper connection
* Spark History Server client connection 
* Kyuubi Client <> Kyuubi Server connection
* Spark jobs communications

#### Client <> Kubernetes API connections

Make sure that the API service of Kubernetes is correctly encrypted, and it exposes HTTPS protocol. Please refer to the documentation above
for the main substrates and/or the documentation of your distribution. Please ensure that the various components of the solution, 
e.g. `spark-client`, `pods`, etc, are correctly configured with the trusted CA certificate of the K8s cluster. 

#### Object storage connections

Make sure that the object storage service is correctly encrypted, and it exposes HTTPS protocol. Please refer to the documentation of your 
object storage backend to make sure this option is supported and enabled. Please ensure that the various components of the solution, 
e.g. `spark-client`, `pods`, etc, are correctly configured with the trusted CA certificate of the K8s cluster. 
See the [how-to manage certificates](/t/charmed-spark-k8s-documentation-using-self-signed-certificates/14898) guide for more information.

#### Apache Kyuubi <> PostgreSQL connection 

Charmed Apache Kyuubi integration with PostgreSQL can be secured by enabling encryption for the PostgreSQL K8s charm. 
See the [PostgreSQL K8s how-to enable TLS](/t/charmed-postgresql-k8s-how-to-enable-tls-encryption/9593) user guide for more information on 
how to enable and customize encryption. 

#### Apache Kyuubi <> Apache ZooKeeper connection

Charmed Apache Kyuubi integration with Apache ZooKeeper can be secured by enabling encryption for the Apache ZooKeeper K8s charm. 
See the [Apache Kafka K8s how-to enable TLS](/t/charmed-kafka-k8s-documentation-how-to-enable-encryption/10289) user guide for more information on 
how to enable and customize encryption for Apache ZooKeeper. 

#### Spark History Server client connection 

Spark History Server implements encryption terminated at ingress-level. Therefore, internal Kubernetes communication between ingress and Spark History Server is 
unencrypted. To enable encryption, see the [how-to expose Spark History Server](/t/charmed-spark-k8s-documentation-how-to-expose-history-server/14297) user guide. 

#### Kyuubi Client <> Kyuubi Server connection

The Apache Kyuubi charm exposes a JDBC-compliant endpoint which can be connected using JDBC-compliant clients, like Beeline. 
Encryption is currently not supported and it is planned for 25.04.

#### Spark jobs communications

To secure the RPC channel used for communication between driver and executor, use the [dedicated Apache Spark properties](https://spark.apache.org/docs/latest/security.html#ssl-configuration). 
Refer to the [how-to manage spark accounts](/t/spark-client-snap-how-to-manage-spark-accounts/8959) for more information on how to customize the 
Apache Spark service account with additional properties, or the [Spark Configuration Management](/t/charmed-spark-documentation-explanation-components/11685) explanation page for more information on how Spark workload can be further configured.

### Authentication

Charmed Apache Spark K8s provides external authentication capabilities for:

1. Kubernetes API
2. Spark History Server
3. Kyuubi JDBC endpoint

#### Kubernetes API

Authentication to the Kubernetes API follows standard implementations, as described in the [upstream Kubernetes documentation](https://kubernetes.io/docs/reference/access-authn-authz/authentication/). 
Please make sure that the distribution being used supports the authentication used by clients, and that the Kubernetes cluster has been correctly configured. 

Generally, client applications store credentials information locally in a `KUBECONFIG` file. 
On the other hand, pods created by the charms and the Spark Job workloads receive credentials via shared secrets, mounted to the default locations `/var/run/secrets/kubernetes.io/serviceaccount/`. 
See the [upstream documentation](https://kubernetes.io/docs/tasks/run-application/access-api-from-pod/#directly-accessing-the-rest-api) for more information.

#### Spark History Server

Authentication can be enabled in the Spark History Server when exposed using Traefik by leveraging on the [Oath Keeper](https://charmhub.io/oathkeeper) integration, that provides 
a cloud native Identity & Access Proxy (IAP) and Access Control Decision API able to authenticates, authorizes, 
and mutates incoming HTTP(s) requests, fully-integrated with the Canonical Identity Platform.

Refer to the [how-to enable authorization in the Spark history server](/t/charmed-spark-k8s-documentation-how-to-enable-authentication-on-the-spark-history-server-charm/13563) user guide 
for more information. From a permission-wise point of view, white lists of authorised users 
can be provided using the Spark History Server [charm configuration option](https://charmhub.io/spark-history-server-k8s/configurations?channel=3.4/edge). 

#### Kyuubi JDBC endpoint

Authentication can be enabled for Charmed Apache Kyuubi via its integration with PostgreSQL charm on the `auth-db` interface. Currently, only one admin user is enabled, whose credentials can be retrieved 
using the [`get-jdbc-endpoint` action](https://charmhub.io/kyuubi-k8s/actions#get-jdbc-endpoint).

### Monitoring and auditing

Charmed Apache Spark provides native integration with the [Canonical Observability Stack (COS)](https://charmhub.io/topics/canonical-observability-stack).
To reduce the blast radius of infrastructure disruptions, the general recommendation is to deploy COS and the observed application into 
separate environments, isolated from one another. Refer to the [COS production deployments best practices](https://charmhub.io/topics/canonical-observability-stack/reference/best-practices) page
for more information. 

For more information on how to enable and customise monitoring with COS, see the [Guide](/t/charmed-spark-k8s-documentation-enable-monitoring/13063).

## Additional resources

For further information and details on the security and cryptographic specifications used by Charmed Apache Spark, please refer to the [Cryptography](/t/15795).