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
| [juju_access_secret.azure_blob_storage_secret_access](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/access_secret) | resource |
| [juju_application.azure_storage](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.azure_storage_integration_hub](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.history_server_azure_storage](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_secret.azure_blob_storage_secret](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/secret) | resource |
| [juju_model.spark](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/model) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_azure_storage"></a> [azure\_storage](#input\_azure\_storage) | Azure Object storage information | <pre>object({<br/>    container       = optional(string, "azurecontainer")<br/>    storage_account = optional(string, "azurestorageaccount")<br/>    protocol        = optional(string, "abfss")<br/>    secret_key      = optional(string, "secret-key")<br/>    path            = optional(string, "spark-events")<br/>  })</pre> | `{}` | no |
| <a name="input_azure_storage_revision"></a> [azure\_storage\_revision](#input\_azure\_storage\_revision) | Charm revision for azure-storage-integrator | `number` | n/a | yes |
| <a name="input_model"></a> [model](#input\_model) | Name of the Spark Juju Model to deploy to | `string` | n/a | yes |
| <a name="input_spark_charms"></a> [spark\_charms](#input\_spark\_charms) | Names of the Spark applications in the Spark Juju model. | `map(string)` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_application"></a> [application](#output\_application) | The deployed application name. |
| <a name="output_charms"></a> [charms](#output\_charms) | The name of the charms which are part of the deployment. |
| <a name="output_provides"></a> [provides](#output\_provides) | Relation endpoint provided by this module. |
