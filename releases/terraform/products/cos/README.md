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
| [juju_application.alertmanager](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.catalogue](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.grafana](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.loki](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.prometheus](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_application.traefik](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/application) | resource |
| [juju_integration.catalogue-alertmanager](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.catalogue-grafana](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.catalogue-prometheus](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.catalogue-traefik](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana-alertmanager-dashboard](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana-alertmanager-source](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana-loki-dashboard](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana-loki-source](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana-prometheus-dashboard](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.grafana-prometheus-source](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.loki-alertmanager](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.prometheus-alertmanager-alerting](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.prometheus-alertmanager-metrics](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.prometheus-grafana](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.prometheus-loki](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.prometheus-traefik](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.traefik-alertmanager](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.traefik-grafana](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.traefik-loki](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.traefik-prometheus](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_offer.grafana_dashboards](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_offer.loki_logging](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_offer.prometheus_receive_remote_write](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/offer) | resource |
| [juju_model.cos](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/model) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_alertmanager_size"></a> [alertmanager\_size](#input\_alertmanager\_size) | Storage size for the alertmanager database | `string` | `"10G"` | no |
| <a name="input_cos_tls_ca"></a> [cos\_tls\_ca](#input\_cos\_tls\_ca) | COS CA certificate | `string` | `""` | no |
| <a name="input_cos_tls_cert"></a> [cos\_tls\_cert](#input\_cos\_tls\_cert) | COS certificate | `string` | `""` | no |
| <a name="input_cos_tls_key"></a> [cos\_tls\_key](#input\_cos\_tls\_key) | COS certificate key | `string` | `""` | no |
| <a name="input_cos_user"></a> [cos\_user](#input\_cos\_user) | The name of the Juju user of the COS deployment. | `string` | `"admin"` | no |
| <a name="input_grafana_size"></a> [grafana\_size](#input\_grafana\_size) | Storage size for the grafana database | `string` | `"10G"` | no |
| <a name="input_loki_active_index_directory_size"></a> [loki\_active\_index\_directory\_size](#input\_loki\_active\_index\_directory\_size) | Storage size for the active index directory for Loki | `string` | `"10G"` | no |
| <a name="input_loki_chunks_size"></a> [loki\_chunks\_size](#input\_loki\_chunks\_size) | Storage size for the Loki chucks storage | `string` | `"500G"` | no |
| <a name="input_model"></a> [model](#input\_model) | The name of the Juju model to deploy to | `string` | n/a | yes |
| <a name="input_prometheus_size"></a> [prometheus\_size](#input\_prometheus\_size) | Storage size for the Prometheus database | `string` | `"500G"` | no |
| <a name="input_traefik_size"></a> [traefik\_size](#input\_traefik\_size) | Storage size for the Traefik storage | `string` | `"10G"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_charms"></a> [charms](#output\_charms) | The name of the charms which are part of the deployment. |
| <a name="output_dashboards_offer"></a> [dashboards\_offer](#output\_dashboards\_offer) | n/a |
| <a name="output_logging_offer"></a> [logging\_offer](#output\_logging\_offer) | n/a |
| <a name="output_metrics_offer"></a> [metrics\_offer](#output\_metrics\_offer) | n/a |
| <a name="output_user"></a> [user](#output\_user) | The name of the Juju user of the COS deployment. |
