## How to setup a K8s cluster for Spark

The Charmed Spark solution runs on top of a K8s distribution. We recommend you to use version the latest stable version, but at least version 1.26. There are multiple ways that a K8s cluster can be deployed. Here below we summarize how to setup on K8s on the distributions that we currently support: 

* MicroK8s
* AWS EKS

The how-to guide belows shows you how to setup all of the services used by Charmed Spark. It may be that given your use-case some of them may not be needed though.

### MicroK8s

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

#### S3 Storage

Enable the MinIO storage if you want to store Spark Jobs logs in a S3 compatible object storage to be then exposed via Charmed Spark History Server.

```
microk8s.enable minio
```

Refer [here](https://microk8s.io/docs/addon-minio) for more information how to customize your MinIO MicroK8s deployment.

Use the following commands to obtain the access key, the access secret and the MinIO endpoint:

* *access key*: `microk8s.kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_ACCESS_KEY}' | base64 -d`
* *secret key*: `microk8s.kubectl get secret -n minio-operator microk8s-user-1 -o jsonpath='{.data.CONSOLE_SECRET_KEY}' | base64 -d`
* *MinIO endpoint*: `microk8s.kubectl get services -n minio-operator | grep minio | awk '{ print $3 }'`

#### External LoadBalancer

Enable external loadbalancer if you want to expose the Spark History Server UI via a Traefik ingress

```
IPADDR=$(ip -4 -j route get 2.2.2.2 | jq -r '.[] | .prefsrc')
microk8s enable metallb:$IPADDR-$IPADDR
```

The MicroK8s cluster is now ready to be used. 


### AWS EKS

In order to deploy an EKS cluster, make sure that you have working CLI tools properly installed on your edge machine:

* [AWS CLI](https://aws.amazon.com/cli/) correctly setup to use a properly configured service account (refer to [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) for configuration and [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html) for authentication). Once the AWS CLI is configured, make sure that it works properly by testing the authentication call through the following command:
```bash 
aws sts get-identity-caller
```

* [eksctl](https://eksctl.io/) installed and configure (refer to the [README.md] file for more information on how to install it)

Make also sure that your service account (configured in AWS) has the right permission to create and manage EKS clusters. In general, we recommend the use of profiles when having multiple accounts.

#### Creating the cluster

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

#### S3 Storage

Create a new bucket in the AWS S3 storage if you want to store Spark Jobs logs to be then exposed via Charmed Spark History Server.

Create a new bucket via AWS CLI 

```bash 
aws s3api create-bucket --bucket <BUCKET_NAME> --region <AWS_REGION_NAME>
```

Use the access key and the access secret of your service account, also used for authenticating with the AWS CLI profile. The endpoint of the bucket is `https://s3.<AWS_REGION_NAME>.amazonaws.com`.