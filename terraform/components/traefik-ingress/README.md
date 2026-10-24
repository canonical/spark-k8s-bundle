# Traefik Ingress component Terraform module

The `traefik-ingress` component deploys the Traefik Kubernetes charm and integrates it with a certificate provider. It exposes the application and its provided and required endpoints for use by other components.

## Module reference

### Inputs

- `model_uuid`: UUID of the Juju model where Traefik is deployed (required)
- `app_name`: Name of the deployed Traefik application (default: `"traefik"`)
- `base`: Base operating system for the application (default: `null`)
- `channel`: Charm channel to deploy from (required)
- `config`: Traefik charm configuration (default: `{}`)
- `constraints`: Juju constraints for the application (default: `"arch=amd64"`)
- `resources`: Charm resources to deploy (default: `{}`)
- `revision`: Charm revision to deploy (default: `null`)
- `storage_directives`: Storage directives for the application (default: `{}`)
- `units`: Number of application units (default: `1`)
- `certificates`: Certificate provider integration, supplied as an in-model endpoint or cross-model offer (required)

### Outputs

- `app_name`: Name of the deployed Traefik application
- `application`: Deployed Traefik application
- `provides`: Map of endpoints exposed by the Traefik charm
- `requires`: Map of endpoints consumed by the Traefik charm

<!-- BEGIN_TF_DOCS -->
### Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >= 1.1.1 |

### Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_juju"></a> [juju](#provider\_juju) | >= 1.1.1 |

### Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_traefik"></a> [traefik](#module\_traefik) | git::https://github.com/canonical/traefik-k8s-operator//terraform | traefik-k8s-rev478 |

### Resources

| Name | Type |
| ---- | ---- |
| [juju_integration.traefik_certificates](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |

### Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_app_name"></a> [app\_name](#input\_app\_name) | Name to give the deployed Traefik application. | `string` | `"traefik"` | no |
| <a name="input_base"></a> [base](#input\_base) | The operating system on which to deploy. | `string` | `null` | no |
| <a name="input_certificates"></a> [certificates](#input\_certificates) | External integration for the certificate provider application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_channel"></a> [channel](#input\_channel) | Channel that the charm is deployed from. | `string` | n/a | yes |
| <a name="input_config"></a> [config](#input\_config) | Map of the charm configuration options. | `map(string)` | `{}` | no |
| <a name="input_constraints"></a> [constraints](#input\_constraints) | String listing constraints for this application. | `string` | `"arch=amd64"` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | UUID of the Juju model where Traefik ingress is deployed. | `string` | n/a | yes |
| <a name="input_resources"></a> [resources](#input\_resources) | The charm's resources. | `map(string)` | `{}` | no |
| <a name="input_revision"></a> [revision](#input\_revision) | Revision number of the charm. | `number` | `null` | no |
| <a name="input_storage_directives"></a> [storage\_directives](#input\_storage\_directives) | Map of storage used by the application. | `map(string)` | `{}` | no |
| <a name="input_units"></a> [units](#input\_units) | Unit count/scale. | `number` | `1` | no |

### Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_app_name"></a> [app\_name](#output\_app\_name) | Name of the deployed Traefik application. |
| <a name="output_application"></a> [application](#output\_application) | The deployed Traefik application. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of the provides endpoints exposed by the charm. |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of the requires endpoints consumed by the charm. |
<!-- END_TF_DOCS -->
