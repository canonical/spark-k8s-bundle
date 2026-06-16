---
myst:
  html_meta:
    description: "How-to guide for deploying Charmed Apache Spark on Kubernetes with Juju, including object storage, monitoring, and log aggregation integration."
---

(how-to-deploy-spark)=
# Deploy Charmed Apache Spark

Charmed Apache Spark comes with a bundled set of components that allow you to easily manage Apache
Spark workloads on K8s, providing integration with object storage, monitoring and log aggregation.

For an overview of all components and how they relate to each other, see the [Components overview](explanation-component-overview).

## Prerequisites

Since Charmed Apache Spark will be managed by Juju, make sure that:

* you have a Juju client (e.g. via a [snap](https://snapcraft.io/juju)) installed in your local machine  
* you are able to connect to a Juju controller
* you have read-write permissions to either an S3-compatible or an Azure object storage

To set up a Juju controller on K8s and the Juju client, you can refer to existing tutorials
and documentation for [MicroK8s](https://documentation.ubuntu.com/juju/3.6/tutorial/) and for
[AWS EKS](https://juju.is/docs/juju/amazon-eks).
Also refer to the [How-to set up environment](how-to-deploy-environment) guide to install and set up
an S3-compatible object storage on MicroK8s (MinIO), EKS (AWS S3), or Azure object storages.
For other backends or K8s distributions other than MinIO on MicroK8s and S3 on EKS
(e.g. Ceph, Charmed Kubernetes, GKE, etc.), please refer to their documentation.

Charmed Apache Spark supports native integration with the Canonical Observability Stack (COS).
To enable monitoring on top of Charmed Apache Spark, make sure that you have a Juju model with COS
correctly deployed. To deploy COS on MicroK8s follow the step-by-step
[tutorial](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s)
or refer to its [documentation](https://charmhub.io/topics/canonical-observability-stack) for more
information.

## Preparation

The Charmed Apache Spark bundle is deployed using Terraform, and therefore make sure you have a working Terraform 1.8+ installed in your machine.
You can install [Terraform](https://snapcraft.io/terraform) or [OpenTofu](https://snapcraft.io/terraform) via a snap. Run the following command
to install Terraform using snap:

```shell
sudo snap install terraform --classic
```

Terraform modules make use of the Terraform Juju provider.
More information about the Juju provider can be found in the
[Terraform documentation](https://registry.terraform.io/providers/juju/juju/latest/docs).

The [Charmed Apache Spark Terraform module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform)
is composed of the following submodules:

* [base module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform/modules/spark)
  that bundles all the base resources of the Charmed Apache Spark solution
* [cos-integration module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform/modules/observability)
  that bundles all the resources that enable integration with COS

The Charmed Apache Spark Terraform modules can be configured using a `.tfvars.json` file with the following schema:

```json
{
  "s3": {
    "bucket": "<bucket_name>",
    "endpoint": "<s3_endpoint>"
  },
  "kyuubi_user": "<kyuubi_service_account>",
  "model": "<juju_model>",
  "cos_model": "<cos_model>" 
}
```

The following table provides the description of the different configuration option

| key         | Description                                                                                                                           |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `kyuubi_user` | Service Account to be used by Apache Kyuubi Engines (deprecated)                                                                             |
| `model`       | Namespace where the charms will be deployed. This should correspond to the name of the Juju model to be used.                         |
| `s3.endpoint` | Endpoint of the S3-compatible object storage backend, in the form of `http(s)//host:port`.                                            |
| `s3.bucket`   | Name of the S3 bucket to be used for storing logs and data                                                                            |
| `cos_model`   | (Optional) Name of the model where COS is deployed. If omitted, the resource of the cos-integration submodules will not be deployed   |

#### Example .tfvars.json

For example, to point to the MinIO instance and the right bucket:

```json
{
  "storage_backend": "s3",
  "s3": {
    "region": "eu-central-1",
    "bucket": "spark-test",
    "endpoint": "http://<host>:80"
  }
}
```

For more information on this particular example, see the [microK8s MinIO demo](https://github.com/deusebio/datawarehousing-with-spark/blob/main/docs/microk8s_minio.md). For other examples, see the [repository](https://github.com/deusebio/datawarehousing-with-spark/blob/main/README.md).

```{caution}
The Juju Terraform provider does not yet support cross-controller relations with COS.
Therefore, COS model must be hosted in the same controller as the Charmed Apache Spark model. 
```

## Deploy

To deploy Charmed Apache Spark using Terraform, use standard TF syntax:

* `terraform init` in order to initialize the modules
* `terraform apply -var-file=<.tfvars.json_filename>`
* `terraform destroy -var-file=<.tfvars.json_filename>`

For more information about Terraform, please refer to the [official docs](https://developer.hashicorp.com/terraform/docs).
