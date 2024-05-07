## Deploy the Spark History Server 

The Spark History server is a component in the Spark ecosystem that helps you monitor your Spark jobs. In particualar, the History Server enables access to logs of completed/running Spark jobs for viewing and analysis.

Within the Charmed Spark solution, its deployment, configuration and operation is handled by [Juju](https://juju.is/). Therefore, a [Juju charm](https://charmhub.io/spark-history-server-k8s) will be responsible for its management and operations on K8s.

### Requirements

Since Spark History server will be managed by Juju, make sure that:
* you have a Juju client (e.g. via a [SNAP](https://snapcraft.io/juju)) installed in your local machine  
* you are able to connect to a juju controller running on K8s.
* you have read-write permissions (therefore you have an access key, access secret and the s3 endpoint) to a S3-compatible object storage 

To see how to setup a Juju controller on K8s and the juju client, you can refer to existing tutorials and documentation, e.g. [here](https://juju.is/docs/olm/get-started-with-juju) for MicroK8s and [here](https://juju.is/docs/juju/amazon-elastic-kubernetes-service-(amazon-eks)) for AWS EKS. Also refer to the [How-To Setup Environment](/t/charmed-spark-k8s-documentation-how-to-setup-k8s-environment/11618) userguide to install S3-compatible object storage on MicroK8s (MinIO) or EKS (AWS S3). For other backends or K8s distributions other than MinIO on MicroK8s and S3 on EKS (e.g. Ceph, Charmed Kubernetes, GKE, etc), please refer to the documentation or your admin.

### Preparation

#### Juju Model 

Make sure that you have a Juju model where to deploy the Spark History server. In general, we advise to segregate juju applications belonging to different solutions, and therefore
to have a dedicated model for `Spark` components, e.g.

```bash 
juju add-model spark
```

> Note that this will create a K8s namespace where the different juju applications will be deployed to.

#### Setup S3 Bucket

Create a bucket named `history-server` and an path object `spark-events` for storing Spark logs in s3. This can be done in multiple ways depending on the S3 backend interface.
For instance, via Python API, you can install and use the `boto` library, as in the following:

*Install boto*

`pip install boto3`

*Create the S3 bucket*

```python
from botocore.client import Config
import boto3

config = Config(connect_timeout=60, retries={"max_attempts": 0})
session = boto3.session.Session(
    aws_access_key_id=<ACCESS_KEY>, aws_secret_access_key=<SECRET_KEY>
)
s3 = session.client("s3", endpoint_url=<S3_ENDPOINT>, config=config)

s3.create_bucket(Bucket="history-server")
s3.put_object(Bucket="history-server", Key=("spark-events/"))
```

### Deploy Spark History Server

* *Deploy the Spark History Server component*

```bash
juju deploy spark-history-server-k8s -n1 --channel 3.4/stable
```

* *Deploy and configure a [s3-integrator](https://charmhub.io/s3-integrator) charm*

```bash
juju deploy s3-integrator -n1 --channel edge
juju config s3-integrator bucket="history-server" path="spark-events" endpoint=<S3_ENDPOINT>
juju run-action s3-integrator/0 sync-s3-credentials access-key=<ACCESS_KEY> secret-key=<SECRET_KEY> --wait 
```

* *Relate s3-integrator and Spark History server*

```bash 
juju relate s3-integrator spark-history-server-k8s
```

The Spark History server should now be configured to read data from the S3 storage backend. 
Before start using the Spark History server, make sure that the s3-integrator and Spark History server services are active using `juju status`, e.g.  

```bash 
$ juju status
Model  Controller  Cloud/Region        Version  SLA          Timestamp
spark  micro       microk8s/localhost  2.9.43   unsupported  19:12:46+02:00

App                       Version  Status  Scale  Charm                     Channel  Rev  Address         Exposed  Message
s3-integrator                      active      1  s3-integrator             edge      12  10.152.183.253  no       
spark-history-server-k8s           active      1  spark-history-server-k8s  stable     0  10.152.183.100  no      

Unit                         Workload  Agent  Address      Ports  Message
s3-integrator/0*             active    idle   10.1.99.136         
spark-history-server-k8s/0*  active    idle   10.1.99.135 
```

### Expose the Spark History server UI

#### Without Ingress (MicroK8s only)

The Spark History server exposes a UI accessible at ```http://<spark-history-server-ip>:18080```. 

If you are running MicroK8s, you can directly expose it to the local network by enabling DNS

```bash
microk8s enable dns
```

and retrieve the Spark History server POD IP using

```bash
IP=$(kubectl get pod spark-history-server-k8s-0 -n spark --template '{{.status.podIP}}')
```

#### With Ingress

The Spark History server can be exposed outside a K8s cluster by means of an ingress. This is the recommended way in production for any K8s distribution. If you are running on MicroK8s, make sure that you have enabled `metallb`, as shown in the "How-To Setup K8s" userguide. 

Deploy the `traefik-k8s` charm

```bash
juju deploy traefik-k8s --channel latest/candidate --trust
```

and relate with the Spark History server charm

```bash
juju relate traefik-k8s spark-history-server-k8s
```

After the charms settle down into `idle/active` states, fetch the URL of the Spark History server with 

```bash
juju run-action traefik-k8s/0 show-proxied-endpoints --wait
```

This should print a JSON with all the ingress endpoints exposed by the `traefik-k8s` charm. To also exposed the UI outside the local cloud network via a public domain or to enable TLS encryption, please refer to [this userguide](https://discourse.charmhub.io/t/lets-encrypt-certificates-in-the-juju-ecosystem/8704) about integration of `traefik-k8s` with Route53 and Let's Encrypt (note that this is currently only supported on AWS EKS only).

### Run Spark Jobs

When running a Spark job, it is important to provide the correct configuration to write logs to S3, such that these files can be read by the Spark History server. 

Create a configuration file `spark-s3-bindings.conf` with the Spark configuration keys

```properties
# 
spark.eventLog.enabled=true
spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
spark.hadoop.fs.s3a.connection.ssl.enabled=false
spark.hadoop.fs.s3a.path.style.access=true
spark.hadoop.fs.s3a.access.key=<ACCESS_KEY>
spark.hadoop.fs.s3a.endpoint=<S3_ENDPOINT>
spark.hadoop.fs.s3a.secret.key=<SECRET_KEY>
spark.eventLog.dir=s3a://history-server/spark-events/ \
spark.history.fs.logDirectory=s3a://history-server/spark-events/
```

Add these configurations to your Spark service account using the `spark-client` tool:

```bash
$ spark-client.service-account-registry add-config --username <USER> --namespace <NAMESPACE> --properties-file spark-s3-bindings.conf
```

You can now normally submit a Spark job using the `spark-client` tool:

```bash
$ spark-client.spark-submit --username <USER> --namespace <NAMESPACE> --class ...
```

> Note that if you only want to store logs for some jobs, configuration files could also be provided directly to the `spark-client.spark-submit` command via the `--properties-file` argument. 
> Please refer to the dedicated documentation for more information about [managing service account](/t/spark-client-snap-how-to-manage-spark-accounts/8959) and [running Spark jobs](/t/spark-client-snap-tutorial-spark-submit/8953) using the `spark-client` tool.