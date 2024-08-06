## Deploy Charmed Spark on K8s 

Charmed Spark comes with a bundled set of components that allow you to easily 
manage Spark workloads on K8s, providing integration with object storage,
monitoring and log aggregation. For an overview on the different components
that form Charmed Spark, please refer to [this section](./path/to/explanation.md).

### Prerequisites

Since Charmed Spark will be managed by Juju, make sure that:
* you have a Juju client (e.g. via a [SNAP](https://snapcraft.io/juju)) installed in your local machine  
* you are able to connect to a juju controller
* you have read-write permissions to either a S3-compatible or an Azure object storage

To set up a Juju controller on K8s and the juju client, you can refer to existing tutorials and documentation, e.g. for [MicroK8s](https://juju.is/docs/olm/get-started-with-juju) and for [AWS EKS](https://juju.is/docs/juju/amazon-eks). Also refer to the [How-To Setup Environment](/t/charmed-spark-k8s-documentation-how-to-setup-k8s-environment/11618) userguide to install a S3-compatible object storage on MicroK8s (MinIO), EKS (AWS S3) or Azure object storages. 
For other backends or K8s distributions other than MinIO on MicroK8s and S3 on EKS (e.g. Ceph, Charmed Kubernetes, GKE, etc), please refer to the documentation or your admin.

Charmed Spark supports native integration with the Canonical Observability Stack (COS). To enable monitoring on top of Charmed Spark, make sure that you have a Juju model with COS correctly deployed. To deploy COS on MicroK8s follow the step-by-step [tutorial](https://charmhub.io/topics/canonical-observability-stack/tutorials/install-microk8s) or refer to its [documentation](https://charmhub.io/topics/canonical-observability-stack) for more informations.

### Preparation

#### Juju Model 

Make sure that you have a Juju model where you can deploy the Spark History server. In general, we advise to segregate juju applications belonging to different solutions, and therefore
to have a dedicated model for `Spark` components, e.g.

```bash 
juju add-model <juju_model>
```

> Note that this will create a K8s namespace in which the different Charmed Spark components will be deployed to.

### Deploy Charmed Spark

Charmed Spark can be deployed via 
* Native Juju YAML bundle and overlays
* Terraform modules

#### Using Juju bundles

Juju bundles are provided in the form of Jinja2 templates, for the following distribution:
* Charmed Spark 3.4.x
  * [main `bundle.yaml`](https://github.com/canonical/spark-k8s-bundle/blob/main/releases/3.4/yaml/bundle.yaml.j2)
  * [`overlays`](https://github.com/canonical/spark-k8s-bundle/blob/main/releases/3.4/yaml/overlays) 

You can easily customize these templates from the CLI using `jinja2-cli`:

```shell
pip install jinja2-cli
```

Once the package is installed, you can render the template using

jinja2 -D <key>=<value> bundle.yaml.j2 > bundle.yaml

The following table summarizes the properties to be specified for the main bundle

| key             | Description                                                                                                   |
|-----------------|---------------------------------------------------------------------------------------------------------------|
| service_account | Service Account to be used by Kyuubi Engines (deprecated)                                                     |
| namespace       | Namespace where the charms will be deployed. This should correspond to the name of the Juju model to be used. |
| s3_endpoint     | Endpoint of the S3-compatible object storage backend, in the form of `http(s)//host:port`.                    |
| bucket          | Name of the S3 bucket to be used for storing logs and data                                                    |


Once the bundle is rendered, it can be simply deployed using 

```shell
juju deploy -m <juju_model> ./bundle.yaml
```

After some time, you will see that most of the charms will be in a blocked status because of missing or invalid S3 credentials.
In particular, the `s3` charm should be notifying that it needs to be provided with the access and secret key. This can be done using the action

```shell
juju run s3/leader sync-s3-credentials \
  access-key=<access-key> secret-key=<secret-key>
```

After this, the different charms should start to receive the credentials and move into `active/idle` state.

##### Enabling COS

COS can be enabled using an [overlay](https://github.com/canonical/spark-k8s-bundle/blob/main/releases/3.4/yaml/overlays/cos-integration.yaml.j2). 
Similarly to the main bundle, the jinja2 template for the overlay can be rendered with the following properties:

| key            | Description                                   | Default |
|----------------|-----------------------------------------------|---------|
| cos_controller | Name of the controller hosting the COS model. | micro   |
| cos_model      | Name of the COS model                         | cos     |

Once the template is rendered, the COS-enabled Charmed Spark bundle can be deployed using:

```shell
juju deploy -m <juju_model> ./bundle.yaml --overlay cos-integration.yaml
```

#### Using Terraform

Make sure you have a working Terraform 1.8+ installed in your machine. You can install [Terraform](https://snapcraft.io/terraform) or [OpenTofu](https://snapcraft.io/terraform) via a snap.

Terraform modules make use of the Terraform Juju provider. More information about the Juju provider can be found [here](https://registry.terraform.io/providers/juju/juju/latest/docs).

The [Charmed Spark Terraform module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform) is composed of the following submodules:
* [base module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform/base) that bundles all the base resources of the Charmed Spark solution 
* [cos-integration module](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform/cos) that bundles all the resources that enable integration with COS

The Charmed Spark Terraform modules can be configured using a `.tfvars.json` file with the following schema:

```json
{
  "s3": {
    "bucket": <bucket_name>,
    "endpoint": <s3_endpoint>
  },
  "kyuubi_user": <kyuubi_service_account>,
  "model": <juju_model>,
  "cos_model": <cos_model> 
}
```

The following table provides the description of the different configuration option

| key         | Description                                                                                                                           |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------|
| kyuubi_user | Service Account to be used by Kyuubi Engines (deprecated)                                                                             |
| model       | Namespace where the charms will be deployed. This should correspond to the name of the Juju model to be used.                         |
| s3.endpoint | Endpoint of the S3-compatible object storage backend, in the form of `http(s)//host:port`.                                            |
| s3.bucket   | Name of the S3 bucket to be used for storing logs and data                                                                            |
| cos_model   | (Optional) Name of the model where COS is deployed. If omitted, the resource of the cos-integration submodules will not be deployed   |

> :warning: **NOTE**: The Juju Terraform provider does not yet support cross-controller relations with COS. Therefore, COS model must be hosted in the same controller as the Charmed Spark model. 

In order to deploy Charmed Spark using terraform, use standard TF syntax

* `terraform init` in order to initialize the modules
* `terraform apply -var-file=<.tfvars.json_filename>`
* `terraform destroy -var-file=<.tfvars.json_filename>`

For more information about Terraform, please refer to the [official docs](https://developer.hashicorp.com/terraform/docs).