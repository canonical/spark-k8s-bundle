(how-to-deploy-spark)=
# Deploy Charmed Apache Spark

Charmed Apache Spark comes with a bundled set of components that allow you to easily manage Apache
Spark workloads on K8s, providing integration with object storage, monitoring and log aggregation.
For an overview on the different components that form Charmed Apache Spark, please refer to the
[components overview](explanation-component-overview) page.

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

### Juju model

Make sure that you have a Juju model where you can deploy the Spark History server.
In general, we advise to segregate Juju applications belonging to different solutions, and therefore
to have a dedicated model for `Spark` components, e.g.:

```bash 
juju add-model <juju_model>
```

```{note}
Note that this will create a K8s namespace to which the different Charmed Apache Spark components will be deployed.
```

## Deploy

Charmed Apache Spark can be deployed via:

* Native Juju YAML bundle and overlays
* Terraform modules

### Using Juju bundles

Juju bundles are provided in the form of Jinja2 templates, for the following distribution:

* Charmed Apache Spark 3.4.x
  * [main `bundle.yaml`](https://github.com/canonical/spark-k8s-bundle/blob/main/releases/3.4/yaml/bundle.yaml.j2)
  * [`overlays`](https://github.com/canonical/spark-k8s-bundle/blob/main/releases/3.4/yaml/overlays)

You can easily customize these templates from the CLI using `jinja2-cli`:

```shell
pip install jinja2-cli
```

Once the package is installed, you can render the template using

```shell
jinja2 -D <key>=<value> bundle.yaml.j2 > bundle.yaml
```

There exist different YAML bundles, with different configuration options,
for S3 and Azure object storage backends. Please, refer to the next sections for
more information about how to configure the deployments for the different
object storage backends.

Once the bundle is rendered, it can be simply deployed:

```shell
juju deploy -m <juju_model> ./bundle.yaml
```

#### S3 backends

The following table summarizes the properties to be specified for the main bundle

| key             | Description                                                                                                   |
|-----------------|---------------------------------------------------------------------------------------------------------------|
| `service_account` | Service Account to be used by Apache Kyuubi Engines (deprecated)                                                     |
| `namespace`       | Namespace where the charms will be deployed. This should correspond to the name of the Juju model to be used. |
| `s3_endpoint`     | Endpoint of the S3-compatible object storage backend, in the form of `http(s)//host:port`.                    |
| `bucket`          | Name of the S3 bucket to be used for storing logs and data                                                    |

Once the bundle is deployed, you will see that most of the charms will be in a blocked status
because of missing or invalid S3 credentials.
In particular, the `s3` charm should notify that it needs to be provided with access and a secret key.
This can be done using the `sync-s3-credentials` action:

```shell
juju run s3/leader sync-s3-credentials \
  access-key=<access-key> secret-key=<secret-key>
```

After this, the charms should start to receive the credentials and move into `active/idle` state.

#### Azure storage backends

The following table summarizes the properties to be specified for the main Azure bundle.

| Key             | Description                                                                                                   |
|-----------------|---------------------------------------------------------------------------------------------------------------|
| `service_account` | Service Account to be used by Apache Kyuubi Engines                                                                  |
| `namespace`       | Namespace where the charms will be deployed. This should correspond to the name of the Juju model to be used. |
| `storage_account` | Name of the Azure storage account to be used.                                                                 |
| `container`       | Name of the Azure storage container to be used for storing logs and data                                      |

Create a Juju secret holding the values for the Azure secret key:

```shell
juju add-secret azure-credentials secret-key=<AZURE_STORAGE_KEY>
```

This should prompt the `secret:<secret_id>` that can be used to configure the bundle.
To do so, first grant access to the secret for the Azure Storage Integrator charm

```shell
juju grant-secret <secret_id> azure-storage
```

Then, you can configure the charm to use the secret

```shell
juju config azure-storage credentials=secret:<secret_id> 
```

After this, the different charms should start to receive the credentials and move into `active/idle` state.

```{caution}
The Azure Storage Integrator charm assumes hierarchical namespaces to have been enabled by default.
When you create a new storage account, please make sure you check the "Hierarchical Namespaces" checkbox.
If you want to use a legacy storage account that doesn't have hierarchical namespaces enabled,
please configure Azure Storage integrator charm to use WASB / WASBS protocol instead with:
`juju config azure-storage connection-protocol=wasbs`
```

```{caution}
The directory `spark-events` needs to be created beforehand in the Azure container for the Spark History server to work.
Please refer to the [How-To Setup Environment](how-to-deploy-environment) guide for more detailed instructions.
```

#### Enabling COS

COS can be enabled using an [overlay](https://github.com/canonical/spark-k8s-bundle/blob/main/releases/3.4/yaml/overlays/cos-integration.yaml.j2).
Similarly to the main bundle, the jinja2 template for the overlay can be rendered with the following properties:

| key            | Description                                   | Default |
|----------------|-----------------------------------------------|---------|
| `cos_controller` | Name of the controller hosting the COS model. | micro   |
| `cos_model`      | Name of the COS model                         | cos     |

Once the template is rendered, the COS-enabled Charmed Apache Spark bundle can be deployed using:

```shell
juju deploy -m <juju_model> ./bundle.yaml --overlay cos-integration.yaml
```

### Using Terraform

Make sure you have a working Terraform 1.8+ installed in your machine.
You can install [Terraform](https://snapcraft.io/terraform) or
[OpenTofu](https://snapcraft.io/terraform) via a snap.

Terraform modules make use of the Terraform Juju provider.
More information about the Juju provider can be found in the
[Terraform documentation](https://registry.terraform.io/providers/juju/juju/latest/docs).

The [Charmed Apache Spark Terraform module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform)
is composed of the following submodules:

* [base module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform/modules/spark)
  that bundles all the base resources of the Charmed Apache Spark solution
* [cos-integration module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform/modules/observability)
  that bundles all the resources that enable integration with COS

```{caution}
Currently only S3 storage backends are supported for Terraform-based bundles.
```

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

```{caution}
The Juju Terraform provider does not yet support cross-controller relations with COS.
Therefore, COS model must be hosted in the same controller as the Charmed Apache Spark model. 
```

To deploy Charmed Apache Spark using Terraform, use standard TF syntax:

* `terraform init` in order to initialize the modules
* `terraform apply -var-file=<.tfvars.json_filename>`
* `terraform destroy -var-file=<.tfvars.json_filename>`

For more information about Terraform, please refer to the [official docs](https://developer.hashicorp.com/terraform/docs).
