---
myst:
  html_meta:
    description: "Learn how to set up MicroK8s, spark-client snap, MinIO, and Juju on Ubuntu for running Charmed Apache Spark on Kubernetes."
---

<!-- test:spread
priority: 700
kill-timeout: 20m
-->

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

```shell
sudo snap install microk8s --channel=1.32-strict/stable
```

Make sure to install the `1.32-strict/stable` version of MicroK8s which was tested to work with all the components of this tutorial.

### Configuration

Let's configure MicroK8s so that the currently logged-in user has admin rights to the cluster.

First, set an alias `kubectl` that can be used instead of `microk8s.kubectl`:

```shell
sudo snap alias microk8s.kubectl kubectl
```

Then, add the current user into `microk8s` group:

```shell
sudo usermod -a -G snap_microk8s ${USER}
```

Create and provide ownership of `~/.kube` directory to the current user:

```shell
mkdir -p ~/.kube
sudo chown -f -R ${USER} ~/.kube
```

Put the group membership changes into effect:

```bash
newgrp snap_microk8s
```

<!-- test:run
# Activate snap_microk8s group for the current process (newgrp is interactive-only)
newgrp snap_microk8s << 'NEWGRP_EOF'
true
NEWGRP_EOF
-->

Check the status of the MicroK8s:

```shell
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
This is where `kubectl` looks for the `kubeconfig` file by default.

```shell
microk8s config | tee ~/.kube/config
```

Now let's enable a few add-ons for using features like role based access control, usage of local volume for storage, and load balancing.

```shell
sudo microk8s enable rbac
sudo microk8s enable storage hostpath-storage

sudo apt install -y jq

IP_ADDR_START=$(ip -4 -j route get 2.2.2.2 | jq -r '.[] | .prefsrc')
IP_ADDR_END=$(echo $IP_ADDR_START | awk -F. '{print $1"."$2"."$3"."$4+2}')
sudo microk8s enable metallb:$IP_ADDR_START-$IP_ADDR_END
```

Wait for the commands to finish running and check the list of enabled add-ons:

```shell
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

For Apache Spark jobs to be running run on top of Kubernetes, a set of resources (ServiceAccount, associated Roles, RoleBindings etc.) need to be created and configured.
To simplify this task, the Charmed Apache Spark solution offers the `spark-client` snap. Install the snap: 

```shell
sudo snap install spark-client --channel 3.4/edge
```

Let's create a Kubernetes namespace for us to use as a playground in this tutorial.

```shell
kubectl create namespace spark
```

We will now create a ServiceAccount that will be used to run the Spark jobs. The creation of the ServiceAccount can be done using the `spark-client` snap, which will create necessary Roles, RoleBindings and other necessary configurations along with the creation of the ServiceAccount:

```shell
spark-client.service-account-registry create \
  --username spark --namespace spark
```

This command does a number of things in the background. First, it creates a ServiceAccount in the `spark` namespace with the name `spark`. Then it creates a Role with name `spark-role` with all the required RBAC permissions and binds that Role to the ServiceAccount by creating a RoleBinding. 

These resources can be viewed with `kubectl get` commands as follows:

```shell
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
spark-role   2026-03-04T09:13:00Z

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
   /__ / .__/\_,_/_/ /_/\_\   version 3.4.4
      /_/

Using Python version 3.10.12 (main, Jan  8 2026 06:52:19)
Spark context Web UI available at http://10.189.154.233:4040
Spark context available as 'sc' (master = k8s://https://10.189.154.233:16443, app id = spark-cf06b03549f54011a0ab612df8be335e).
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

```shell
sudo snap install juju 
mkdir -p ~/.local/share
```

Juju can automatically detects all available clouds on our local machine (VM) without the need of additional setup or configuration. 
You can verify this by running `juju clouds` command that should produce an output similar to the following:

```text
Since Juju 3 is being run for the first time, it has downloaded the latest public cloud information.
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

```shell
juju bootstrap microk8s spark-tutorial
```

<!-- test:wait --seconds 30 -->

The creation of the new controller can be verified with the `juju controllers` command.
The output of the command should be similar to:

```text
Use --refresh option with this command to see the latest information.

Controller       Model  User   Access     Cloud/Region        Models  Nodes  HA  Version
spark-tutorial*  -      admin  superuser  microk8s/localhost       1      1   -  3.6.21  
```

The Juju setup is complete.

## MinIO

Apache Spark can be configured to use S3 for object storage.
However, for this tutorial, instead of AWS S3, we'll use [MinIO](https://min.io/): a lightweight S3-compatible object storage.
It is available as a MicroK8s [add-on](https://microk8s.io/docs/addon-minio) by default, allowing us to create a local S3 bucket, which is more convenient for our local tests.

Let's enable the MinIO add-on for MicroK8s.

```shell
sudo microk8s enable minio
```

<!-- test:wait --seconds 60 -->

Authentication with MinIO is managed with an access key and a secret key. 
These credentials are generated and stored as Kubernetes secret when the MinIO add-on is enabled.

Let's fetch credentials and export them as environment variables in order to use them later:

```shell
export ACCESS_KEY=$(kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_ACCESS_KEY}' | base64 -d)
export SECRET_KEY=$(kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_SECRET_KEY}' | base64 -d)
export S3_ENDPOINT=$(kubectl get service minio -n minio-operator -o jsonpath='{.spec.clusterIP}')
export S3_BUCKET="spark-tutorial"
```

The MinIO add-on offers access to a built-in Web UI which can be used to interact with the local S3 object storage. But for this tutorial, we will use CLI commands.

To set up the AWS CLI, run the following commands:

```shell
sudo snap install aws-cli --classic

aws configure set aws_access_key_id $ACCESS_KEY 
aws configure set aws_secret_access_key $SECRET_KEY 
aws configure set region "us-west-2" 
aws configure set endpoint_url "http://$S3_ENDPOINT"
```

Check the tool by listing all S3 buckets:

<!-- test:run
# Retry aws s3 ls until MinIO is ready (may take a moment after addon enable)
for i in $(seq 1 12); do
  aws s3 ls && break || sleep 10
done
-->

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

```shell
aws s3 mb s3://spark-tutorial
```

We now have an S3 bucket available locally on our system!
See for yourself by running the same command to list all buckets:

```shell
aws s3 ls
```

With the access key, secret key, and the endpoint properly configured, you should see `spark-tutorial` bucket listed in the output.

### Credentials setup

For Apache Spark to be able to access and use our local S3 bucket, we need to provide a few configuration options including the bucket endpoint, access key and secret key.

In the Charmed Apache Spark solution, these configurations are stored in a Secret object and bound to a ServiceAccount. When Spark jobs are executed using that service account, all associated configurations are automatically retrieved and supplied to Apache Spark.

The S3 configurations can be added to the existing `spark` service account with the following command:

```shell
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

```shell
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

```shell
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
    creationTimestamp: "2026-03-04T09:13:00Z"
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

With that, the basic environment setup is complete!

## Integration Hub

Throughout this tutorial you will create service accounts in several Kubernetes namespaces.
Running `add-config` to push S3 credentials to every new account manually would quickly become repetitive.
The [Integration Hub for Apache Spark](https://charmhub.io/spark-integration-hub-k8s) automates this:
once deployed and configured with the `monitored-service-accounts` option, it automatically pushes the storage credentials
to every service account that is managed by `spark-client` — including accounts created in the future.

Let's deploy it now so that service accounts we create in later steps receive S3 credentials automatically.

Create a dedicated Juju model for the Integration Hub:

```shell
juju add-model spark-integration-hub
```

Deploy the Integration Hub charm and an `s3-integrator` charm to supply it with the storage configuration:

```shell
juju deploy spark-integration-hub-k8s --channel 3/stable --trust
juju config spark-integration-hub-k8s monitored-service-accounts="*:*"
juju deploy s3-integrator --channel 1/stable
juju config s3-integrator bucket=spark-tutorial path=spark-events endpoint=http://$S3_ENDPOINT
```

<!-- test:await-idle --timeout 600 --allow-blocked s3-integrator -->

The `s3-integrator` will remain in `blocked` state until S3 credentials are provided. Set the credentials first, then integrate:

```shell
juju run s3-integrator/leader sync-s3-credentials \
  access-key=$ACCESS_KEY secret-key=$SECRET_KEY
juju integrate s3-integrator spark-integration-hub-k8s
```

<!-- test:await-idle --timeout 600 -->

Wait for both charms to reach `active/idle` status:

```bash
watch juju status --color
```

Verify that the Integration Hub has automatically updated the `spark` service account:

```shell
spark-client.service-account-registry get-config \
  --username spark --namespace spark
```

The output should include the same S3 configuration properties we set up manually earlier,
now maintained by the Integration Hub.
From this point on, any service account you create with `spark-client` will receive
the S3 credentials automatically.

Create the `spark-events` and `warehouse` directories in S3:

```shell
aws s3api put-object --bucket spark-tutorial --key spark-events/
aws s3api put-object --bucket spark-tutorial --key warehouse/
```

<!-- test:assert
spark-client.service-account-registry get-config --username spark --namespace spark | grep -q "fs.s3a.endpoint"
juju status -m spark-integration-hub --format=json | jq -e '.applications."spark-integration-hub-k8s"."application-status".current == "active"'
-->

## (Optional) Create a snapshot

At this stage, you may want to create a [snapshot](https://documentation.ubuntu.com/multipass/en/latest/reference/command-line-interface/snapshot/#snapshot) of the current state, for which you need to stop the Multipass VM. Exit the VM by pressing `CTRL + D` and stop it:

```bash
multipass stop spark-tutorial
```

Create a snapshot name `env-setup`.
We will use it later to reset the environment for the Charmed Apache Kyuubi K8s deployment:

```bash
multipass snapshot spark-tutorial -n env-setup
```

Before continuing with this tutorial, make sure to start the VM again:

```bash
multipass start spark-tutorial
```

Once it starts, reconnect to the VM:

```bash
multipass shell spark-tutorial
```
