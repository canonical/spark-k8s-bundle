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
| [juju_access_secret.system_users_and_private_key_secret_access](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/access_secret) | resource |
| [juju_application.history_server](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.integration_hub](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.kyuubi](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.history_server_object_storage](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.integration_hub_object_storage](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_data_integrator](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_metastore](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_service_account](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_tls](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_users](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_zookeeper](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_offer.integration_hub_service_account](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_offer.kyuubi_jdbc](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_secret.system_users_and_private_key_secret](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/secret) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_admin_password"></a> [admin\_password](#input\_admin\_password) | The password for the admin user. | `string` | `null` | no |
| <a name="input_data_integrator_endpoint"></a> [data\_integrator\_endpoint](#input\_data\_integrator\_endpoint) | In-model endpoint for the data-integrator application. | <pre>object({<br/>    name     = string<br/>    endpoint = optional(string, "kyuubi")<br/>  })</pre> | n/a | yes |
| <a name="input_history_server"></a> [history\_server](#input\_history\_server) | n/a | <pre>object({<br/>    app_name    = optional(string, "history-server")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    channel     = optional(string, "3/stable")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>  })</pre> | <pre>{<br/>  "app_name": "history-server",<br/>  "base": "ubuntu@22.04",<br/>  "constraints": "arch=amd64",<br/>  "units": 1<br/>}</pre> | no |
| <a name="input_integration_hub"></a> [integration\_hub](#input\_integration\_hub) | n/a | <pre>object({<br/>    app_name    = optional(string, "integration-hub")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    channel     = optional(string, "3/stable")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>  })</pre> | <pre>{<br/>  "app_name": "integration-hub",<br/>  "base": "ubuntu@22.04",<br/>  "constraints": "arch=amd64",<br/>  "units": 1<br/>}</pre> | no |
| <a name="input_kyuubi"></a> [kyuubi](#input\_kyuubi) | n/a | <pre>object({<br/>    app_name    = optional(string, "kyuubi")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    channel     = optional(string, "3.4/stable")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>  })</pre> | <pre>{<br/>  "app_name": "kyuubi",<br/>  "base": "ubuntu@22.04",<br/>  "constraints": "arch=amd64",<br/>  "units": 1<br/>}</pre> | no |
| <a name="input_metastore_endpoint"></a> [metastore\_endpoint](#input\_metastore\_endpoint) | In-model endpoint for the metastore (postgresql-k8s) application. | <pre>object({<br/>    name     = string<br/>    endpoint = optional(string, "database")<br/>  })</pre> | n/a | yes |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Reference to an existing model uuid. | `string` | n/a | yes |
| <a name="input_object_storage_endpoint"></a> [object\_storage\_endpoint](#input\_object\_storage\_endpoint) | In-model endpoint for the object storage integrator application. | <pre>object({<br/>    name     = string<br/>    endpoint = optional(string, "s3_credentials")<br/>  })</pre> | n/a | yes |
| <a name="input_tls_endpoint"></a> [tls\_endpoint](#input\_tls\_endpoint) | In-model endpoint for the TLS certificates provider. | <pre>object({<br/>    name     = string<br/>    endpoint = optional(string, "certificates")<br/>  })</pre> | n/a | yes |
| <a name="input_tls_private_key"></a> [tls\_private\_key](#input\_tls\_private\_key) | The private key to be used for TLS certificates. | `string` | `null` | no |
| <a name="input_users_db_endpoint"></a> [users\_db\_endpoint](#input\_users\_db\_endpoint) | In-model endpoint for the Kyuubi users database (postgresql-k8s) application. | <pre>object({<br/>    name     = string<br/>    endpoint = optional(string, "database")<br/>  })</pre> | n/a | yes |
| <a name="input_zookeeper_endpoint"></a> [zookeeper\_endpoint](#input\_zookeeper\_endpoint) | In-model endpoint for the ZooKeeper application. | <pre>object({<br/>    name     = string<br/>    endpoint = optional(string, "zookeeper")<br/>  })</pre> | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_components"></a> [components](#output\_components) | Map of the deployed applications for this component module. |
| <a name="output_offers"></a> [offers](#output\_offers) | Map of all offers exposed by the component's charms. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of all the provides endpoints. |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of the requires endpoints. |
