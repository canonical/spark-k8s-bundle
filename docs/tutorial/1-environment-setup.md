(tutorial-1-environment-setup)=
# 1. Environment setup

Charmed Apache Spark solution is based on the `spark-client` snap that can run Spark jobs on a Kubernetes cluster.

In this step of the tutorial, we will prepare a lightweight K8s environment, `spark-client` snap, and some additional components required for this tutorial. We are going to use [Multipass](https://canonical.com/multipass) to create a virtual environment and set up the following software:

* [MicroK8s](https://microk8s.io/) — a lightweight Kubernetes that can run locally
* [Spark-client snap](https://snapcraft.io/spark-client) — a snap that bundles client-side scripts to manage, configure, and run Apache Spark jobs on a Kubernetes cluster
* [MiniO](https://min.io/) — S3-compliant object storage
* [Juju](https://juju.is/) — Canonical's orchestration system

## Minimum system requirements

Before we start, make sure your machine meets the following minimal requirements:

* Ubuntu 22.04 (jammy) or later (the tutorial has been prepared and tested to work on 24.04)
* 10 GB of RAM
* 5 CPU cores
* At least 50 GB of available storage
* Access to the internet for downloading the required snaps and charms

## Virtual machine

Use Multipass to start a new Ubuntu virtual machine with the following recommended parameters:

```bash
multipass launch --cpus 4 --memory 8G --disk 50G --name spark-tutorial 24.04
```

```{note}
See also:

* [How to create an instance](https://documentation.ubuntu.com/multipass/latest/how-to-guides/manage-instances/create-an-instance/#create-an-instance-with-a-specific-image) guide from Multipass documentation
* [`multipass launch` command reference](https://documentation.ubuntu.com/multipass/latest/reference/command-line-interface/launch/)
```

Check the status of the provisioned virtual machine:

```bash
multipass list
```

Connect to the virtual machine:

```bash
multipass shell spark-tutorial
```

From now on, unless stated otherwise, we will work inside this virtual machine's environment.
For clarity, we will refer to it as VM, while the host machine that runs the Multipass will be called Host.

## MicroK8s

Charmed Apache Spark is developed to be run on top of a Kubernetes cluster.
For the purpose of this tutorial we will be using a lightweight Kubernetes: [MicroK8s](https://microk8s.io/).

Installing MicroK8s is as simple as running the following command:

```bash
sudo snap install microk8s --channel=1.32-strict/stable
```

Make sure to install the `1.32-strict/stable` version of MicroK8s which was tested to work with all the components of this tutorial.

### Configuration

Let's configure MicroK8s so that the currently logged-in user has admin rights to the cluster.

First, set an alias `kubectl` that can be used instead of `microk8s.kubectl`:

```bash
sudo snap alias microk8s.kubectl kubectl
```

Then, add the current user into `microk8s` group:

```bash
sudo usermod -a -G snap_microk8s ${USER}
```

Create and provide ownership of `~/.kube` directory to the current user:

```bash
mkdir -p ~/.kube
sudo chown -f -R ${USER} ~/.kube
```

Put the group membership changes into effect:

```bash
newgrp snap_microk8s
```

Check the status of the MicroK8s:

```bash
microk8s status --wait-ready
```

When the MicroK8s cluster is running and ready, you should see an output similar to the following:

```text
microk8s is running
high-availability: no
...
addons:
  enabled:
    dns                  # (core) CoreDNS
    ha-cluster           # (core) Configure high availability on the current node
    helm                 # (core) Helm - the package manager for Kubernetes
    helm3                # (core) Helm 3 - the package manager for Kubernetes
  disabled:
    cert-manager         # (core) Cloud native certificate management
...
```

Let's generate a Kubernetes configuration file using MicroK8s and write it to `~/.kube/config`. 
This is where `kubectl` looks for the Kubeconfig file by default.

```bash
microk8s config | tee ~/.kube/config
```

Now let's enable a few add-ons for using features like role based access control, usage of local volume for storage, and load balancing.

```bash
sudo microk8s enable rbac
sudo microk8s enable storage hostpath-storage

sudo apt install -y jq
IPADDR=$(ip -4 -j route get 2.2.2.2 | jq -r '.[] | .prefsrc')
sudo microk8s enable metallb:$IPADDR-$IPADDR
```

Wait for the commands to finish running and check the list of enabled add-ons:

```bash
microk8s status --wait-ready
```

The output of the command should look similar to the following:

```text
microk8s is running
...
addons:
  enabled:
    dns                  # (core) CoreDNS
    ha-cluster           # (core) Configure high availability on the current node
    helm                 # (core) Helm - the package manager for Kubernetes
    helm3                # (core) Helm 3 - the package manager for Kubernetes
    hostpath-storage     # (core) Storage class; allocates storage from host directory
    metallb              # (core) Loadbalancer for your Kubernetes cluster
    storage              # (core) Alias to hostpath-storage add-on, deprecated
...
```

The MicroK8s setup is complete.

## The `spark-client` snap

For Apache Spark jobs to be running run on top of Kubernetes, a set of resources (service account, associated roles, role bindings etc.) need to be created and configured.
To simplify this task, the Charmed Apache Spark solution offers the `spark-client` snap. Install the snap: 

```bash
sudo snap install spark-client --channel 3.4/edge
```

Let's create a Kubernetes namespace for us to use as a playground in this tutorial.

```bash
kubectl create namespace spark
```

We will now create a Kubernetes service account that will be used to run the Spark jobs. The creation of the service account can be done using the `spark-client` snap, which will create necessary roles, role bindings and other necessary configurations along with the creation of the service account:

```bash
spark-client.service-account-registry create \
  --username spark --namespace spark
```

This command does a number of things in the background. First, it creates a service account in the `spark` namespace with the name `spark`. Then it creates a role with name `spark-role` with all the required RBAC permissions and binds that role to the service account by creating a role binding. 

These resources can be viewed with `kubectl get` commands as follows:

```bash
kubectl get serviceaccounts -n spark
kubectl get roles -n spark
kubectl get rolebindings -n spark
```

<details>

<summary> Output example</summary>

```text
kubectl get serviceaccounts -n spark
NAME      SECRETS   AGE
default   0         5m41s
spark     0         2m49s


kubectl get roles -n spark
NAME         CREATED AT
spark-role   2025-04-16T09:13:00Z

kubectl get rolebindings -n spark
NAME                 ROLE              AGE
spark-role-binding   Role/spark-role   2m48s
```

</details>

Now, launch a PySpark shell using the service account you created earlier to verify that it works:

```bash
spark-client.pyspark \
  --username spark --namespace spark
```

The resulted output should include a welcome screen from PySpark:

```text
Welcome to
      ____              __
     / __/__  ___ _____/ /__
    _\ \/ _ \/ _ `/ __/  '_/
   /__ / .__/\_,_/_/ /_/\_\   version 3.4.2
      /_/

Using Python version 3.10.12 (main, Jan 17 2025 14:35:34)
Spark context Web UI available at http://10.181.60.136:4040
Spark context available as 'sc' (master = k8s://https://10.181.60.136:16443, app id = spark-627fb48be4da4315b3716e71a7613baf).
SparkSession available as 'spark'.
>>> 
```

Press `CTRL + D` to exit PySpark shell.

The basic Apache Spark setup is now complete: you have a Kubernetes environment and a configured `spark-client` snap ready to use it. We will get back to using them in later steps of the tutorial.

Next, we'll continue to set up additional software needed for Spark History Server and object storage that are also used during this tutorial.

## Juju

[Juju](https://juju.is/) is an Operator Lifecycle Manager (OLM) for clouds, bare metal, LXD or Kubernetes.
We'll use `juju` to deploy and manage the Spark History Server and a number of other applications later to be integrated with Apache Spark. 

To install and configure a `juju` client using a snap:

```bash
sudo snap install juju 
mkdir -p ~/.local/share
```

Juju can automatically detects all available clouds on our local machine (VM) without the need of additional setup or configuration. 
You can verify this by running `juju clouds` command that should produce an output similar to the following:

```text
Only clouds with registered credentials are shown.
There are more clouds, use --all to see them.
You can bootstrap a new controller using one of these clouds...

Clouds available on the client:
Cloud      Regions  Default    Type  Credentials  Source    Description
localhost  1        localhost  lxd   0            built-in  LXD Container Hypervisor
microk8s   1        localhost  k8s   0            built-in  A Kubernetes Cluster
```

As you can see, Juju has detected LXD as well as K8s installation in the system.
For us to be able to deploy Kubernetes charms, let's bootstrap a Juju controller in the `microk8s` cloud:

```bash
juju bootstrap microk8s spark-tutorial
```

The creation of the new controller can be verified with the `juju controllers` command.
The output of the command should be similar to:

```text
Use --refresh option with this command to see the latest information.

Controller       Model  User   Access     Cloud/Region        Models  Nodes  HA  Version
spark-tutorial*  -      admin  superuser  microk8s/localhost       1      1   -  3.6.5
```

The Juju setup is complete.

## MinIO

Apache Spark can be configured to use S3 for object storage.
However, for this tutorial, instead of AWS S3, we'll use [MinIO](https://min.io/): a lightweight S3-compatible object storage.
It is available as a MicroK8s [add-on](https://microk8s.io/docs/addon-minio) by default, allowing us to create a local S3 bucket, which is more convenient for our local tests.

Let's enable the MinIO add-on for MicroK8s.

```bash
sudo microk8s enable minio
```

Authentication with MinIO is managed with an access key and a secret key. 
These credentials are generated and stored as Kubernetes secret when the MinIO add-on is enabled.

Let's fetch credentials and export them as environment variables in order to use them later:

```bash
export ACCESS_KEY=$(kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_ACCESS_KEY}' | base64 -d)
export SECRET_KEY=$(kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_SECRET_KEY}' | base64 -d)
export S3_ENDPOINT=$(kubectl get service minio -n minio-operator -o jsonpath='{.spec.clusterIP}')
export S3_BUCKET="spark-tutorial"
```

The MinIO add-on offers access to a built-in Web UI which can be used to interact with the local S3 object storage. But for this tutorial, we will use CLI commands.

To set up the AWS CLI, run the following commands:

```bash
sudo snap install aws-cli --classic

aws configure set aws_access_key_id $ACCESS_KEY 
aws configure set aws_secret_access_key $SECRET_KEY 
aws configure set region "us-west-2" 
aws configure set endpoint_url "http://$S3_ENDPOINT"
```

Check the tool by listing all S3 buckets:

```bash
aws s3 ls
```

```{note}
If you see an error message "Could not connect to the endpoint URL: ", then you need to wait a minute before trying the command above again.
```

The list of the buckets in our S3 storage is empty now, and the command returns no output.
That's because we have not created any buckets yet.
Let's proceed to create a new one.

To create the `spark-tutorial` bucket using AWS CLI, run:

```bash
aws s3 mb s3://spark-tutorial
```

We now have an S3 bucket available locally on our system!
See for yourself by running the same command to list all buckets:

```bash
aws s3 ls
```

With the access key, secret key, and the endpoint properly configured, you should see `spark-tutorial` bucket listed in the output.

### Credentials setup

For Apache Spark to be able to access and use our local S3 bucket, we need to provide a few configuration options including the bucket endpoint, access key and secret key.

In the Charmed Apache Spark solution, these configurations are stored in a Kubernetes secret and bound to a Kubernetes service account. When Spark jobs are executed using that service account, all associated configurations are automatically retrieved and supplied to Apache Spark.

The S3 configurations can be added to the existing `spark` service account with the following command:

```bash
spark-client.service-account-registry add-config \
  --username spark --namespace spark \
  --conf spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider \
  --conf spark.hadoop.fs.s3a.connection.ssl.enabled=false \
  --conf spark.hadoop.fs.s3a.path.style.access=true \
  --conf spark.hadoop.fs.s3a.access.key=$ACCESS_KEY \
  --conf spark.hadoop.fs.s3a.endpoint=$S3_ENDPOINT \
  --conf spark.hadoop.fs.s3a.secret.key=$SECRET_KEY
```

Now check the list of configurations bound for the service account:

```bash
spark-client.service-account-registry get-config \
  --username spark --namespace spark 
```

You should see the following list of configurations in the output:

```bash
spark.hadoop.fs.s3a.access.key=<access_key> 
spark.hadoop.fs.s3a.aws.credentials.provider=org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider
spark.hadoop.fs.s3a.connection.ssl.enabled=false
spark.hadoop.fs.s3a.endpoint=<s3_endpoint>
spark.hadoop.fs.s3a.path.style.access=true
spark.hadoop.fs.s3a.secret.key=<secret_key>
spark.kubernetes.authenticate.driver.serviceAccountName=spark
spark.kubernetes.namespace=spark
```

You can also see the configuration stored in a Kubernetes secret:

```bash
kubectl get secret -n spark -o yaml
```

<details>

<summary> Output example</summary>

```text
apiVersion: v1
items:
- apiVersion: v1
  data:
    spark.hadoop.fs.s3a.access.key: M0MyTHBKd1duSHd4SDZVQ2d3cVQ=
    spark.hadoop.fs.s3a.aws.credentials.provider: b3JnLmFwYWNoZS5oYWRvb3AuZnMuczNhLlNpbXBsZUFXU0NyZWRlbnRpYWxzUHJvdmlkZXI=
    spark.hadoop.fs.s3a.connection.ssl.enabled: ZmFsc2U=
    spark.hadoop.fs.s3a.endpoint: MTAuMTUyLjE4My4xMDU=
    spark.hadoop.fs.s3a.path.style.access: dHJ1ZQ==
    spark.hadoop.fs.s3a.secret.key: MTlBaVdWZENxMWZ1dHBYeUM0bmRSTlJ0M3Fid3ZydXFHdGZNNjl4ZA==
  kind: Secret
  metadata:
    creationTimestamp: "2025-04-16T09:13:00Z"
    name: spark8t-sa-conf-spark
    namespace: spark
    resourceVersion: "5555"
    uid: ddc76bf0-729f-4a01-9e0e-e1668b658036
  type: Opaque
kind: List
metadata:
  resourceVersion: ""
```

</details>

With that, the tutorial’s environment setup is complete!

## (Optional) Create a snapshot

At this stage, you may want to create a [snapshot](https://documentation.ubuntu.com/multipass/en/latest/reference/command-line-interface/snapshot/#snapshot) of the current state, for which you need to stop the Multipass VM:

```bash
multipass stop spark-tutorial
multipass snapshot spark-tutorial -n env-setup
```

This creates a snapshot name `env-setup` that we can use later to reset the environment. We will use it later for the Charmed Apache Kyuubi K8s deployment.

```{note}
Restarting the VM means that you might need to reset the environment variables exported earlier.
```

Before continuing with this tutorial, make sure to start the VM again:

```bash
multipass start spark-tutorial
```

