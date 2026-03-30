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
| [juju_application.cos_configuration](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.grafana_agent](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.pushgateway](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.scrape_config](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.cos_configuration_grafana_agent](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana_agent_grafana_dashboards](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana_agent_loki](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana_agent_prometheus](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.history_server_grafana_agent_dashboard](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.history_server_grafana_agent_logging](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.history_server_grafana_agent_metrics](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.integration_hub_grafana_agent_logging](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_grafana_agent_dashboards](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_grafana_agent_logging](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_grafana_agent_metrics](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.pushgateway_integration_hub](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.pushgateway_scrape_config](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.scrape_config_grafana_agent](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_model.spark](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/model) | data source |
| [juju_offer.grafana_dashboards](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/offer) | data source |
| [juju_offer.loki_logging](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/offer) | data source |
| [juju_offer.prometheus_receive_remote_write](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/offer) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_config_grafana_path"></a> [config\_grafana\_path](#input\_config\_grafana\_path) | Grafana dashboard path from configuration repo root. | `string` | `"releases/3.4/resources/grafana/"` | no |
| <a name="input_config_repo"></a> [config\_repo](#input\_config\_repo) | COS configuration repo URL. | `string` | `"https://github.com/canonical/spark-k8s-bundle"` | no |
| <a name="input_cos_configuration_revision"></a> [cos\_configuration\_revision](#input\_cos\_configuration\_revision) | Charm revision for cos-configuration-k8s | `number` | n/a | yes |
| <a name="input_dashboards_offer"></a> [dashboards\_offer](#input\_dashboards\_offer) | URL of the `grafana_dashboard` interface offer. | `string` | n/a | yes |
| <a name="input_grafana_agent_revision"></a> [grafana\_agent\_revision](#input\_grafana\_agent\_revision) | Charm revision for grafana-agent-k8s | `number` | n/a | yes |
| <a name="input_logging_offer"></a> [logging\_offer](#input\_logging\_offer) | URL of the `loki_push_api` interface offer. | `string` | n/a | yes |
| <a name="input_metrics_offer"></a> [metrics\_offer](#input\_metrics\_offer) | URL of the `prometheus_remote_write` interface offer. | `string` | n/a | yes |
| <a name="input_pushgateway_revision"></a> [pushgateway\_revision](#input\_pushgateway\_revision) | Charm revision for prometheus-pushgateway-k8s | `number` | n/a | yes |
| <a name="input_pushgateway_size"></a> [pushgateway\_size](#input\_pushgateway\_size) | Storage size for the pushgateway database | `string` | `"10G"` | no |
| <a name="input_scrape_config_revision"></a> [scrape\_config\_revision](#input\_scrape\_config\_revision) | Charm revision for prometheus-scrape-config-k8s | `number` | n/a | yes |
| <a name="input_spark_charms"></a> [spark\_charms](#input\_spark\_charms) | Names of the Spark applications in the Spark Juju model. | `map(string)` | n/a | yes |
| <a name="input_spark_model"></a> [spark\_model](#input\_spark\_model) | Name of the Spark Juju model. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_charms"></a> [charms](#output\_charms) | The name of the charms which are part of the deployment. |
| <a name="output_components"></a> [components](#output\_components) | List of the deployed applications for this component module. |
