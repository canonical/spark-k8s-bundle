## How to setup a K8s cluster for Spark

The Charmed Spark solution requires an environment with:

* A Kubernetes cluster for running the services and workloads
* An Object storage layer to store persistent data

In the following guide, we provide details on the technologies currently supported and instructions on how these layers can be set up.

### Kubernetes

The Charmed Spark solution runs on top of several K8s distribution. We recommend you to use 1.29+, but no less than version 1.28. 
Earlier versions may still be working, although we do not explicitly test them. 

There are multiple ways that a K8s cluster can be deployed. We provide full compatibility and support for:

* MicroK8s
* AWS EKS
* Azure AKS (**Coming Soon**)

The how-to guide below shows you how to set up these to be used with Charmed Spark. 

#### MicroK8s

[MicroK8s](https://microk8s.io/) is the mightiest tiny Kubernetes distribution around. It can easily installed locally via SNAPs

```bash
sudo snap install microk8s --classic
```

When installing MicroK8s, it is recommended to configure MicroK8s in a way, so that there exists a user that has admin rights on the cluster. 

```bash 
sudo snap alias microk8s.kubectl kubectl
sudo usermod -a -G microk8s ${USER}
mkdir -p ~/.kube
sudo chown -f -R ${USER} ~/.kube
```

To make these changes effective, you can either open a new shell (or log in, log out) or use `newgrp microk8s` 

Make sure that the MicroK8s cluster is now up and running:

```bash
microk8s status --wait-ready
```

Export the Kubernetes config file associated with admin rights and store it in the $KUBECONFIG file, e.g. `~/.kube/config`: 

```bash 
export KUBECONFIG=path/to/file # Usually ~/.kube/config
microk8s config | tee ${KUBECONFIG}
```

Enable the K8s features required by the Spark Client Snap 

```
microk8s.enable dns rbac storage hostpath-storage
```

The MicroK8s cluster is now ready to be used. 

##### External LoadBalancer

If you want to expose the Spark History Server UI via a Traefik ingress, we need to enable external loadbalancer 

```
IPADDR=$(ip -4 -j route get 2.2.2.2 | jq -r '.[] | .prefsrc')
microk8s enable metallb:$IPADDR-$IPADDR
```

#### AWS EKS

In order to deploy an EKS cluster, make sure that you have working CLI tools properly installed on your edge machine:

* [AWS CLI](https://aws.amazon.com/cli/) correctly setup to use a properly configured service account (refer to [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) for configuration and [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html) for authentication). Once the AWS CLI is configured, make sure that it works properly by testing the authentication call through the following command:
```bash 
aws sts get-identity-caller
```

* [eksctl](https://eksctl.io/) installed and configure (refer to the [README.md] file for more information on how to install it)

Make also sure that your service account (configured in AWS) has the right permission to create and manage EKS clusters. In general, we recommend the use of profiles when having multiple accounts.

##### Creating the cluster

An EKS cluster can be created using `eksctl`, the AWS Management Console, or the AWS CLI. In the following we will use `eksctl`.
Create a YAML file with the following content 

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
    name: spark-cluster
    region: <AWS_REGION_NAME>
    version: "1.27"
iam:
  withOIDC: true

addons:
- name: aws-ebs-csi-driver
  wellKnownPolicies:
    ebsCSIController: true

nodeGroups:
    - name: ng-1
      minSize: 3
      maxSize: 5
      iam:
        attachPolicyARNs:
        - arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy
        - arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy
        - arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
        - arn:aws:iam::aws:policy/AmazonS3FullAccess
      instancesDistribution:
        maxPrice: 0.15
        instanceTypes: ["m5.xlarge", "m5.large"] # At least two instance types should be specified
        onDemandBaseCapacity: 0
        onDemandPercentageAboveBaseCapacity: 50
        spotInstancePools: 2
```

Feel free to replace the ```<AWS_REGION_NAME>``` with the AWS region of your choice, and custom further the above YAML based on your needs and policies in place. 

You can then create the EKS via CLI

```bash
eksctl create cluster -f cluster.yaml
```

The EKS cluster creation process may take several minutes. The cluster creation process should already update the `KUBECONFIG` file with the new cluster information. By default, `eksctl` creates a user that generate new access token on the fly via the `aws` CLI. However, this conflicts with the `spark-client` snap that is strictly confined and does not have access to the `aws` command. Therefore, we recommend you to manually retrieve a token, i.e.

```bash 
aws eks get-token --region <AWS_REGION_NAME> --cluster-name spark-cluster --output json
```

and paste the token in the KUBECONFIG file

```yaml
users:
- name: eks-created-username
  user:
    token: <AWS_TOKEN>
```

The EKS cluster is now ready to be used. 

### Object storage

Object storage persistence integration with Charmed Spark is critical for: 

* reading and writing application data to be used in Spark Jobs
* storing Spark Jobs logs to be then exposed via Charmed Spark History Server
* enable Hive-compatible JDBC/ODBC endpoints provided by Apache Kyuubi to provide datalake capabilities on top of HDFS/Hadoop/object storages

Charmed Spark provides out-of-box integration with the following object storage backends:

* S3-compatible object storages, such as:
  * MinIO
  * AWS S3 bucket
* Azure Storage 
  * Azure Blob Storage 
  * Azure DataLake v2 Storage

In the following, we provide guidance on how to set up different object storages and 
how to configure them to make sure that it seamlessly integrates with Charmed Spark. 

In fact, to store Spark logs on a dedicated directories, you need to create the appropriate folder (that is named `spark-events`) in the storage backend. 
This can be done both on S3 and on Azure DataLake Gen2 Storage. Although there are multiple ways to do this, 
in the following we recommend you to use snap clients. 
Alternatively, use [Python libraries](https://github.com/canonical/spark-k8s-bundle/blob/94ac51d519cece9dc6810c7aaa0144a28cd7989b/python/spark_test/core/s3.py).

#### S3-compatible object storages

To connect Charmed Spark with an S3-compatible object storage, 
the following configurations need to be specified:

* *access_key* 
* *secret_key*
* *endpoint*
* *bucket*
* (optional) *region*

##### Supported S3 backends

In the following sections, we show how to setup and extract those information in 
MinIO and AWS S3. 

###### MicroK8s MinIO

If you have already a MicroK8s cluster running, you can enable the MinIO storage with the dedicated addon

```
microk8s.enable minio
```

Refer [here](https://microk8s.io/docs/addon-minio) for more information how to customize your MinIO MicroK8s deployment.

You can then use the following commands to obtain the access key, the access secret and the MinIO endpoint:

* *access_key*: `microk8s.kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_ACCESS_KEY}' | base64 -d`
* *secret_key*: `microk8s.kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_SECRET_KEY}' | base64 -d`
* *endpoint*: `microk8s.kubectl get services -n minio-operator | grep minio | awk '{ print $3 }'`

Configure the AWS CLI snap with these parameters. After that, you can create a bucket using

```shell
aws s3 mb s3://<S3_BUCKET>
```

###### AWS S3

In order to use AWS S3, you need to have an AWS user that has permission to use S3 resource for reading and writing. 
You can create a new user or use an existing one, as long as you grant permission to S3, either centrally using the IAM console 
or from the S3 service itself. 

If the service account has `AmazonS3FullAccess` permission, you can create new buckets using

```bash 
aws s3api create-bucket --bucket <S3_BUCKET> --region <S3_REGION>
```

Note that buckets will be associated to a given AWS region. Once the bucket is created, you can use 
the `access_key` and the `secret_key` of your service account, also used for authenticating with the AWS CLI profile. 
The endpoint of the service is `https://s3.<S3_REGION>.amazonaws.com`.

##### Setting Up the object Storage

Leveraging on standard S3 API, you can use the `aws` snap client to perform operations with the
S3 service, like creating buckets, upload new content, inspecting the structure and removing data.

To install the AWS CLI client, use 

```shell
sudo snap install aws-cli --classic
```

The client can then be configured using the parameters above with 

```shell
aws configure set aws_access_key_id <S3_ACCESS_KEY>
aws configure set aws_secret_access_key <S3_SECRET_KEY>
aws configure set endpoint_url <S3_ENDPOINT>
aws configure set default.region <S3_REGION>
```

Test that the `aws-cli` client is properly working with 

```
aws s3 ls
```

To create a folder on an existing bucket, just place an empty path object `spark-events`. 

```shell
aws s3api put-object --bucket <S3_BUCKET> --key spark-events
```

The S3-object storage should now be ready to be used by Spark Jobs to store their logs. 

#### Azure Storage

Charmed Spark provides out-of-the-box support also for the following Azure storage backends: 

* Azure Blob Storage (both WASB and WASBS)
* Azure DataLake Gen2 Storage (ABFS and ABFSS)

> :warning: Note that Azure DataLake Gen1 Storage is currently not supported, and it has been deprecated by Azure.

In order to connect Charmed Spark with the Azure storage backends (WASB, WASBS, ABFS and ABFSS) 
the following configurations need to be specified:

* *storage_account*
* *storage_key*
* *container*

##### Setting Up the object Storage

You can use the `azcli` snap client to perform operations with the Azure storage services, 
like creating buckets, upload new content, inspecting the structure and removing data.

To install the `azcli` client, use 

```shell
sudo snap install azcli
```

The client can then be configured using the following environment variables

```shell
export AZURE_STORAGE_ACCOUNT=...
export AZURE_STORAGE_KEY=...
```

These credentials can be retrieved from the [Azure portal](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts), after creating a storage account. 
When creating the storage account, make sure that you enable "Hierarchical namespace" if you 
want to use Azure DataLake Gen2 Storage.

Test that the `azcli` client is properly working with 

```
azcli storage container list
```

Once the credentials are set up, you can create a container in your namespace either from the portal 
or also using the `azcli` with

```shell
azcli storage container create --fail-on-exist --name <AZURE_CONTAINER>
```

To create a folder on an existing container, just place a dummy file in the container under the  `spark-events` path.
For doing this, you can use the `azcli` client snap.

```shell
azcli storage blob upload --container-name <AZURE_CONTAINER> --name spark-events/a.tmp -f /dev/null
```
