# ZooKeeper charm terraform module

To be contributed upstream.

## Module reference

<!-- BEGIN_TF_DOCS -->
### Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.0.0 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >=1.0.0 |

### Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_juju"></a> [juju](#provider\_juju) | 1.3.1 |

### Modules

No modules.

### Resources

| Name | Type |
| ---- | ---- |
| [juju_application.zookeeper](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |

### Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_app_name"></a> [app\_name](#input\_app\_name) | Name to give the deployed application. | `string` | `"zookeeper"` | no |
| <a name="input_base"></a> [base](#input\_base) | The operating system on which to deploy. E.g. ubuntu@22.04. | `string` | `null` | no |
| <a name="input_channel"></a> [channel](#input\_channel) | Channel of the charm. | `string` | `"3/stable"` | no |
| <a name="input_config"></a> [config](#input\_config) | Map for configuration options. | `map(string)` | `{}` | no |
| <a name="input_constraints"></a> [constraints](#input\_constraints) | String listing constraints for this application. | `string` | `"arch=amd64"` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Reference to an existing model uuid. | `string` | n/a | yes |
| <a name="input_resources"></a> [resources](#input\_resources) | Resources to attach to the application (e.g. OCI images). | `map(string)` | `null` | no |
| <a name="input_revision"></a> [revision](#input\_revision) | Revision number of the charm. | `number` | `null` | no |
| <a name="input_storage_size"></a> [storage\_size](#input\_storage\_size) | Storage size for the zookeeper data. | `string` | `"10G"` | no |
| <a name="input_units"></a> [units](#input\_units) | Unit count. 3 units are recommended for high availability. | `number` | `3` | no |

### Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_application"></a> [application](#output\_application) | Object representing the deployed application. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of all the provided endpoints. |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of all the required endpoints. |
<!-- END_TF_DOCS -->
