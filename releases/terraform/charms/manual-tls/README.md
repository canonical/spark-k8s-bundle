## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.0.0 |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.0.0 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >=1.0.0 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >=1.0.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_juju"></a> [juju](#provider\_juju) | >=1.0.0 >=1.0.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [juju_application.certificates](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_app_name"></a> [app\_name](#input\_app\_name) | n/a | `string` | `"certificates"` | no |
| <a name="input_channel"></a> [channel](#input\_channel) | n/a | `string` | `"latest/stable"` | no |
| <a name="input_example"></a> [example](#input\_example) | Example variable | `string` | `""` | no |
| <a name="input_model"></a> [model](#input\_model) | n/a | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_app_name"></a> [app\_name](#output\_app\_name) | Name of the deployed application. |
| <a name="output_example"></a> [example](#output\_example) | Example output |
| <a name="output_provides"></a> [provides](#output\_provides) | n/a |
