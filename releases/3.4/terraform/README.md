# Spark

## Usage

The features are split into multiples submodules, where each file has a dedicated role:

- `applications.tf` -> Speak for itself
- `integrations.tf` -> Same
- `resources.tf` -> Define juju models, secrets, cross model offers
  each module can also include `providers.tf`, `variables.tf` and `outputs.tf`. The latter is especially useful to pass values back to a different module.

Modules description:

- `spark`: main spark module with integration-hub, history-server, kyuubi
- `s3` and `azure-storage`: storage backend. Having one of them is necessary, and they are mutually exclusive
- `cos`: observability stack (= the COS bundle)
- `observabiliby`: parts of the observability stack to be deployed alongside spark (config, pushgateway, etc.)

Outside the 5 main modules, `main.tf` only takes care of instantiating the modules and passing the variables to them.
We defined a dependency chain such as cos, s3 and azure depends on spark.
By depending on spark, they can use whatever output spark defines.\
This means that using this structure, an optional module takes care of defining its applications and their integrations with the existing resources, in contrast to what was originally suggested by the reversed dependency chain in the GH repository.
`observability` depends on both spark and cos.

## Content

| Module        | Channel       | Charm                        | revision |
| ------------- | ------------- | ---------------------------- | -------- |
| azure         | latest/edge   | azure-storage-integrator     | 9        |
| cos           | latest/stable | alertmanager-k8s             |          |
| cos           | latest/stable | catalogue-k8s                |          |
| cos           | latest/stable | grafana-k8s                  |          |
| cos           | latest/stable | loki-k8s                     |          |
| cos           | latest/stable | prometheus-k8s               |          |
| cos           | latest/stable | traefik-k8s                  |          |
| observability | latest/edge   | grafana-agent-k8s            | 103      |
| observability | latest/stable | cos-configuration-k8s        | 63       |
| observability | latest/stable | prometheus-pushgateway-k8s   | 16       |
| observability | latest/stable | prometheus-scrape-config-k8s | 51       |
| spark         | latest/edge   | self-signed-certificates     | 163      |
| spark         | 3.4/edge      | spark-history-server-k8s     | 37       |
| spark         | latest/edge   | spark-integration-hub-k8s    | 31       |
| spark         | latest/edge   | kyuubi-k8s                   | 31       |
| spark         | 14/stable     | postgresql-k8s               | 281      |
| spark         | 14/stable     | postgresql-k8s               | 281      |
| spark         | 3/edge        | zookeeper-k8s                | 75       |
| s3            | latest/stable | s3-integrator                | 77       |

### Updating the table

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
        charms_summary.append([name, *charm.values()])


data = [["Module", "Channel", "Charm", "revision"]] + charms_summary
md_table = "\n".join(
    [
        "| " + " | ".join(map(str, row)) + " |"
        for row in [data[0], ["---"] * len(data[0])] + data[1:]
    ]
)
print(md_table)
```
