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

| Name | Source | Version |
|------|--------|---------|
| <a name="module_azure_storage"></a> [azure\_storage](#module\_azure\_storage) | ../../charms/azure-storage-integrator | n/a |
| <a name="module_data_integrator"></a> [data\_integrator](#module\_data\_integrator) | ../../charms/data-integrator | n/a |
| <a name="module_kyuubi_users"></a> [kyuubi\_users](#module\_kyuubi\_users) | git::https://github.com/canonical/postgresql-k8s-operator//terraform | rev774 |
| <a name="module_metastore"></a> [metastore](#module\_metastore) | git::https://github.com/canonical/postgresql-k8s-operator//terraform | rev774 |
| <a name="module_s3"></a> [s3](#module\_s3) | ../../charms/s3-integrator-v1 | n/a |
| <a name="module_spark"></a> [spark](#module\_spark) | ../../components/spark-3.4 | n/a |
| <a name="module_ssc"></a> [ssc](#module\_ssc) | git::https://github.com/canonical/self-signed-certificates-operator//terraform | rev586 |
| <a name="module_zookeeper"></a> [zookeeper](#module\_zookeeper) | ../../charms/zookeeper | n/a |

## Resources

| Name | Type |
|------|------|
| [juju_model.spark](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/model) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_K8S_CLOUD"></a> [K8S\_CLOUD](#input\_K8S\_CLOUD) | The kubernetes juju cloud name. | `string` | `"microk8s"` | no |
| <a name="input_K8S_CREDENTIAL"></a> [K8S\_CREDENTIAL](#input\_K8S\_CREDENTIAL) | The name of the kubernetes juju credential. | `string` | `"microk8s"` | no |
| <a name="input_admin_password"></a> [admin\_password](#input\_admin\_password) | The password for the admin user. | `string` | `null` | no |
| <a name="input_alertmanager_size"></a> [alertmanager\_size](#input\_alertmanager\_size) | Storage size for the alertmanager database | `string` | `"10G"` | no |
| <a name="input_azure_storage"></a> [azure\_storage](#input\_azure\_storage) | Azure Object storage information | <pre>object({<br/>    container       = optional(string, "azurecontainer")<br/>    storage_account = optional(string, "azurestorageaccount")<br/>    secret_key      = optional(string, "azurestoragesecret")<br/>    protocol        = optional(string, "abfss")<br/>  })</pre> | `{}` | no |
| <a name="input_azure_storage_revision"></a> [azure\_storage\_revision](#input\_azure\_storage\_revision) | Charm revision for azure-storage-integrator | `number` | `null` | no |
| <a name="input_certificate_common_name"></a> [certificate\_common\_name](#input\_certificate\_common\_name) | Common name for the certificate to be used in self-signed | `string` | `"charmed-spark"` | no |
| <a name="input_cos"></a> [cos](#input\_cos) | Observability settings | <pre>object({<br/>    model    = optional(string, "cos")<br/>    deployed = optional(string, "bundled")<br/>    offers = optional(object({<br/>      dashboard = optional(string, null),<br/>      metrics   = optional(string, null),<br/>      logging   = optional(string, null)<br/>    }), {}),<br/>    tls = optional(object({<br/>      cert = optional(string, "")<br/>      key  = optional(string, "")<br/>      ca   = optional(string, "")<br/>    }), {})<br/>  })</pre> | <pre>{<br/>  "deployed": "bundled",<br/>  "model": "cos",<br/>  "offers": {},<br/>  "tls": {}<br/>}</pre> | no |
| <a name="input_cos_configuration_revision"></a> [cos\_configuration\_revision](#input\_cos\_configuration\_revision) | Charm revision for cos-configuration-k8s | `number` | `null` | no |
| <a name="input_create_model"></a> [create\_model](#input\_create\_model) | Should terraform create the Juju models? If set to false, assume the models are created by a different mechanism. | `bool` | `true` | no |
| <a name="input_data_integrator_revision"></a> [data\_integrator\_revision](#input\_data\_integrator\_revision) | Charm revision for data-integrator | `number` | `null` | no |
| <a name="input_driver_pod_template"></a> [driver\_pod\_template](#input\_driver\_pod\_template) | Define K8s driver pod from a file accessible to the `spark-submit` process. | `string` | `null` | no |
| <a name="input_enable_dynamic_allocation"></a> [enable\_dynamic\_allocation](#input\_enable\_dynamic\_allocation) | Enable dynamic allocation of pods for Spark jobs. | `bool` | `false` | no |
| <a name="input_executor_pod_template"></a> [executor\_pod\_template](#input\_executor\_pod\_template) | Define K8s executor pod from a file accessible to the `spark-submit` process. | `string` | `null` | no |
| <a name="input_grafana_agent_revision"></a> [grafana\_agent\_revision](#input\_grafana\_agent\_revision) | Charm revision for grafana-agent-k8s | `number` | `null` | no |
| <a name="input_grafana_size"></a> [grafana\_size](#input\_grafana\_size) | Storage size for the grafana database | `string` | `"10G"` | no |
| <a name="input_history_server_image"></a> [history\_server\_image](#input\_history\_server\_image) | Image for spark-history-server-k8s | `map(string)` | `null` | no |
| <a name="input_history_server_revision"></a> [history\_server\_revision](#input\_history\_server\_revision) | Charm revision for spark-history-server-k8s | `number` | `null` | no |
| <a name="input_integration_hub_image"></a> [integration\_hub\_image](#input\_integration\_hub\_image) | Image for spark-integration-hub-k8s | `map(string)` | `null` | no |
| <a name="input_integration_hub_monitored_service_accounts"></a> [integration\_hub\_monitored\_service\_accounts](#input\_integration\_hub\_monitored\_service\_accounts) | Comma-separated patterns for namespaces and service accounts to monitor and update | `string` | `null` | no |
| <a name="input_integration_hub_revision"></a> [integration\_hub\_revision](#input\_integration\_hub\_revision) | Charm revision for spark-integration-hub-k8s | `number` | `null` | no |
| <a name="input_juju_controller"></a> [juju\_controller](#input\_juju\_controller) | Controller information: endpoint, username, password and CA certificate. | <pre>object({<br/>    endpoint = string<br/>    username = string<br/>    password = string<br/>    ca       = string<br/>  })</pre> | `null` | no |
| <a name="input_kyuubi_driver_pod_template"></a> [kyuubi\_driver\_pod\_template](#input\_kyuubi\_driver\_pod\_template) | Define K8s driver pod from a file accessible in the object storage. | `string` | `null` | no |
| <a name="input_kyuubi_executor_cores"></a> [kyuubi\_executor\_cores](#input\_kyuubi\_executor\_cores) | Set kyuubi executor pods cpu cores. | `number` | `null` | no |
| <a name="input_kyuubi_executor_memory"></a> [kyuubi\_executor\_memory](#input\_kyuubi\_executor\_memory) | Set kyuubi executor pods memory (in GB). | `number` | `null` | no |
| <a name="input_kyuubi_executor_pod_template"></a> [kyuubi\_executor\_pod\_template](#input\_kyuubi\_executor\_pod\_template) | Define K8s executor pod from a file accessible in the object storage. | `string` | `null` | no |
| <a name="input_kyuubi_gpu_enable"></a> [kyuubi\_gpu\_enable](#input\_kyuubi\_gpu\_enable) | Enable GPU acceleration for SparkSQLEngine. | `bool` | `false` | no |
| <a name="input_kyuubi_gpu_engine_executors_limit"></a> [kyuubi\_gpu\_engine\_executors\_limit](#input\_kyuubi\_gpu\_engine\_executors\_limit) | Limit the number of GPUs an engine can schedule executor pods on. | `number` | `1` | no |
| <a name="input_kyuubi_gpu_pinned_memory"></a> [kyuubi\_gpu\_pinned\_memory](#input\_kyuubi\_gpu\_pinned\_memory) | Set the host memory (in GB) per executor reserved for fast data transfer on GPUs. | `number` | `1` | no |
| <a name="input_kyuubi_image"></a> [kyuubi\_image](#input\_kyuubi\_image) | Image for kyuubi-k8s | `map(string)` | `null` | no |
| <a name="input_kyuubi_k8s_node_selectors"></a> [kyuubi\_k8s\_node\_selectors](#input\_kyuubi\_k8s\_node\_selectors) | Comma separated label:value selectors for K8s pods in Kyuubi. | `string` | `null` | no |
| <a name="input_kyuubi_loadbalancer_extra_annotations"></a> [kyuubi\_loadbalancer\_extra\_annotations](#input\_kyuubi\_loadbalancer\_extra\_annotations) | Optional extra annotations to be supplied to the load balancer service in Kyuubi. | `string` | `null` | no |
| <a name="input_kyuubi_profile"></a> [kyuubi\_profile](#input\_kyuubi\_profile) | The profile to be used for Kyuubi; should be one of 'testing', 'staging' and 'production'. | `string` | `"production"` | no |
| <a name="input_kyuubi_revision"></a> [kyuubi\_revision](#input\_kyuubi\_revision) | Charm revision for kyuubi-k8s | `number` | `null` | no |
| <a name="input_kyuubi_units"></a> [kyuubi\_units](#input\_kyuubi\_units) | Number of Kyuubi units. 3 units are recommended for high availability. | `number` | `3` | no |
| <a name="input_kyuubi_user"></a> [kyuubi\_user](#input\_kyuubi\_user) | Define the user to be used for running Kyuubi enginers | `string` | `"kyuubi-spark-engine"` | no |
| <a name="input_kyuubi_users_image"></a> [kyuubi\_users\_image](#input\_kyuubi\_users\_image) | Image for postgresql-k8s (auth-db) | `map(string)` | `null` | no |
| <a name="input_kyuubi_users_revision"></a> [kyuubi\_users\_revision](#input\_kyuubi\_users\_revision) | Charm revision for postgresql-k8s (auth-db) | `number` | `null` | no |
| <a name="input_kyuubi_users_size"></a> [kyuubi\_users\_size](#input\_kyuubi\_users\_size) | Storage size for the Kyuubi users database | `string` | `"1G"` | no |
| <a name="input_logging_config"></a> [logging\_config](#input\_logging\_config) | Logging configuration to be used. | `string` | `""` | no |
| <a name="input_loki_active_index_directory_size"></a> [loki\_active\_index\_directory\_size](#input\_loki\_active\_index\_directory\_size) | Storage size for the active index directory for Loki | `string` | `"10G"` | no |
| <a name="input_loki_chunks_size"></a> [loki\_chunks\_size](#input\_loki\_chunks\_size) | Storage size for the Loki chucks storage | `string` | `"500G"` | no |
| <a name="input_metastore_image"></a> [metastore\_image](#input\_metastore\_image) | Image for postgresql-k8s (metastore) | `map(string)` | `null` | no |
| <a name="input_metastore_revision"></a> [metastore\_revision](#input\_metastore\_revision) | Charm revision for postgresql-k8s (metastore) | `number` | `null` | no |
| <a name="input_metastore_size"></a> [metastore\_size](#input\_metastore\_size) | Storage size for the metastore database | `string` | `"10G"` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Optional existing Juju model UUID to deploy Spark to. If provided, model creation is skipped in higher-level modules. | `string` | `null` | no |
| <a name="input_prometheus_size"></a> [prometheus\_size](#input\_prometheus\_size) | Storage size for the Prometheus database | `string` | `"500G"` | no |
| <a name="input_proxy"></a> [proxy](#input\_proxy) | Proxy information for the deployment. | <pre>object({<br/>    http     = optional(string, "")<br/>    https    = optional(string, "")<br/>    no_proxy = optional(string, "")<br/>  })</pre> | `{}` | no |
| <a name="input_pushgateway_revision"></a> [pushgateway\_revision](#input\_pushgateway\_revision) | Charm revision for prometheus-pushgateway-k8s | `number` | `null` | no |
| <a name="input_s3"></a> [s3](#input\_s3) | S3 Bucket information | <pre>object({<br/>    bucket   = optional(string, "spark-test")<br/>    endpoint = optional(string, "https://s3.amazonaws.com")<br/>    region   = optional(string, "us-east-1")<br/>  })</pre> | `{}` | no |
| <a name="input_s3_revision"></a> [s3\_revision](#input\_s3\_revision) | Charm revision for s3-integrator | `number` | `null` | no |
| <a name="input_scrape_config_revision"></a> [scrape\_config\_revision](#input\_scrape\_config\_revision) | Charm revision for prometheus-scrape-config-k8s | `number` | `null` | no |
| <a name="input_spark_model_name"></a> [spark\_model\_name](#input\_spark\_model\_name) | The name of the juju model to deploy Spark to | `string` | `"spark-test"` | no |
| <a name="input_storage_backend"></a> [storage\_backend](#input\_storage\_backend) | Storage backend to be used | `string` | `"s3"` | no |
| <a name="input_tls_private_key"></a> [tls\_private\_key](#input\_tls\_private\_key) | The file path of the private key to use for TLS certificates. | `string` | `null` | no |
| <a name="input_traefik_size"></a> [traefik\_size](#input\_traefik\_size) | Storage size for the Traefik storage | `string` | `"10G"` | no |
| <a name="input_zookeeper_image"></a> [zookeeper\_image](#input\_zookeeper\_image) | Image for zookeeper-k8s | `map(string)` | `null` | no |
| <a name="input_zookeeper_revision"></a> [zookeeper\_revision](#input\_zookeeper\_revision) | Charm revision for zookeeper-k8s | `number` | `null` | no |
| <a name="input_zookeeper_size"></a> [zookeeper\_size](#input\_zookeeper\_size) | Storage size for the metastore database | `string` | `"10G"` | no |
| <a name="input_zookeeper_units"></a> [zookeeper\_units](#input\_zookeeper\_units) | Define the number of zookeeper units. 3 units are recommended for high availability. | `number` | `3` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_metadata"></a> [metadata](#output\_metadata) | Metadata of the product deployment. |
| <a name="output_models"></a> [models](#output\_models) | Maps of the models and the components deployed in each model. |
| <a name="output_offers"></a> [offers](#output\_offers) | The name and url of the various offers being exposed |
