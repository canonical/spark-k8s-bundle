# Spark-Core component terraform module

The `spark-core` component bundles the following charms:
- Spark History Server
- Spark Integration Hub

## Module reference

The spark-core module provides the core components for the Spark ecosystem, including the history server for tracking job execution history and the integration hub for managing integrations with external services.

### Inputs

- `history_server`: Configuration for the Spark History Server application
- `integration_hub`: Configuration for the Spark Integration Hub application
- `object_storage`: External integration for the object storage integrator application
- `object_storage_interface`: The interface of the object storage backend (s3-credentials or azure-storage-credentials)
- `model_uuid`: Reference to an existing model uuid
- `risk`: Component's charms risk channel (edge, beta, candidate, or stable; default: stable)

### Outputs

- `components`: Map of the deployed applications (history_server, integration_hub)
- `requires`: Map of the requires endpoints
- `provides`: Map of the provides endpoints
- `offers`: Map of all offers exposed by the component's charms

<!-- BEGIN_TF_DOCS -->
### Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.0.0 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >=1.4.0 |

### Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_juju"></a> [juju](#provider\_juju) | >=1.4.0 |

### Modules

No modules.

### Resources

| Name | Type |
| ---- | ---- |
| [juju_application.history_server](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.integration_hub](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.history_server_object_storage](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.integration_hub_object_storage](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_offer.integration_hub_service_account](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_charm.spark](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/charm) | data source |

### Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_history_server"></a> [history\_server](#input\_history\_server) | n/a | <pre>object({<br/>    app_name    = optional(string, "history-server")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(any))<br/>    revision    = optional(number)<br/>    track       = optional(string, "3")<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_integration_hub"></a> [integration\_hub](#input\_integration\_hub) | n/a | <pre>object({<br/>    app_name    = optional(string, "integration-hub")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(any))<br/>    revision    = optional(number)<br/>    track       = optional(string, "3")<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Reference to an existing model uuid. | `string` | n/a | yes |
| <a name="input_object_storage"></a> [object\_storage](#input\_object\_storage) | External integration for the object storage integrator application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_object_storage_interface"></a> [object\_storage\_interface](#input\_object\_storage\_interface) | The interface of the object storage backend. | `string` | n/a | yes |
| <a name="input_risk"></a> [risk](#input\_risk) | Component's charms risk channel | `string` | `"stable"` | no |

### Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_components"></a> [components](#output\_components) | Map of the deployed applications for this component module. |
| <a name="output_offers"></a> [offers](#output\_offers) | Map of all offers exposed by the component's charms. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of all the provides endpoints. |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of the requires endpoints. |
<!-- END_TF_DOCS -->