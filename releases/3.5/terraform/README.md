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

## Top-level inputs

| Variable                              | Description                                                                     | Type   | Nullable | Default             |
| ------------------------------------- | ------------------------------------------------------------------------------- | ------ | -------- | ------------------- |
| K8S_CLOUD                             | The kubernetes juju cloud name.                                                 | string | True     | microk8s            |
| K8S_CREDENTIAL                        | The name of the kubernetes juju credential.                                     | string | True     | microk8s            |
| model                                 | The name of the juju model to deploy Spark to                                   | string | True     | spark               |
| create_model                          | Should terraform create the Juju models? If set to false, assume the [...]      | bool   | False    | True                |
| cos                                   | Observability settings                                                          | map    | True     | See variables.tf    |
| storage_backend                       | Storage backend to be used                                                      | string | True     | s3                  |
| s3                                    | S3 Bucket information                                                           | map    | True     | See variables.tf    |
| azure_storage                         | Azure Object storage information                                                | map    | True     | See variables.tf    |
| admin_password                        | The password for the admin user.                                                | string | True     | null                |
| tls_private_key                       | The file path of the private key to use for TLS certificates.                   | string | True     | null                |
| kyuubi_profile                        | The profile to be used for Kyuubi; should be one of 'testing', 'staging' [...]  | string | False    | production          |
| kyuubi_user                           | Define the user to be used for running Kyuubi enginers                          | string | True     | kyuubi-spark-engine |
| enable_dynamic_allocation             | Enable dynamic allocation of pods for Spark jobs.                               | bool   | True     | False               |
| kyuubi_k8s_node_selectors             | Comma separated label:value selectors for K8s pods in Kyuubi.                   | string | True     | null                |
| kyuubi_loadbalancer_extra_annotations | Optional extra annotations to be supplied to the load balancer service in [...] | string | True     | null                |
| kyuubi_gpu_enable                     | Enable GPU acceleration for SparkSQLEngine.                                     | bool   | True     | False               |
| kyuubi_gpu_engine_executors_limit     | Limit the number of GPUs an engine can schedule executor pods on.               | number | True     | 1                   |
| kyuubi_gpu_pinned_memory              | Set the host memory (in GB) per executor reserved for fast data transfer [...]  | number | True     | 1                   |
| kyuubi_driver_pod_template            | Define K8s driver pod from a file accessible in the object storage.             | string | True     | null                |
| kyuubi_executor_pod_template          | Define K8s executor pod from a file accessible in the object storage.           | string | True     | null                |
| kyuubi_executor_cores                 | Set kyuubi executor pods cpu cores.                                             | number | True     | null                |
| kyuubi_executor_memory                | Set kyuubi executor pods memory (in GB).                                        | number | True     | null                |
| driver_pod_template                   | Define K8s driver pod from a file accessible to the `spark-submit` process.     | string | True     | null                |
| executor_pod_template                 | Define K8s executor pod from a file accessible to the `spark-submit` process.   | string | True     | null                |
| zookeeper_units                       | Define the number of zookeeper units. 3 units are recommended for high [...]    | number | False    | 3                   |
| history_server_revision               | Charm revision for spark-history-server-k8s                                     | number | True     | null                |
| history_server_image                  | Image for spark-history-server-k8s                                              | map    | True     | null                |
| integration_hub_revision              | Charm revision for spark-integration-hub-k8s                                    | number | True     | null                |
| integration_hub_image                 | Image for spark-integration-hub-k8s                                             | map    | True     | null                |
| kyuubi_revision                       | Charm revision for kyuubi-k8s                                                   | number | True     | null                |
| kyuubi_image                          | Image for kyuubi-k8s                                                            | map    | True     | null                |
| kyuubi_units                          | Number of Kyuubi units. 3 units are recommended for high availability.          | number | False    | 3                   |
| kyuubi_users_revision                 | Charm revision for postgresql-k8s (auth-db)                                     | number | True     | null                |
| kyuubi_users_image                    | Image for postgresql-k8s (auth-db)                                              | map    | True     | null                |
| metastore_revision                    | Charm revision for postgresql-k8s (metastore)                                   | number | True     | null                |
| metastore_image                       | Image for postgresql-k8s (metastore)                                            | map    | True     | null                |
| zookeeper_revision                    | Charm revision for zookeeper-k8s                                                | number | True     | null                |
| zookeeper_image                       | Image for zookeeper-k8s                                                         | map    | True     | null                |
| data_integrator_revision              | Charm revision for data-integrator                                              | number | True     | null                |
| s3_revision                           | Charm revision for s3-integrator                                                | number | True     | null                |
| azure_storage_revision                | Charm revision for azure-storage-integrator                                     | number | True     | null                |
| grafana_agent_revision                | Charm revision for grafana-agent-k8s                                            | number | True     | null                |
| cos_configuration_revision            | Charm revision for cos-configuration-k8s                                        | number | True     | null                |
| pushgateway_revision                  | Charm revision for prometheus-pushgateway-k8s                                   | number | True     | null                |
| scrape_config_revision                | Charm revision for prometheus-scrape-config-k8s                                 | number | True     | null                |
| certificate_common_name               | Common name for the certificate to be used in self-signed                       | string | True     | charmed-spark       |

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
  source                    = "git::https://github.com/canonical/spark-k8s-bundle//releases/3.5/terraform/modules/spark"
  model                     = juju_model.spark.name
  tls_app_name              = module.ssc.app_name
  tls_certificates_endpoint = module.ssc.provides.certificates
}

module "azure" {
  depends_on   = [juju_model.spark]
  source       = "git::https://github.com/canonical/spark-k8s-bundle//releases/3.5/terraform/modules/azure-storage"
  model        = juju_model.spark.name
  spark_charms = module.spark.charms
  azure = {
    storage_account = "storage_account"
    storage_secret  = "storage_secret"
  }
}
```

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
| ------------- | ---------------------------- | ------------- | -------- |
| azure         | azure-storage-integrator     | latest/edge   | 15       |
| observability | grafana-agent-k8s            | 1/stable      | 121      |
| observability | cos-configuration-k8s        | 1/stable      | 65       |
| observability | prometheus-pushgateway-k8s   | 1/stable      | 27       |
| observability | prometheus-scrape-config-k8s | 1/stable      | 67       |
| spark         | spark-history-server-k8s     | 3/stable      | 47       |
| spark         | spark-integration-hub-k8s    | 3/stable      | 67       |
| spark         | kyuubi-k8s                   | 3.5/stable    | 121      |
| spark         | postgresql-k8s               | 14/stable     | 495      |
| spark         | postgresql-k8s               | 14/stable     | 495      |
| spark         | zookeeper-k8s                | 3/stable      | 78       |
| spark         | data-integrator              | latest/stable | 179      |
| s3            | s3-integrator                | 1/stable      | 145      |

### Updating the inputs table

1. Run `tox -e tfinputs` from the `python` folder.
2. Paste the relevant output table in the README.

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
