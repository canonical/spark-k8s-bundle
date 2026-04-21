# Observability component terraform module

Bundles the following charms:
- Grafana-agent
- COS-configuration
- Prometheus Pushgateway
- Prometheus-scrape-config

While we do not maintain those charms, we have specific requirements for them.
As such, it is easier to define our own component module for now.

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

### Modules

No modules.

### Resources

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
| [juju_integration.integration_hub_pushgateway](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_grafana_agent_dashboards](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_grafana_agent_logging](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.kyuubi_grafana_agent_metrics](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.pushgateway_scrape_config](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_integration.scrape_config_grafana_agent](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |
| [juju_offer.grafana_dashboards](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/offer) | data source |
| [juju_offer.loki_logging](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/offer) | data source |
| [juju_offer.prometheus_receive_remote_write](https://registry.terraform.io/providers/juju/juju/latest/docs/data-sources/offer) | data source |

### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_cos_configuration"></a> [cos\_configuration](#input\_cos\_configuration) | n/a | <pre>object({<br/>    app_name = optional(string, "cos-configuration")<br/>    base     = optional(string, "ubuntu@22.04")<br/>    channel  = optional(string, "1/stable")<br/>    config = optional(map(string), {<br/>      git_branch              = "main"<br/>      git_depth               = 1<br/>      git_repo                = "https://github.com/canonical/spark-k8s-bundle"<br/>      grafana_dashboards_path = "resources/grafana/"<br/>    })<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number, 65) # TODO<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_dashboards_offer"></a> [dashboards\_offer](#input\_dashboards\_offer) | URL of the `grafana_dashboard` interface offer. | `string` | n/a | yes |
| <a name="input_grafana_agent"></a> [grafana\_agent](#input\_grafana\_agent) | n/a | <pre>object({<br/>    app_name    = optional(string, "grafana-agent")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    channel     = optional(string, "1/stable")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_history_server_dashboard_endpoint"></a> [history\_server\_dashboard\_endpoint](#input\_history\_server\_dashboard\_endpoint) | In-model endpoint for the History Server dashboard integration. | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_history_server_logging_endpoint"></a> [history\_server\_logging\_endpoint](#input\_history\_server\_logging\_endpoint) | In-model endpoint for the History Server logging integration. | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_history_server_metrics_endpoint"></a> [history\_server\_metrics\_endpoint](#input\_history\_server\_metrics\_endpoint) | In-model endpoint for the History Server metrics integration. | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_integration_hub_cos_endpoint"></a> [integration\_hub\_cos\_endpoint](#input\_integration\_hub\_cos\_endpoint) | In-model endpoint for the Integration Hub COS integration. | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_integration_hub_logging_endpoint"></a> [integration\_hub\_logging\_endpoint](#input\_integration\_hub\_logging\_endpoint) | In-model endpoint for the Integration Hub logging integration. | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_kyuubi_dashboard_endpoint"></a> [kyuubi\_dashboard\_endpoint](#input\_kyuubi\_dashboard\_endpoint) | In-model endpoint for the Kyuubi dashboard integration. | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_kyuubi_logging_endpoint"></a> [kyuubi\_logging\_endpoint](#input\_kyuubi\_logging\_endpoint) | In-model endpoint for the Kyuubi logging integration. | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_kyuubi_metrics_endpoint"></a> [kyuubi\_metrics\_endpoint](#input\_kyuubi\_metrics\_endpoint) | In-model endpoint for the Kyuubi metrics integration. | <pre>object({<br/>    name     = string<br/>    endpoint = string<br/>  })</pre> | n/a | yes |
| <a name="input_logging_offer"></a> [logging\_offer](#input\_logging\_offer) | URL of the `loki_push_api` interface offer. | `string` | n/a | yes |
| <a name="input_metrics_offer"></a> [metrics\_offer](#input\_metrics\_offer) | URL of the `prometheus_remote_write` interface offer. | `string` | n/a | yes |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | Reference to an existing model uuid. | `string` | n/a | yes |
| <a name="input_pushgateway"></a> [pushgateway](#input\_pushgateway) | n/a | <pre>object({<br/>    app_name    = optional(string, "pushgateway")<br/>    base        = optional(string, "ubuntu@22.04")<br/>    channel     = optional(string, "1/stable")<br/>    config      = optional(map(string), {})<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    storage_directives = optional(map(string), {<br/>      pushgateway-store = "10G"<br/>    })<br/>    units = optional(number, 1)<br/>  })</pre> | `{}` | no |
| <a name="input_scrape_config"></a> [scrape\_config](#input\_scrape\_config) | n/a | <pre>object({<br/>    app_name = optional(string, "scrape-config")<br/>    base     = optional(string, "ubuntu@22.04")<br/>    channel  = optional(string, "1/stable")<br/>    config = optional(map(string), {<br/>      scrape_interval = "10s"<br/>    })<br/>    constraints = optional(string, "arch=amd64")<br/>    resources   = optional(map(string), {})<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>  })</pre> | `{}` | no |

### Outputs

| Name | Description |
|------|-------------|
| <a name="output_components"></a> [components](#output\_components) | List of the deployed applications for this component module. |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of all the provided endpoints. |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of the required endpoints. |
<!-- END_TF_DOCS -->
