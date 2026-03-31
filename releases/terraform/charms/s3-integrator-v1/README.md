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
| [juju_application.s3_integrator](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_offer.s3_credentials](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_app_name"></a> [app\_name](#input\_app\_name) | Name to give the deployed application. | `string` | `"s3-integrator"` | no |
| <a name="input_base"></a> [base](#input\_base) | The operating system on which to deploy | `string` | `"ubuntu@22.04"` | no |
| <a name="input_channel"></a> [channel](#input\_channel) | Channel of the charm. | `string` | `"1/stable"` | no |
| <a name="input_config"></a> [config](#input\_config) | Map for configuration options. | <pre>object({<br/>    attributes                          = optional(string, "")<br/>    bucket                              = optional(string, "spark-bucket")<br/>    endpoint                            = optional(string, "https://s3.amazonaws.com")<br/>    experimental-delete-older-than-days = optional(number, 14)<br/>    path                                = optional(string, "path/")<br/>    region                              = optional(string, "us-east-1")<br/>    s3-api-version                      = optional(string, "2")<br/>    s3-uri-style                        = optional(string, "2")<br/>    storage-class                       = optional(string, "")<br/>    tls-ca-chain                        = optional(string, "")<br/>  })</pre> | `{}` | no |
| <a name="input_constraints"></a> [constraints](#input\_constraints) | String listing constraints for this application. | `string` | `null` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Reference to an existing model uuid. | `string` | n/a | yes |
| <a name="input_revision"></a> [revision](#input\_revision) | Revision number of the charm. | `number` | `null` | no |
| <a name="input_units"></a> [units](#input\_units) | Unit count. | `number` | `1` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_application"></a> [application](#output\_application) | Object representing the deployed application. |
| <a name="output_offers"></a> [offers](#output\_offers) | Map of all offers exposed by the single charm. |
| <a name="output_provides"></a> [provides](#output\_provides) | Provides endpoints. |
