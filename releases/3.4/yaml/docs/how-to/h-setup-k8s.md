## How to setup a K8s cluster for Apache Spark

The Charmed Apache Spark solution requires an environment with:

* A Kubernetes cluster for running the services and workloads
* An Object storage layer to store persistent data

In the following guide, we provide details on the technologies currently supported and instructions on how these layers can be set up.

### Kubernetes

The Charmed Apache Spark solution runs on top of several K8s distributions. We recommend using versions above or equal to `1.29`. 
Earlier versions may still be working, although we do not explicitly test them. 

There are multiple ways that a K8s cluster can be deployed. We provide full compatibility and support for:

* MicroK8s
* AWS EKS
* Azure AKS

The how-to guide below shows you how to set up these to be used with Charmed Apache Spark. 

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

Enable the K8s features required by the Apache Spark Client snap 

```
microk8s.enable dns rbac storage hostpath-storage
```

The MicroK8s cluster is now ready to be used. 

##### External LoadBalancer

If you want to expose the Spark History Server UI via a Traefik ingress, we need to enable an external loadbalancer:

```
IPADDR=$(ip -4 -j route get 2.2.2.2 | jq -r '.[] | .prefsrc')
microk8s enable metallb:$IPADDR-$IPADDR
```

#### AWS EKS

To deploy an EKS cluster, make sure that you have working CLI tools properly installed on your edge machine:

* [AWS CLI](https://aws.amazon.com/cli/) correctly setup to use a properly configured service account (refer to [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) for configuration and [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html) for authentication). Once the AWS CLI is configured, make sure that it works properly by testing the authentication call through the following command:

  ```bash 
  aws sts get-identity-caller
  ```

* [eksctl](https://eksctl.io/) installed and configured (refer to the **README.md** file for more information on how to install it)

Make sure that your service account (configured in AWS) has the right permission to create and manage EKS clusters. In general, we recommend the use of profiles when having multiple accounts.

##### Creating a cluster

An EKS cluster can be created using `eksctl`, the AWS Management Console, or the AWS CLI. In the following, we will use `eksctl`.

Create a YAML file with the following content:

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

You can then create the EKS via CLI:

```bash
eksctl create cluster -f cluster.yaml
```

The EKS cluster creation process may take several minutes. The cluster creation process should already update the `KUBECONFIG` file with the new cluster information. By default, `eksctl` creates a user that generates a new access token on the fly via the `aws` CLI. However, this conflicts with the `spark-client` snap that is strictly confined and does not have access to the `aws` command. Therefore, we recommend you to manually retrieve a token:

```bash 
aws eks get-token --region <AWS_REGION_NAME> --cluster-name spark-cluster --output json
```

and paste the token in the KUBECONFIG file:

```yaml
users:
- name: eks-created-username
  user:
    token: <AWS_TOKEN>
```

The EKS cluster is now ready to be used. 


#### Azure AKS

To deploy an Azure Kubernetes Service (AKS) cluster, you'd need to make sure you have Azure CLI properly installed and authenticated on your edge machine.

[The Azure CLI](https://learn.microsoft.com/en-us/cli/azure/) is the official cross-platform command-line tool to connect to Azure Cloud and execute administrative commands on Azure resources.

Install Azure CLI with snap:

```bash
sudo snap install azcli
```

Alias the command `azcli.az` as `az`, since most of the online resources -- including the Azure Docs -- refer to the CLI as `az`:

```bash
sudo snap alias azcli.az az
```

Authenticate with an Azure account.
The easiest way to do so is by using the device login workflow as follows:

```bash
az login --use-device-code
```

Once you run the login command, you should see an output similar to the following in the console:

```txt
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code XXXXXXX to authenticate.
```

Browse to the page https://microsoft.com/devicelogin, enter the code displayed in the console earlier, and finally login with your Azure account credentials.
When prompted for confirmation, click "Yes".
Once the authentication is successful, you should see authentication success message in the browser.
If you have multiple subscriptions associated with your Azure account, you may be asked to choose the subscription by the CLI.
Once that is complete, the Azure CLI is ready.

To confirm that the authentication went well, try listing storage accounts in your Azure Cloud:

```bash
az storage account list
echo $?
```

The command should list the storage accounts in your Azure cloud (if any) and the return code printed by `echo $?` should be `0` if the command was successful.

##### Creating a cluster

Now that the Azure Cloud and CLI are working, start creating the AKS cluster resources.
This can be done in multiple ways -- using the browser console, using `az` CLI directly, or by using Azure Terraform provider.
In this guide, we're going to use Terraform to create the AKS cluster.

[Terraform](https://developer.hashicorp.com/terraform) is an infrastructure as code (IaC) tool that lets you create, change and version the infrastructure (in our case, Azure cloud resources) safely and efficiently. Start by installing `terraform` as a snap.

```bash
sudo snap install terraform --classic
```

Once terraform is installed, we're ready to write the Terraform plan for our new AKS cluster.

The terraform scripts for the creation of a simple AKS cluster for Charmed Spark is already available in the [GitHub repository](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/yaml/docs-resources/aks-setup).
If you inspect the contents there, you will see that there are different Terraform configuration files.
These configuration files contain the specification for the resource group, virtual network and AKS cluster we're going to create.

We can use the aforementioned Terraform module by referencing it as a module in a local Terraform file.
Create a file named `setup.tf` locally and reference the Terraform module:

```terraform
# file: setup.tf

module "aks_cluster" {
  source     = "git::https://github.com/canonical/spark-k8s-bundle//releases/3.4/yaml/docs-resources/aks-setup"
}

```

Now, initialize Terraform and view the plan by running the following command from the same directory that contains the `setup.tf` file:

```bash
terraform init
terraform plan
```

Under the plan, you should see that an AKS cluster, along with resource group, virtual network, subnet, NAT gateway, etc. are on the "to-add" list.

Apply the plan and wait for the resources to be created:

```bash
terraform apply -auto-approve
```

Once the resource creation completes, check the resource group name and AKS cluster name:

```bash
terraform output

# aks_cluster_name = "TestAKSCluster"
# resource_group_name = "TestSparkAKSRG"
```

##### Generating Kubeconfig file

To generate the Kubeconfig file for connecting the client to the newly created cluster:

```bash
az aks get-credentials --resource-group <resource_group_name> --name <aks_cluster_name> --file ~/.kube/config
```

The AKS cluster is now ready to be used.

### Object storage

Object storage persistence integration with Charmed Apache Spark is critical for: 

* reading and writing application data to be used in Spark jobs
* storing Spark jobs logs to be then exposed via Charmed Apache Spark History Server
* enable Hive-compatible JDBC/ODBC endpoints provided by Apache Kyuubi to provide datalake capabilities on top of HDFS/Hadoop/object storages

Charmed Apache Spark provides out-of-box integration with the following object storage backends:

* S3-compatible object storages, such as:
  * MinIO
  * AWS S3 bucket
* Azure Storage 
  * Azure Blob Storage 
  * Azure DataLake v2 Storage

In the following, we provide guidance on how to set up different object storages and 
how to configure them to make sure that they seamlessly integrate with Charmed Apache Spark. 

In fact, to store Apache Spark logs on dedicated directories, you need to create the appropriate folder (that is named `spark-events`) in the storage backend. 
This can be done both on S3 and on Azure DataLake Gen2 Storage. Although there are multiple ways to do this, 
in the following we recommend you to use snap clients. 
Alternatively, use [Python libraries](https://github.com/canonical/spark-k8s-bundle/blob/94ac51d519cece9dc6810c7aaa0144a28cd7989b/python/spark_test/core/s3.py).

#### S3-compatible object storages

To connect Charmed Apache Spark with an S3-compatible object storage, 
the following configurations need to be specified:

* `access_key` 
* `secret_key`
* `endpoint`
* `bucket`
* (optional) `region`

Leveraging on standard S3 API, you can use the `aws-cli` snap client to perform operations with the
S3 service, like creating buckets, uploading new content, inspecting the structure, and removing data.

To install the AWS CLI client, use 

```shell
sudo snap install aws-cli --classic
```

The client can then be configured using the parameters above with 

```shell
aws configure set aws_access_key_id <S3_ACCESS_KEY>
aws configure set aws_secret_access_key <S3_SECRET_KEY>
aws configure set endpoint_url <S3_ENDPOINT>
aws configure set default.region <S3_REGION> # Optional for AWS only
```

Test that the AWS CLI client is properly working with 

```
aws s3 ls
```

##### Supported S3 backends

In the following sections, we show how to setup and extract information for:

* MicroK8s MinIO 
* AWS S3

###### MicroK8s MinIO

If you have already a MicroK8s cluster running, you can enable the MinIO storage with the dedicated addon

```
microk8s.enable minio
```

Refer to the [add-on documentation](https://microk8s.io/docs/addon-minio) for more information on how to customize your MinIO MicroK8s deployment.

You can then use the following commands to obtain the `access_key`, the `secret_key` and the MinIO `endpoint`:

* `access_key`: `microk8s.kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_ACCESS_KEY}' | base64 -d`
* `secret_key`: `microk8s.kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_SECRET_KEY}' | base64 -d`
* `endpoint`: `microk8s.kubectl get services -n minio-operator | grep minio | awk '{ print $3 }'`

Configure the AWS CLI snap with these parameters, as shown above. After that, you can create a bucket using

```shell
aws s3 mb s3://<S3_BUCKET>
```

###### AWS S3

To use AWS S3, you need to have an AWS user that has permission to use S3 resource for reading and writing. 
You can create a new user or use an existing one, as long as you grant permission to S3, either centrally using the IAM console 
or from the S3 service itself. 

If the service account has the `AmazonS3FullAccess` permission, you can create new buckets by using

```bash 
aws s3api create-bucket --bucket <S3_BUCKET> --region <S3_REGION>
```

Note that buckets will be associated to a given AWS region. Once the bucket is created, you can use 
the `access_key` and the `secret_key` of your service account, also used for authenticating with the AWS CLI profile. 
The endpoint of the service is `https://s3.<S3_REGION>.amazonaws.com`.

##### Setting up the object storage

To create a folder on an existing bucket, just place an empty path object `spark-events`:

```shell
aws s3api put-object --bucket <S3_BUCKET> --key spark-events
```

The S3-object storage should now be ready to be used by Spark jobs to store their logs. 

#### Azure Storage

Charmed Apache Spark provides out-of-the-box support also for the following Azure storage backends: 

* Azure Blob Storage (both WASB and WASBS)
* Azure DataLake Gen2 Storage (ABFS and ABFSS)

[note type="caution"]
Note that Azure DataLake Gen1 Storage is currently not supported, and it has been deprecated by Azure.
[/note]

To connect Charmed Apache Spark with the Azure storage backends (WASB, WASBS, ABFS and ABFSS) 
the following configurations need to be specified:

* `storage_account`
* `storage_key`
* `container`

##### Setting up the object storage

You can use the `azcli` snap client to perform operations with the Azure storage services, 
like creating buckets, uploading new content, inspecting the structure, and removing data.

To install the `azcli` client, use 

```shell
sudo snap install azcli
```

The client needs to be configured using the Azure storage account and the associated storage key. These credentials can be retrieved from the [Azure portal](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts), after creating a storage account. 
When creating the storage account, make sure that you enable "Hierarchical namespace" if you 
want to use Azure DataLake Gen2 Storage (which is assumed by default unless configured otherwise).

Once you have that information, the client can be configured by using the following environment variables:

```shell
export AZURE_STORAGE_ACCOUNT=<storage_account> 
export AZURE_STORAGE_KEY=<storage_key>
```

Now test that the `azcli` client is properly working with 

```
azcli storage container list
```

Once the credentials are set up, you can create a container in your namespace either from the portal 
or also using the `azcli` with

```shell
azcli storage container create --fail-on-exist --name <AZURE_CONTAINER>
```

To create a folder on an existing container, just place a dummy file in the container under the  `spark-events` path.
To do this, you can use the `azcli` client snap:

```shell
azcli storage blob upload --container-name <AZURE_CONTAINER> --name spark-events/a.tmp -f /dev/null
```

## Use a local Python package with PySpark

You can configure the spark-client snap to see and access Python packages, installed locally, outside of the snap, which are not available in the PySpark shell by default.

For example, to do so for NumPy, follow the steps below.

Create a virtual environment and install the Python package using

```shell
python3.10 -m venv .venv
.venv/bin/pip install numpy
```

[note type="caution"]
Ensure you use the same Python version as the one shipped in the spark-client snap. The python version is displayed upon entering the PySpark shell.
[/note]

After the installation, configure the client using the following environment variable:
```shell
export PYTHONPATH=path/to/.venv/lib/python3.10/site-packages
```

You may now enter the PySpark shell and import the package:

```python
import numpy as np
``