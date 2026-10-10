<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >= 1.1.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_juju"></a> [juju](#provider\_juju) | >= 1.1.1 |

## Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_istio_beacon_k8s"></a> [istio\_beacon\_k8s](#module\_istio\_beacon\_k8s) | git::https://github.com/canonical/istio-beacon-k8s-operator//terraform | 51b204dd50392809692263f6e973d81dd9fe200a |
| <a name="module_istio_ingress_k8s_m2m"></a> [istio\_ingress\_k8s\_m2m](#module\_istio\_ingress\_k8s\_m2m) | git::https://github.com/canonical/istio-ingress-k8s-operator//terraform | a9ef9646aea149a00a6a7620acaf483249714d04 |
| <a name="module_istio_ingress_k8s_ui"></a> [istio\_ingress\_k8s\_ui](#module\_istio\_ingress\_k8s\_ui) | git::https://github.com/canonical/istio-ingress-k8s-operator//terraform | a9ef9646aea149a00a6a7620acaf483249714d04 |

## Resources

| Name | Type |
| ---- | ---- |
| [juju_integration.istio_ingress_k8s_ui_config](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_istio_beacon_k8s"></a> [istio\_beacon\_k8s](#input\_istio\_beacon\_k8s) | Configuration for istio-beacon-k8s application | <pre>object({<br/>    channel     = optional(string, "2/stable")<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>    constraints = optional(string)<br/>    config      = optional(map(string), {})<br/>  })</pre> | `{}` | no |
| <a name="input_istio_ingress_config"></a> [istio\_ingress\_config](#input\_istio\_ingress\_config) | Control-plane ingress-config provider consumed by the UI gateway, from<br/>istio-k8s:istio-ingress-config (interface istio\_ingress\_config). Supports a<br/>same-model endpoint (kind = "endpoint") or a cross-model offer<br/>(kind = "offer"). When istio-k8s runs in the istio-system model this is the<br/>cross-model offer. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | `null` | no |
| <a name="input_istio_ingress_k8s"></a> [istio\_ingress\_k8s](#input\_istio\_ingress\_k8s) | Common configuration for both istio-ingress-k8s gateways (UI and M2M) | <pre>object({<br/>    channel     = optional(string, "2/stable")<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>    constraints = optional(string)<br/>    config      = optional(map(string), {})<br/>  })</pre> | `{}` | no |
| <a name="input_istio_ingress_k8s_m2m_config"></a> [istio\_ingress\_k8s\_m2m\_config](#input\_istio\_ingress\_k8s\_m2m\_config) | Extra configuration for the M2M gateway (merged over istio\_ingress\_k8s.config) | `map(string)` | `{}` | no |
| <a name="input_istio_ingress_k8s_ui_config"></a> [istio\_ingress\_k8s\_ui\_config](#input\_istio\_ingress\_k8s\_ui\_config) | Extra configuration for the UI gateway (merged over istio\_ingress\_k8s.config) | `map(string)` | `{}` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | UUID of the Juju model where Istio Ambient is deployed | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_components"></a> [components](#output\_components) | Map of the deployed Istio Ambient applications |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of endpoints provided by this component to other components (outbound relations) |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of endpoints required by this component from other components (inbound relations) |
<!-- END_TF_DOCS -->
