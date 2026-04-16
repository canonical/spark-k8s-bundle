# Data-integrator charm terraform module

To be contributed upstream.

## Module reference

<!-- BEGIN_TF_DOCS -->
### Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.0.0 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >=1.0.0 |

### Providers

| Name | Version |
|------|---------|
| <a name="provider_juju"></a> [juju](#provider\_juju) | >=1.0.0 |

### Modules

No modules.

### Resources

| Name | Type |
|------|------|
| [juju_application.data_integrator](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |

### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_app_name"></a> [app\_name](#input\_app\_name) | Name to give the deployed application. | `string` | `"data-integrator"` | no |
| <a name="input_base"></a> [base](#input\_base) | The operating system on which to deploy | `string` | `"ubuntu@24.04"` | no |
| <a name="input_channel"></a> [channel](#input\_channel) | Channel of the charm. | `string` | `"latest/stable"` | no |
| <a name="input_config"></a> [config](#input\_config) | Map for configuration options. | <pre>object({<br/>    database-name = optional(string, "integrator")<br/>  })</pre> | `{}` | no |
| <a name="input_constraints"></a> [constraints](#input\_constraints) | String listing constraints for this application. | `string` | `"arch=amd64"` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Reference to an existing model uuid. | `string` | n/a | yes |
| <a name="input_revision"></a> [revision](#input\_revision) | Revision number of the charm. | `number` | `null` | no |
| <a name="input_units"></a> [units](#input\_units) | Unit count. | `number` | `1` | no |

### Outputs

| Name | Description |
|------|-------------|
| <a name="output_application"></a> [application](#output\_application) | Object representing the deployed application. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of all the provided endpoints. |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of all the required endpoints. |
<!-- END_TF_DOCS -->
