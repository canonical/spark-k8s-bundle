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
is a reusable product module, that consists of all charms in the Charmed Apache Spark solution including the integration between
the charms. In order to use it, create a new file named `main.tf` in a local directory, and use the following Terrform code:

```hcl
terraform {
  required_version = ">=1.0.0"

  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">=1.0.0"
    }
  }
}

module "spark" {
  source     = "git::https://github.com/canonical/spark-k8s-bundle//terraform/products/charmed-spark-3.4?ref=terraform-cc008"

  history_server_image       = "ghcr.io/canonical/charmed-spark:3.4-22.04_stable"
  integration_hub_image      = "ghcr.io/canonical/spark-integration-hub:3-22.04_stable"
  kyuubi_image               = "ghcr.io/canonical/charmed-spark-kyuubi:3.4-22.04_stable"

  spark_model_name           = "spark"
  admin_password             = "<kyuubi-admin-password>"
  tls_private_key            = "<base-64-encoded-private-key>"
  kyuubi_config              = {"service-account": "kyuubi-user"}

  storage_backend            = "s3"
  s3_access_key              = "<s3-access-key>"
  s3_secret_key              = "<s3-secret-key>"
  s3_config                  = {"endpoint": "<s3-endpoint>", "region": "<s3-region>", "bucket": "<s3-bucket>", "path": "spark-events/"}
}
```

```{caution}
The example here assumes we want to use Apache Spark 3.4. If you wish to use a different Apache Spark version, please make sure you use
the correct source of the Terraform module, and also the correct OCI images for `history_server_image` and `kyuubi_image`. For instance, 
if you'd wish to use Apache Spark 4.0, you would need use the source `charmed-spark-4.0` and specify `history_server_image` and `kyuubi_image`
as `ghcr.io/canonical/charmed-spark:4.0-22.04_stable` and `ghcr.io/canonical/charmed-spark-kyuubi:4.0-22.04_stable` respectively.
```

The following table provides the description of the different options:

| key         | Description                                                                                                                           |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `history_server_image` | The Apache Spark image to use as workload for Spark History Server charm                                                                             |
| `integration_hub_image`       | The OCI image to use as workload for Spark Integration Hub charm                         |
| `kyuubi_image` | The OCI image to use as workload for Kyuubi K8s charm                                            |
| `spark_model_name`   | The name of the Juju model where the bundle is to be deployed                                                                            |
| `admin_password`   | The password to set for the `admin` user that is used later to connect to Kyuubi   |
| `tls_private_key` | The private key to be used for generating Kyuubi TLS certificates, provided as base64-encoded string |
| `kyuubi_config.service-account` | The service account which is used by Kyuubi to run Spark jobs |
| `storage_backend` | The object storage backend to be used. The backends `s3` and `azure_storage` are supported. |
| `s3_access_key` | The S3 access key ID |
| `s3_secret_key` | The S3 secret key |
| `s3_config.endpoint` | The S3 endpoint |
| `s3_config.region` | The S3 region |
| `s3_config.bucket` | The name of the S3 bucket to be used |
| `s3_config.path` | The path inside the S3 bucket to be used |

The following command can be used to generate a new private key and get its base64-encoded value:

```bash
openssl genrsa -out private.key  2048
base64 private.key -w0
```

If you'd wish to use Azure Storage as a storage backend instead, you'd need to configure the Azure Storage specific options, as follows:

```hcl
terraform {
  required_version = ">=1.0.0"

  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">=1.0.0"
    }
  }
}

module "spark" {
  source     = "git::https://github.com/canonical/spark-k8s-bundle//terraform/products/charmed-spark-3.4?ref=terraform-cc008"

  history_server_image       = "ghcr.io/canonical/charmed-spark:3.4-22.04_stable"
  integration_hub_image      = "ghcr.io/canonical/spark-integration-hub:3-22.04_stable"
  kyuubi_image               = "ghcr.io/canonical/charmed-spark-kyuubi:3.4-22.04_stable"

  spark_model_name           = "spark"
  admin_password             = "<kyuubi-admin-password>"
  tls_private_key            = "<base-64-encoded-private-key>"
  kyuubi_config              = {"service-account": "kyuubi-user"}

  storage_backend            = "azure_storage"
  azure_storage_secret_key   = "<azure-storage-secret-key>"
  azure_storage_config       = {"container": "<azure-storage-container>", "storage-account": "<azure-storage-account>", "protocol": "<storage-protocol>", "path": "spark-events/"}
}
```

The following table provides the description of the Azure Storage specific options:

| key         | Description                                                                                                                           |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `azure_storage_secret_key` | The Azure Storage account secret key |
| `azure_storage_config.container` | The name of the Azure Storage container to be used |
| `azure_storage_config.storage-account` | The Azure Storage account to be used |
| `azure_storage_config.protocol` | The connection protocol to be used. Valid values are `http`, `https`, `abfs`, `abfss`, `wasb` and `wasbs`. |
| `azure_storage_config.path` | The path inside the Azure Storage container to be used |

The `main.tf` module we just created will not deploy the Canonical Observability Stack (COS) and thus by default the bundle would not have observability enabled.
To enable observability using COS, add an additional COS module in the same `main.tf` file, and wire it to work with the `spark` module, as follows:

```hcl
terraform {
  required_version = ">=1.0.0"

  required_providers {
    juju = {
      source  = "juju/juju"
      version = ">=1.0.0"
    }
  }
}

resource "juju_model" "cos" {
  name = "cos"
}

module "cos" {
  source       = "git::https://github.com/canonical/observability-stack//terraform/cos-lite?ref=04ab6c618dbbec62292a052a61cdb402d80e5974"
  model_uuid   = juju_model.cos.uuid
}

module "spark" {
  source     = "git::https://github.com/canonical/spark-k8s-bundle//terraform/products/charmed-spark-3.4?ref=terraform-cc008"

  history_server_image       = "ghcr.io/canonical/charmed-spark:3.4-22.04_stable"
  integration_hub_image      = "ghcr.io/canonical/spark-integration-hub:3-22.04_stable"
  kyuubi_image               = "ghcr.io/canonical/charmed-spark-kyuubi:3.4-22.04_stable"

  spark_model_name           = "spark"
  admin_password             = "<kyuubi-admin-password>"
  tls_private_key            = "<base-64-encoded-private-key>"
  kyuubi_config              = {"service-account": "kyuubi-user"}

  storage_backend            = "s3"
  s3_access_key              = "<s3-access-key>"
  s3_secret_key              = "<s3-secret-key>"
  s3_config                  = {"endpoint": "<s3-endpoint>", "region": "<s3-region>", "bucket": "<s3-bucket>", "path": "spark-events/"}

  cos_offers                 = {
    dashboard = module.cos.offers.grafana_dashboards.url
    logging   = module.cos.offers.loki_logging.url
    metrics   = module.cos.offers.prometheus_receive_remote_write.url
  }
}
```

The added section creates a new Juju model named `cos`, deploys COS in that model, and the `grafana_dashboards`, `loki_logging` and `prometheus_receive_remote_write` offers are provided as `cos_offers` to the `spark` module.

For the full list of input configurations supported, and the reference of the Charmed Apache Spark Teform bundle, please refer to the README corresponding to the product module in [`spark-k8s-bundle` repository](https://github.com/canonical/spark-k8s-bundle/tree/terraform-cc008/terraform/products).

## Deploy

To deploy Charmed Apache Spark using Terraform, first initialize the terraform modules. To do so, run the following command while being on the directory which contains the `main.tf` file you created in the previous step.

```shell
terraform init
```

Once the terraform modules are initialized, deploy the solution with the following command:

```shell
terraform apply
```

Once prompted with the Terraform plan, verify the plan and type "yes" in the prompt. The deployment will then begin and take some time. Once the deployment completes, verify the deployment with the `juju status` command as follows:

```shell
# for charms in the spark model
juju switch spark
juju status

# for charms in the cos model (if you deployed with COS)
juju status --model cos
```

Once everything settles to idle, you may test connection with Kyuubi using [this section of documentation on Charmed Apache Kyuubi](kyuubi.md#connect). Please note that most of the charms and integrations in that section of documentation are already deployed alongside the bundle, in which case you can skip deploying / integrating them.

For more information about Terraform, please refer to the [official docs](https://developer.hashicorp.com/terraform/docs).
