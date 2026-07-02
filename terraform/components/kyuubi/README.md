# Kyuubi component terraform module

Manages the Kyuubi SQL engine charm with all necessary integrations for use in conjunction with the spark-core module.

## Module reference

The kyuubi component module provides a complete deployment of the Kyuubi SQL engine with all necessary integrations.

### Inputs

**Application Configuration:**
- `kyuubi`: Configuration object for Kyuubi application with the following attributes:
  - `app_name`: Name to give the deployed Kyuubi application (default: "kyuubi")
  - `base`: The operating system on which to deploy Kyuubi (default: "ubuntu@22.04")
  - `track`: Track of the Kyuubi charm (default: "3.4")
  - `config`: Map for Kyuubi configuration options (default: {})
  - `constraints`: String listing constraints for the Kyuubi application (default: "arch=amd64")
  - `resources`: Resources to attach to the Kyuubi application (default: null)
  - `revision`: Revision number of the Kyuubi charm (default: null)
  - `units`: Unit count for Kyuubi (default: 1)

**Risk Channel:**
- `risk`: Component's charms risk channel (default: "stable")

**Module Dependencies:**
- `model_uuid`: Reference to an existing model uuid (required)

**External Integrations:**
- `spark_service_account`: External integration for the Spark service account (integration hub) application (required)
- `certificates`: External integration for the certificate provider application (required)
- `data_integrator`: External integration for the data-integrator application (required)
- `metastore`: External integration for the metastore (postgresql-k8s) application (required)
- `users_db`: External integration for the Kyuubi users database (postgresql-k8s) application (required)
- `zookeeper`: External integration for the ZooKeeper application (required)

### Outputs

- `application`: Object representing the deployed Kyuubi application
- `components`: Map of the deployed applications (kyuubi)
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
| [juju_application.kyuubi](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.kyuubi_certificates](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_data_integrator](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_metastore](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_service_account](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_users_db](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_zookeeper](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_offer.kyuubi_jdbc](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_charm.kyuubi](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/charm) | data source |

### Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_certificates"></a> [certificates](#input\_certificates) | External integration for the certificate provider application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_data_integrator"></a> [data\_integrator](#input\_data\_integrator) | External integration for the data-integrator application | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_kyuubi"></a> [kyuubi](#input\_kyuubi) | n/a | <pre>object({<br/>    app_name    = optional(string, "kyuubi")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(any))<br/>    revision    = optional(number)<br/>    track       = optional(string, "4.0")<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_metastore"></a> [metastore](#input\_metastore) | External integration for the metastore (postgresql-k8s) application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Reference to an existing model uuid. | `string` | n/a | yes |
| <a name="input_risk"></a> [risk](#input\_risk) | Component's charms risk channel | `string` | `"stable"` | no |
| <a name="input_spark_service_account"></a> [spark\_service\_account](#input\_spark\_service\_account) | External integration for the object storage integrator application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_users_db"></a> [users\_db](#input\_users\_db) | External integration for the Kyuubi users database (postgresql-k8s) application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_zookeeper"></a> [zookeeper](#input\_zookeeper) | External integration for the ZooKeeper application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |

### Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_application"></a> [application](#output\_application) | Object representing the deployed Kyuubi application. |
| <a name="output_components"></a> [components](#output\_components) | Map of the deployed applications for this component module. |
| <a name="output_offers"></a> [offers](#output\_offers) | Map of all offers exposed by the component's charms. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of all the provides endpoints. |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of the requires endpoints. |
<!-- END_TF_DOCS -->