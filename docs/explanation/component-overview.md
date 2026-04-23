---
myst:
  html_meta:
    description: "Understand the components of Charmed Apache Spark: spark8t, OCI images, spark-client snap, and Juju charms for Kubernetes deployments."
---

(explanation-component-overview)=
# Components overview

Charmed Apache Spark is composed of foundational software artifacts and a set of Juju operators (charms) that together provide a fully managed Apache Spark platform on Kubernetes. All charms are available individually on [Charmhub](https://charmhub.io/) and can also be deployed together via the [Charmed Apache Spark bundle](https://charmhub.io/spark-k8s-bundle) or [Terraform modules](https://github.com/canonical/spark-k8s-bundle/tree/main/releases/3.4/terraform).

## Software artifacts

### spark8t

[spark8t](https://github.com/canonical/spark-k8s-toolkit-py) is a Python library that extends Apache Spark with tooling to manage Spark jobs and service accounts with hierarchical configuration. It is the foundation shared by both the `spark-client` snap and the Juju charms.

### Charmed Apache Spark Rock

The [Charmed Apache Spark Rock](https://github.com/canonical/charmed-spark-rock/pkgs/container/charmed-spark) is an OCI-compliant container image that bundles Apache Spark binaries together with Canonical tooling. It is used as the base image for Spark driver and executor pods on Kubernetes, and as the foundation for the `spark-client` snap.

### spark-client snap

The [spark-client snap](https://snapcraft.io/spark-client) provides CLI tools for working with Charmed Apache Spark from a workstation or edge node. It communicates with the Kubernetes API to submit jobs and manage service accounts — it does not connect to any Juju charm directly.

| Command | Description |
|---|---|
| `spark-client.spark-submit` | Submit Spark applications to a Kubernetes cluster |
| `spark-client.pyspark` | Start an interactive PySpark shell |
| `spark-client.service-account-registry` | Create, configure, and manage Spark service accounts |
| `spark-client.beeline` | JDBC client for connecting to Apache Kyuubi endpoints |
| `spark-client.import-certificate` | Import TLS certificates for encrypted Kyuubi connections |

## Juju operators (charms)

### Core integrators

The following charms form the foundation of any Charmed Apache Spark deployment, connecting Spark service accounts to object storage:

| Charm | Description |
|---|---|
| [`spark-integration-hub-k8s`](https://charmhub.io/spark-integration-hub-k8s) | Central hub that manages Spark service account configurations and writes them into Kubernetes Secrets. Connects to object storage integrators, Kyuubi, and optionally to the COS observability bridge. |
| [`s3-integrator`](https://charmhub.io/s3-integrator) | Supplies S3-compatible object storage credentials (endpoint, bucket, access key) to the Integration Hub and History Server. Supports MinIO, AWS S3, and any S3-compatible backend. |
| [`azure-storage-integrator`](https://charmhub.io/azure-storage-integrator) | Alternative to `s3-integrator` for deployments using Azure Blob Storage. |

### History Server

| Charm | Description |
|---|---|
| [`spark-history-server-k8s`](https://charmhub.io/spark-history-server-k8s) | Exposes a web UI for browsing and analyzing event logs of completed Spark jobs stored in object storage. Receives credentials from `s3-integrator` or `azure-storage-integrator`. |
| [`traefik-k8s`](https://charmhub.io/traefik-k8s) | Kubernetes ingress proxy. Exposes the History Server web UI at a stable URL outside the cluster. |

### Apache Kyuubi (SQL / JDBC)

[Charmed Apache Kyuubi](https://charmhub.io/kyuubi-k8s) provides a JDBC/ODBC endpoint for running SQL queries against data in object storage, powered by Apache Spark engines.

| Charm | Description |
|---|---|
| [`kyuubi-k8s`](https://charmhub.io/kyuubi-k8s) | Provides a JDBC/ODBC endpoint for SQL queries. Integrates with the Integration Hub to obtain Spark service account configuration. Supports horizontal scaling and external metastore. |
| [`postgresql-k8s`](https://charmhub.io/postgresql-k8s) (as `auth-db`) | Required authentication database for Kyuubi. Kyuubi will remain blocked without this integration. |
| [`postgresql-k8s`](https://charmhub.io/postgresql-k8s) (as `metastore`) | External Hive metastore providing persistent metadata storage. Without it, metadata is stored on pod-local storage and lost on pod restarts. |
| [`zookeeper-k8s`](https://charmhub.io/zookeeper-k8s) | Required for multi-node Kyuubi deployments. Coordinates distributed Kyuubi instances. |
| [`self-signed-certificates`](https://charmhub.io/self-signed-certificates) | Provides TLS certificates to Kyuubi for encrypted JDBC connections. For production environments, use a CA-backed certificates operator instead. |
| [`data-integrator`](https://charmhub.io/data-integrator) | Retrieves JDBC credentials (endpoint, username, password, TLS certificate) from Kyuubi via the `get-credentials` action, making them available to external clients. |

### Observability (COS integration)

Charmed Apache Spark integrates natively with the [Canonical Observability Stack (COS)](https://charmhub.io/cos-lite), which is deployed in a separate Juju model and includes Grafana, Prometheus, Loki, and Alertmanager.

The [Tutorial](tutorial-introduction) demonstrates a simplified COS setup using only `prometheus-pushgateway-k8s` and `cos-configuration-k8s`, integrated directly with the COS model charms. The full bundle overlay additionally deploys `grafana-agent-k8s` and `prometheus-scrape-config-k8s` as a cross-model observability bridge:

| Charm | Tutorial | Bundle | Description |
|---|---|---|---|
| [`prometheus-pushgateway-k8s`](https://charmhub.io/prometheus-pushgateway-k8s) | Yes | Yes | Accepts metrics pushed by ephemeral Spark jobs (which are too short-lived for pull-based scraping) and exposes them to Prometheus. In the full bundle, integrates with the Integration Hub to automatically configure service accounts with the pushgateway address. |
| [`cos-configuration-k8s`](https://charmhub.io/cos-configuration-k8s) | Yes | Yes | Syncs Grafana dashboard definitions from a git repository into Grafana. Pre-configured in the bundle to use the dashboards from this repository. |
| [`grafana-agent-k8s`](https://charmhub.io/grafana-agent-k8s) | — | Yes | Cross-model bridge that ships metrics, log streams, and dashboard definitions from the Spark model to the COS model via remote-write and Loki push API. |
| [`prometheus-scrape-config-k8s`](https://charmhub.io/prometheus-scrape-config-k8s) | — | Yes | Configures the Prometheus scrape interval for the Pushgateway metrics endpoint. |

## Architecture

The following diagram shows how the components relate in a full deployment:

```{mermaid}
flowchart TB
    client["<b>spark-client snap</b><br>spark-submit · pyspark<br>beeline · service-account-registry"]
    backend[("<b>Object Storage</b><br>MinIO · AWS S3 · Azure Blob")]

    subgraph spark-model["Spark Juju Model"]
        direction TB

        hub["<b>spark-integration-hub-k8s</b>"]

        subgraph integrators["Storage Integrators"]
            direction LR
            s3int["s3-integrator"]
            azint["azure-storage-integrator"]
        end

        subgraph hist-grp["History Server"]
            direction LR
            hs["spark-history-server-k8s"]
            traefik["traefik-k8s"]
        end

        subgraph kyu-grp["Apache Kyuubi"]
            direction TB
            kyuubi["kyuubi-k8s"]
            authdb["postgresql-k8s<br>(auth-db)"]
            metadb["postgresql-k8s<br>(metastore)"]
            zk["zookeeper-k8s"]
            tls["self-signed-certificates"]
            di["data-integrator"]
        end

        subgraph cos-bridge["COS Bridge"]
            direction LR
            pgw["prometheus-pushgateway-k8s"]
            scrape["prometheus-scrape-config-k8s"]
            agent["grafana-agent-k8s"]
            cosconf["cos-configuration-k8s"]
        end
    end

    subgraph cos-model["COS Juju Model (cos-lite)"]
        direction LR
        prom["Prometheus"]
        graf["Grafana"]
        loki_n["Loki"]
    end

    client -->|"K8s API<br>(spark-submit / pyspark)"| hub
    client -->|"JDBC"| kyuubi
    backend <-->|credentials| s3int & azint
    s3int & azint -->|s3-credentials| hub
    s3int & azint -->|s3-credentials| hs
    hub -->|service-account| kyuubi
    hub -->|cos| pgw
    traefik -->|ingress| hs
    kyuubi --- authdb
    kyuubi --- metadb
    kyuubi --- zk
    kyuubi --- tls
    di -->|get-credentials| kyuubi
    hs -->|metrics · logs · dashboards| agent
    pgw --- scrape -->|metrics| agent
    cosconf -->|dashboards| agent
    agent -->|remote-write| prom
    agent -->|push API| loki_n
    agent -->|dashboards| graf
```

The `spark-client` tools communicate with Kubernetes directly — the Integration Hub writes configuration into K8s Secrets associated with service accounts, and `spark-client` reads them at job submission time.

For a step-by-step walkthrough of setting up these components, see the [Tutorial](tutorial-introduction). For supported Kubernetes distributions, see the [Requirements](reference-requirements) page.

