## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.0.0 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >=1.0.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_juju"></a> [juju](#provider\_juju) | >=1.0.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [juju_access_secret.system_users_and_private_key_secret_access](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/access_secret) | resource |
| [juju_application.data_integrator](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.history_server](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.integration_hub](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.kyuubi](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.kyuubi_users](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.metastore](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.zookeeper](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.kyuubi_data_integrator](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_metastore](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_service_account](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_tls](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_users](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_zookeeper](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_offer.integration_hub](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_offer.metastore](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_secret.system_users_and_private_key_secret](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/secret) | resource |
| [juju_model.spark](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/model) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_admin_password"></a> [admin\_password](#input\_admin\_password) | The password for the admin user. | `string` | `null` | no |
| <a name="input_data_integrator_revision"></a> [data\_integrator\_revision](#input\_data\_integrator\_revision) | Charm revision for data-integrator | `number` | n/a | yes |
| <a name="input_driver_pod_template"></a> [driver\_pod\_template](#input\_driver\_pod\_template) | Define K8s driver pod from a file accessible to the `spark-submit` process. | `string` | `null` | no |
| <a name="input_enable_dynamic_allocation"></a> [enable\_dynamic\_allocation](#input\_enable\_dynamic\_allocation) | Enable dynamic allocation of pods for Spark jobs. | `bool` | `false` | no |
| <a name="input_executor_pod_template"></a> [executor\_pod\_template](#input\_executor\_pod\_template) | Define K8s executor pod from a file accessible to the `spark-submit` process. | `string` | `null` | no |
| <a name="input_history_server_image"></a> [history\_server\_image](#input\_history\_server\_image) | Image for spark-history-server-k8s | `map(string)` | n/a | yes |
| <a name="input_history_server_revision"></a> [history\_server\_revision](#input\_history\_server\_revision) | Charm revision for spark-history-server-k8s | `number` | n/a | yes |
| <a name="input_integration_hub_image"></a> [integration\_hub\_image](#input\_integration\_hub\_image) | Image for spark-integration-hub-k8s | `map(string)` | n/a | yes |
| <a name="input_integration_hub_monitored_service_accounts"></a> [integration\_hub\_monitored\_service\_accounts](#input\_integration\_hub\_monitored\_service\_accounts) | Comma-separated patterns for namespaces and service accounts to monitor and update | `string` | `null` | no |
| <a name="input_integration_hub_revision"></a> [integration\_hub\_revision](#input\_integration\_hub\_revision) | Charm revision for spark-integration-hub-k8s | `number` | n/a | yes |
| <a name="input_kyuubi_driver_pod_template"></a> [kyuubi\_driver\_pod\_template](#input\_kyuubi\_driver\_pod\_template) | Define K8s driver pod from a file accessible in the object storage. | `string` | `null` | no |
| <a name="input_kyuubi_executor_cores"></a> [kyuubi\_executor\_cores](#input\_kyuubi\_executor\_cores) | Set kyuubi executor pods cpu cores. | `number` | `null` | no |
| <a name="input_kyuubi_executor_memory"></a> [kyuubi\_executor\_memory](#input\_kyuubi\_executor\_memory) | Set kyuubi executor pods memory (in GB). | `number` | `null` | no |
| <a name="input_kyuubi_executor_pod_template"></a> [kyuubi\_executor\_pod\_template](#input\_kyuubi\_executor\_pod\_template) | Define K8s executor pod from a file accessible in the object storage. | `string` | `null` | no |
| <a name="input_kyuubi_gpu_enable"></a> [kyuubi\_gpu\_enable](#input\_kyuubi\_gpu\_enable) | Enable GPU acceleration for SparkSQLEngine. | `bool` | n/a | yes |
| <a name="input_kyuubi_gpu_engine_executors_limit"></a> [kyuubi\_gpu\_engine\_executors\_limit](#input\_kyuubi\_gpu\_engine\_executors\_limit) | Limit the number of GPUs an engine can schedule executor pods on. | `number` | n/a | yes |
| <a name="input_kyuubi_gpu_pinned_memory"></a> [kyuubi\_gpu\_pinned\_memory](#input\_kyuubi\_gpu\_pinned\_memory) | Set the host memory (in GB) per executor reserved for fast data transfer on GPUs. | `number` | n/a | yes |
| <a name="input_kyuubi_image"></a> [kyuubi\_image](#input\_kyuubi\_image) | Image for kyuubi-k8s | `map(string)` | n/a | yes |
| <a name="input_kyuubi_k8s_node_selectors"></a> [kyuubi\_k8s\_node\_selectors](#input\_kyuubi\_k8s\_node\_selectors) | Comma separated label:value selectors for K8s pods in Kyuubi. | `string` | `null` | no |
| <a name="input_kyuubi_loadbalancer_extra_annotations"></a> [kyuubi\_loadbalancer\_extra\_annotations](#input\_kyuubi\_loadbalancer\_extra\_annotations) | Optional extra annotations to be supplied to the load balancer service in Kyuubi. | `string` | `null` | no |
| <a name="input_kyuubi_profile"></a> [kyuubi\_profile](#input\_kyuubi\_profile) | The profile to be used for Kyuubi; should be one of 'testing', 'staging' and 'production'. | `string` | `"production"` | no |
| <a name="input_kyuubi_revision"></a> [kyuubi\_revision](#input\_kyuubi\_revision) | Charm revision for kyuubi-k8s | `number` | n/a | yes |
| <a name="input_kyuubi_units"></a> [kyuubi\_units](#input\_kyuubi\_units) | Number of Kyuubi units. 3 units are recommended for high availability. | `number` | `3` | no |
| <a name="input_kyuubi_user"></a> [kyuubi\_user](#input\_kyuubi\_user) | User name to be used for running Kyuubi engines. | `string` | `"kyuubi-spark-engine"` | no |
| <a name="input_kyuubi_users_image"></a> [kyuubi\_users\_image](#input\_kyuubi\_users\_image) | Image for postgresql-k8s (auth-db) | `map(string)` | n/a | yes |
| <a name="input_kyuubi_users_revision"></a> [kyuubi\_users\_revision](#input\_kyuubi\_users\_revision) | Charm revision for postgresql-k8s (auth-db) | `number` | n/a | yes |
| <a name="input_kyuubi_users_size"></a> [kyuubi\_users\_size](#input\_kyuubi\_users\_size) | Storage size for the Kyuubi users database | `string` | `"1G"` | no |
| <a name="input_metastore_image"></a> [metastore\_image](#input\_metastore\_image) | Image for postgresql-k8s (metastore) | `map(string)` | n/a | yes |
| <a name="input_metastore_revision"></a> [metastore\_revision](#input\_metastore\_revision) | Charm revision for postgresql-k8s (metastore) | `number` | n/a | yes |
| <a name="input_metastore_size"></a> [metastore\_size](#input\_metastore\_size) | Storage size for the metastore database | `string` | `"10G"` | no |
| <a name="input_model"></a> [model](#input\_model) | Name of the Juju Model to deploy to. | `string` | n/a | yes |
| <a name="input_tls_app_name"></a> [tls\_app\_name](#input\_tls\_app\_name) | Name of the application providing the `tls-certificates` interface. | `string` | n/a | yes |
| <a name="input_tls_certificates_endpoint"></a> [tls\_certificates\_endpoint](#input\_tls\_certificates\_endpoint) | Name of the endpoint providing the `tls-certificates` interface. | `string` | n/a | yes |
| <a name="input_tls_private_key"></a> [tls\_private\_key](#input\_tls\_private\_key) | The private key to be used for TLS certificates. | `string` | `null` | no |
| <a name="input_zookeeper_image"></a> [zookeeper\_image](#input\_zookeeper\_image) | Image for zookeeper-k8s | `map(string)` | n/a | yes |
| <a name="input_zookeeper_revision"></a> [zookeeper\_revision](#input\_zookeeper\_revision) | Charm revision for zookeeper-k8s | `number` | n/a | yes |
| <a name="input_zookeeper_size"></a> [zookeeper\_size](#input\_zookeeper\_size) | Storage size for the zookeeper unit | `string` | `"10G"` | no |
| <a name="input_zookeeper_units"></a> [zookeeper\_units](#input\_zookeeper\_units) | Number of zookeeper units. 3 units are recommended for high availability. | `number` | `3` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_charms"></a> [charms](#output\_charms) | The name of the charms which are part of the deployment. |
| <a name="output_components"></a> [components](#output\_components) | List of the deployed applications for this component module. |
| <a name="output_offers"></a> [offers](#output\_offers) | n/a |
