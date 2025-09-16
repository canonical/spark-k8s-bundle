# Spark bundle Terraform modules

These Terraform modules aim to facilitate the deployment of the Charmed Spark solution, using the using the [Terraform juju provider](https://github.com/juju/terraform-provider-juju/). For more information, refer to the provider [documentation](https://registry.terraform.io/providers/juju/juju/latest/docs).

The solution consists of the following modules:

- `spark`: main spark module with integration-hub, history-server, kyuubi
- `s3` and `azure-storage`: storage backend. Having one of them is necessary, and they are mutually exclusive
- `observabiliby`: parts of the observability stack to be deployed alongside spark (config, pushgateway, etc.)

> [!NOTE]
> The `s3` module itself doesn't act as an S3 object storage system. For the solution to be functional, the `s3-integrator` charm needs to point to an S3-like storage.
> The same applies to `azure-storage`.

## Requirements

This module requires a `juju` model to be available. Refer to the [usage section](#usage) below for more details.

## Usage

### Quick start

Here is what a minimal deployment could look like:

```hcl
resource "juju_model" "spark" {
  name = "spark"
}

module "ssc" {
  depends_on  = [juju_model.spark]
  source      = "git::https://github.com/canonical/self-signed-certificates-operator//terraform"
  model       = juju_model.spark.name
  channel     = "latest/stable"
  revision    = 163
  constraints = "arch=amd64"
  base        = "ubuntu@22.04"
  units       = 1
}

module "spark" {
  depends_on                = [juju_model.spark]
  source                    = "git::https://github.com/canonical/spark-k8s-bundle//releases/3.4/terraform/modules/spark"
  model                     = juju_model.spark.name
  tls_app_name              = module.ssc.app_name
  tls_certificates_endpoint = module.ssc.provides.certificates
}

module "azure" {
  depends_on   = [juju_model.spark]
  source       = "git::https://github.com/canonical/spark-k8s-bundle//releases/3.4/terraform/modules/azure-storage"
  model        = juju_model.spark.name
  spark_charms = module.spark.charms
  azure = {
    storage_account = "storage_account"
    storage_secret  = "storage_secret"
  }
}
```

### Inputs

| Module        | Name                         | Type        | Description                                                              |
| ------------- | ---------------------------- | ----------- | ------------------------------------------------------------------------ |
| azure-storage | `azure`                      | object      | Azure Object storage information (storage account, key, container, etc.) |
| azure-storage | `model`                      | string      | Name of the model to deploy to (same as spark).                          |
| azure-storage | `spark_charms`               | map(string) | Names of the Spark applications in the Spark Juju model.                 |
| observability | `config_repo`                | string      | COS configuration repo URL.                                              |
| observability | `config_grafana_path`        | string      | Grafana dashboard path from configuration repo root.                     |
| observability | `dashboards_offer`           | string      | URL of the `grafana_dashboards` interface offer.                         |
| observability | `metrics_offer`              | string      | URL of the `prometheus_remote_write` interface offer.                    |
| observability | `logging_offer`              | string      | URL of the `loki_push_api` interface offer.                              |
| observability | `spark_charms`               | map(string) | Names of the Spark applications in the Spark Juju model.                 |
| observability | `spark_model`                | string      | Name of the model to deploy to (same as spark).                          |
| s3            | `s3`                         | object      | S3 Bucket information (bucket name, path, etc.)                          |
| s3            | `model`                      | string      | Name of the model to deploy to (same as spark).                          |
| s3            | `spark_charms`               | map(string) | Names of the Spark applications in the Spark Juju model.                 |
| spark         | `model`                      | string      | Name of the model to deploy to.                                          |
| spark         | `kyuubi_user`                | string      | User name to be used for running Kyuubi engines.                         |
| spark         | `zookeeper_units`            | number      | Number of zookeeper units.                                               |
| spark         | `tls_app_name`               | string      | Name of the application providing the `tls-certificates` interface.      |
| spark         | `tls_certificates_endpoints` | string      | Name of the endpoint providing the `tls-certificates` interface.         |

### Outputs

All modules return a `charms` output, a map(string) of the charms deployed.

## Development

The features are split into multiples submodules, where each file has a dedicated role:

- `applications.tf` -> Speak for itself
- `integrations.tf` -> Same
- `resources.tf` -> Define juju models, secrets, cross model offers
  each module can also include `providers.tf`, `variables.tf` and `outputs.tf`. The latter is especially useful to pass values back to a different module.

We defined a dependency chain such as `azure-storage`, `observability` and `s3` depend on `spark`.
By depending on `spark`, they can use whatever output `spark` defines.\
This means that using this structure, a new optional module just takes care of defining its applications and their integrations with the existing resources, without any change needed from the existing modules.

## Versions

| Module        | Charm                        | Channel       | revision |
| ------------- | ---------------------------- |---------------|----------|
| azure         | azure-storage-integrator     | latest/edge   | 15       |
| observability | grafana-agent-k8s            | 1/stable      | 121      |
| observability | cos-configuration-k8s        | 1/stable      | 65       |
| observability | prometheus-pushgateway-k8s   | 1/stable      | 27       |
| observability | prometheus-scrape-config-k8s | 1/stable      | 67       |
| spark         | spark-history-server-k8s     | 3/stable      | 47       |
| spark         | spark-integration-hub-k8s    | 3/stable      | 67       |
| spark         | kyuubi-k8s                   | 3.4/stable    | 113      |
| spark         | postgresql-k8s               | 14/stable     | 495      |
| spark         | postgresql-k8s               | 14/stable     | 495      |
| spark         | zookeeper-k8s                | 3/stable      | 78       |
| spark         | data-integrator              | latest/stable | 179      |
| s3            | s3-integrator                | 1/stable      | 145      |

### Updating the version table

1. Make sure that you work from a clean slate (no `terraform.tfstate`)\
   `terraform plan -out "tfplan"`
2. Convert to json `terraform show -json "tfplan" > tfplan.json`
3. Run the following python script

```py
import json
import re
from typing import TypedDict


class Charm(TypedDict):
    name: str
    channel: str
    revision: int


with open("tfplan.json", "r") as f:
    plan = json.load(f)

root = plan["planned_values"]["root_module"]

charms_summary = []
for module in root["child_modules"]:
    if match := re.match(r"module\.(?P<name>\w+)\[?", module["address"]):
        name = match.group("name")
    else:
        name = module["address"]
    for resource in module["resources"]:
        if not resource["type"] == "juju_application":
            continue
        charm = Charm(resource["values"]["charm"][0])
        charms_summary.append([name, charm["name"], charm["channel"], charm["revision"]])


data = [["Module", "Charm", "Channel", "revision"]] + charms_summary
md_table = "\n".join(
    [
        "| " + " | ".join(map(str, row)) + " |"
        for row in [data[0], ["---"] * len(data[0])] + data[1:]
    ]
)
print(md_table)
```
