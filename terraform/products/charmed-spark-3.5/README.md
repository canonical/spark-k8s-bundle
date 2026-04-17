# Charmed Apache Spark (3.5) product terraform module

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
| <a name="provider_juju"></a> [juju](#provider\_juju) | 1.3.1 |
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |

### Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_azure_storage"></a> [azure\_storage](#module\_azure\_storage) | ../../charms/azure-storage-integrator | n/a |
| <a name="module_data_integrator"></a> [data\_integrator](#module\_data\_integrator) | ../../charms/data-integrator | n/a |
| <a name="module_kyuubi_users"></a> [kyuubi\_users](#module\_kyuubi\_users) | git::https://github.com/canonical/postgresql-k8s-operator//terraform | rev774 |
| <a name="module_metastore"></a> [metastore](#module\_metastore) | git::https://github.com/canonical/postgresql-k8s-operator//terraform | rev774 |
| <a name="module_observability"></a> [observability](#module\_observability) | ../../components/observability | n/a |
| <a name="module_s3"></a> [s3](#module\_s3) | ../../charms/s3-integrator-v1 | n/a |
| <a name="module_spark"></a> [spark](#module\_spark) | ../../components/spark | n/a |
| <a name="module_ssc"></a> [ssc](#module\_ssc) | git::https://github.com/canonical/self-signed-certificates-operator//terraform | rev586 |
| <a name="module_zookeeper"></a> [zookeeper](#module\_zookeeper) | ../../charms/zookeeper | n/a |

### Resources

| Name | Type |
|------|------|
| [juju_access_secret.azure_storage_secret_access](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/access_secret) | resource |
| [juju_access_secret.system_users_and_private_key_secret_access](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/access_secret) | resource |
| [juju_model.spark](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/model) | resource |
| [juju_secret.azure_storage_secret](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/secret) | resource |
| [juju_secret.system_users_and_private_key_secret](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/secret) | resource |
| [terraform_data.deployed_at](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |

### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_K8S_CLOUD"></a> [K8S\_CLOUD](#input\_K8S\_CLOUD) | The kubernetes juju cloud name. | `string` | `"microk8s"` | no |
| <a name="input_K8S_CREDENTIAL"></a> [K8S\_CREDENTIAL](#input\_K8S\_CREDENTIAL) | The name of the kubernetes juju credential. | `string` | `"microk8s"` | no |
| <a name="input_admin_password"></a> [admin\_password](#input\_admin\_password) | The password for the Kyuubi admin user. | `string` | `null` | no |
| <a name="input_azure_storage_config"></a> [azure\_storage\_config](#input\_azure\_storage\_config) | Azure Object storage information | <pre>object({<br/>    container       = optional(string)<br/>    credentials     = optional(string)<br/>    path            = optional(string)<br/>    protocol        = optional(string, "abfss")<br/>    storage-account = optional(string)<br/>  })</pre> | `{}` | no |
| <a name="input_azure_storage_revision"></a> [azure\_storage\_revision](#input\_azure\_storage\_revision) | Charm revision for azure-storage-integrator | `number` | `null` | no |
| <a name="input_azure_storage_secret_key"></a> [azure\_storage\_secret\_key](#input\_azure\_storage\_secret\_key) | Secret key to the Azure Storage account. | `string` | `null` | no |
| <a name="input_certificate_common_name"></a> [certificate\_common\_name](#input\_certificate\_common\_name) | Common name for the certificate to be used in self-signed | `string` | `"charmed-spark"` | no |
| <a name="input_cos_offers"></a> [cos\_offers](#input\_cos\_offers) | Observability stack offers. | <pre>object({<br/>    dashboard = string<br/>    logging   = string<br/>    metrics   = string<br/>  })</pre> | `null` | no |
| <a name="input_create_model"></a> [create\_model](#input\_create\_model) | Should terraform create the Juju models? If set to false, assume the models are created by a different mechanism. | `bool` | `true` | no |
| <a name="input_data_integrator_revision"></a> [data\_integrator\_revision](#input\_data\_integrator\_revision) | Charm revision for data-integrator | `number` | `null` | no |
| <a name="input_grafana_agent_revision"></a> [grafana\_agent\_revision](#input\_grafana\_agent\_revision) | Charm revision for grafana-agent-k8s | `number` | `null` | no |
| <a name="input_history_server_config"></a> [history\_server\_config](#input\_history\_server\_config) | History Server configuration options | `map(any)` | `{}` | no |
| <a name="input_history_server_image"></a> [history\_server\_image](#input\_history\_server\_image) | Image for spark-history-server-k8s | `string` | `null` | no |
| <a name="input_history_server_revision"></a> [history\_server\_revision](#input\_history\_server\_revision) | Charm revision for spark-history-server-k8s | `number` | `null` | no |
| <a name="input_integration_hub_config"></a> [integration\_hub\_config](#input\_integration\_hub\_config) | Integration Hub configuration options. | `map(any)` | `{}` | no |
| <a name="input_integration_hub_image"></a> [integration\_hub\_image](#input\_integration\_hub\_image) | Image for spark-integration-hub-k8s | `string` | `null` | no |
| <a name="input_integration_hub_revision"></a> [integration\_hub\_revision](#input\_integration\_hub\_revision) | Charm revision for spark-integration-hub-k8s | `number` | `null` | no |
| <a name="input_juju_controller"></a> [juju\_controller](#input\_juju\_controller) | Controller information: endpoint, username, password and CA certificate. | <pre>object({<br/>    endpoint = optional(string)<br/>    username = optional(string)<br/>    password = optional(string)<br/>    ca       = optional(string)<br/>  })</pre> | `{}` | no |
| <a name="input_kyuubi_config"></a> [kyuubi\_config](#input\_kyuubi\_config) | Kyuubi configuration options. | `map(any)` | `{}` | no |
| <a name="input_kyuubi_image"></a> [kyuubi\_image](#input\_kyuubi\_image) | Image for kyuubi-k8s | `string` | `null` | no |
| <a name="input_kyuubi_revision"></a> [kyuubi\_revision](#input\_kyuubi\_revision) | Charm revision for kyuubi-k8s | `number` | `null` | no |
| <a name="input_kyuubi_units"></a> [kyuubi\_units](#input\_kyuubi\_units) | Number of Kyuubi units. 3 units are recommended for high availability. | `number` | `3` | no |
| <a name="input_kyuubi_users_image"></a> [kyuubi\_users\_image](#input\_kyuubi\_users\_image) | Image for postgresql-k8s (auth-db) | `string` | `null` | no |
| <a name="input_kyuubi_users_revision"></a> [kyuubi\_users\_revision](#input\_kyuubi\_users\_revision) | Charm revision for postgresql-k8s (auth-db) | `number` | `null` | no |
| <a name="input_kyuubi_users_size"></a> [kyuubi\_users\_size](#input\_kyuubi\_users\_size) | Storage size for the Kyuubi users database | `string` | `"1G"` | no |
| <a name="input_logging_config"></a> [logging\_config](#input\_logging\_config) | Logging configuration to be used | `string` | `"<root>=INFO"` | no |
| <a name="input_metastore_image"></a> [metastore\_image](#input\_metastore\_image) | Image for postgresql-k8s (metastore) | `string` | `null` | no |
| <a name="input_metastore_revision"></a> [metastore\_revision](#input\_metastore\_revision) | Charm revision for postgresql-k8s (metastore) | `number` | `null` | no |
| <a name="input_metastore_size"></a> [metastore\_size](#input\_metastore\_size) | Storage size for the metastore database | `string` | `"10G"` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Optional existing Juju model UUID to deploy Spark to. If provided, model creation is skipped in higher-level modules. | `string` | `null` | no |
| <a name="input_proxy"></a> [proxy](#input\_proxy) | Proxy information for the deployment. | <pre>object({<br/>    http     = optional(string, "")<br/>    https    = optional(string, "")<br/>    no-proxy = optional(string, "")<br/>  })</pre> | `{}` | no |
| <a name="input_s3_config"></a> [s3\_config](#input\_s3\_config) | S3 integrator configuration | <pre>object({<br/>    attributes                          = optional(string)<br/>    bucket                              = optional(string)<br/>    endpoint                            = optional(string)<br/>    experimental-delete-older-than-days = optional(number)<br/>    path                                = optional(string)<br/>    region                              = optional(string)<br/>    s3-api-version                      = optional(string)<br/>    s3-uri-style                        = optional(string)<br/>    storage-class                       = optional(string)<br/>    tls-ca-chain                        = optional(string)<br/>  })</pre> | `{}` | no |
| <a name="input_s3_revision"></a> [s3\_revision](#input\_s3\_revision) | Charm revision for s3-integrator | `number` | `null` | no |
| <a name="input_spark_model_name"></a> [spark\_model\_name](#input\_spark\_model\_name) | The name of the juju model to deploy Spark to | `string` | `"spark"` | no |
| <a name="input_storage_backend"></a> [storage\_backend](#input\_storage\_backend) | Storage backend to be used | `string` | `"s3"` | no |
| <a name="input_tls_private_key"></a> [tls\_private\_key](#input\_tls\_private\_key) | The file path of the private key to use for TLS certificates. | `string` | `null` | no |
| <a name="input_zookeeper_image"></a> [zookeeper\_image](#input\_zookeeper\_image) | Image for zookeeper-k8s | `map(string)` | `null` | no |
| <a name="input_zookeeper_revision"></a> [zookeeper\_revision](#input\_zookeeper\_revision) | Charm revision for zookeeper-k8s | `number` | `null` | no |
| <a name="input_zookeeper_size"></a> [zookeeper\_size](#input\_zookeeper\_size) | Storage size for the metastore database | `string` | `"10G"` | no |
| <a name="input_zookeeper_units"></a> [zookeeper\_units](#input\_zookeeper\_units) | Define the number of zookeeper units. 3 units are recommended for high availability. | `number` | `3` | no |

### Outputs

| Name | Description |
|------|-------------|
| <a name="output_metadata"></a> [metadata](#output\_metadata) | Metadata of the product deployment. |
| <a name="output_models"></a> [models](#output\_models) | Map of the key of the model and the components deployed in the model. |
| <a name="output_offers"></a> [offers](#output\_offers) | The name and url of the various offers being exposed |
<!-- END_TF_DOCS -->
