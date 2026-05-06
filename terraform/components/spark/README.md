# Spark (3.4) component terraform module

Bundles the following charms:
- Spark History Server
- Spark Integration Hub
- Kyuubi

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
| [juju_application.history_server](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.integration_hub](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.kyuubi](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.history_server_object_storage](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.integration_hub_object_storage](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_certificates](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_data_integrator](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_metastore](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_service_account](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_users_db](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_zookeeper](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_offer.integration_hub_service_account](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_offer.kyuubi_jdbc](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |

### Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_certificates"></a> [certificates](#input\_certificates) | External integration for the certificate provider application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_data_integrator"></a> [data\_integrator](#input\_data\_integrator) | External integration for the data-integrator application | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_history_server"></a> [history\_server](#input\_history\_server) | n/a | <pre>object({<br/>    app_name    = optional(string, "history-server")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    track       = optional(string, "3")<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_integration_hub"></a> [integration\_hub](#input\_integration\_hub) | n/a | <pre>object({<br/>    app_name    = optional(string, "integration-hub")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    track       = optional(string, "3")<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_kyuubi"></a> [kyuubi](#input\_kyuubi) | n/a | <pre>object({<br/>    app_name    = optional(string, "kyuubi")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    track       = optional(string, "3.4")<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_metastore"></a> [metastore](#input\_metastore) | External integration for the metastore (postgresql-k8s) application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Reference to an existing model uuid. | `string` | n/a | yes |
| <a name="input_object_storage"></a> [object\_storage](#input\_object\_storage) | External integration for the object storage integrator application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_object_storage_interface"></a> [object\_storage\_interface](#input\_object\_storage\_interface) | The interface of the object storage backend. | `string` | n/a | yes |
| <a name="input_risk"></a> [risk](#input\_risk) | Component's charms risk channel | `string` | `"stable"` | no |
| <a name="input_users_db"></a> [users\_db](#input\_users\_db) | External integration for the Kyuubi users database (postgresql-k8s) application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_zookeeper"></a> [zookeeper](#input\_zookeeper) | External integration for the ZooKeeper application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |

### Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_components"></a> [components](#output\_components) | Map of the deployed applications for this component module. |
| <a name="output_offers"></a> [offers](#output\_offers) | Map of all offers exposed by the component's charms. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of all the provides endpoints. |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of the requires endpoints. |
<!-- END_TF_DOCS -->
