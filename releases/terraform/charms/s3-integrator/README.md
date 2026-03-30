## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.0.0 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >=1.0.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_juju"></a> [juju](#provider\_juju) | 1.3.1 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [juju_application.s3](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.s3_history_server](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.s3_integration_hub](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_model.spark](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/model) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_model"></a> [model](#input\_model) | Name of the Spark Juju Model to deploy to | `string` | n/a | yes |
| <a name="input_s3"></a> [s3](#input\_s3) | S3 Bucket information | <pre>object({<br/>    bucket   = optional(string, "spark-bucket")<br/>    endpoint = optional(string, "https://s3.amazonaws.com")<br/>    region   = optional(string, "us-east-1")<br/>  })</pre> | <pre>{<br/>  "bucket": "spark-bucket",<br/>  "endpoint": "https://s3.amazonaws.com",<br/>  "region": "us-east-1"<br/>}</pre> | no |
| <a name="input_s3_revision"></a> [s3\_revision](#input\_s3\_revision) | Charm revision for s3-integrator | `number` | n/a | yes |
| <a name="input_spark_charms"></a> [spark\_charms](#input\_spark\_charms) | Names of the Spark applications in the Spark Juju model. | `map(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_application"></a> [application](#output\_application) | The deployed application name. |
| <a name="output_charms"></a> [charms](#output\_charms) | The name of the charms which are part of the deployment. |
| <a name="output_provides"></a> [provides](#output\_provides) | Relation endpoint provided by this module. |
