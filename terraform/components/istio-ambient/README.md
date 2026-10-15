# Istio Ambient component Terraform module

The `istio-ambient` component deploys the Istio Beacon and Istio Ingress charms into an existing Juju model. Beacon connects applications in the model to the Istio service mesh, and Istio Ingress provides an ingress gateway for mesh traffic.

## Module reference

The module integrates the Istio Ingress certificate endpoint with a certificate provider. Its outputs expose deployed applications and the endpoints they provide and require.

### Inputs

- `model_uuid`: UUID of the Juju model where the Istio Ambient applications are deployed (required)
- `istio_beacon_k8s`: Configuration for the Istio Beacon application (optional)
- `istio_ingress_k8s`: Configuration for the Istio Ingress gateway (optional)
- `certificates`: Certificate provider integration, supplied as an in-model endpoint or cross-model offer (required)

### Outputs

- `components`: Map of the deployed Istio Ambient applications
- `provides`: Map of endpoints provided to other components
- `requires`: Map of endpoints required from other components

<!-- BEGIN_TF_DOCS -->
### Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.6 |
| <a name="requirement_juju"></a> [juju](#requirement\_juju) | >= 1.1.1 |

### Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_juju"></a> [juju](#provider\_juju) | >= 1.1.1 |

### Modules

| Name | Source | Version |
| ---- | ------ | ------- |
| <a name="module_istio_beacon_k8s"></a> [istio\_beacon\_k8s](#module\_istio\_beacon\_k8s) | git::https://github.com/canonical/istio-beacon-k8s-operator//terraform | rev63 |
| <a name="module_istio_ingress_k8s"></a> [istio\_ingress\_k8s](#module\_istio\_ingress\_k8s) | git::https://github.com/canonical/istio-ingress-k8s-operator//terraform | rev61 |

### Resources

| Name | Type |
| ---- | ---- |
| [juju_integration.istio_ingress_k8s_certificates](https://registry.terraform.io/providers/juju/juju/latest/docs/resources/integration) | resource |

### Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_certificates"></a> [certificates](#input\_certificates) | External integration for the certificate provider application. | <pre>object({<br/>    kind     = string<br/>    name     = optional(string, null)<br/>    endpoint = optional(string, null)<br/>    url      = optional(string, null)<br/>  })</pre> | n/a | yes |
| <a name="input_istio_beacon_k8s"></a> [istio\_beacon\_k8s](#input\_istio\_beacon\_k8s) | Configuration for istio-beacon-k8s application | <pre>object({<br/>    channel     = optional(string, "2/stable")<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>    constraints = optional(string)<br/>    config      = optional(map(string), {})<br/>  })</pre> | `{}` | no |
| <a name="input_istio_ingress_k8s"></a> [istio\_ingress\_k8s](#input\_istio\_ingress\_k8s) | Configuration for istio-ingress-k8s ingress gateway | <pre>object({<br/>    channel     = optional(string, "2/stable")<br/>    revision    = optional(number)<br/>    units       = optional(number, 1)<br/>    constraints = optional(string)<br/>    config      = optional(map(string), {})<br/>  })</pre> | `{}` | no |
| <a name="input_model_uuid"></a> [model\_uuid](#input\_model\_uuid) | UUID of the Juju model where Istio Ambient is deployed | `string` | n/a | yes |

### Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_components"></a> [components](#output\_components) | Map of the deployed Istio Ambient applications |
| <a name="output_provides"></a> [provides](#output\_provides) | Map of endpoints provided by this component to other components (outbound relations) |
| <a name="output_requires"></a> [requires](#output\_requires) | Map of endpoints required by this component from other components (inbound relations) |
<!-- END_TF_DOCS -->
