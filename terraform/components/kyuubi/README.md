# Kyuubi component terraform module

Manages the Kyuubi SQL engine charm with all necessary integrations for use in conjunction with the spark-core module.

## Module reference

The kyuubi component module provides a complete deployment of the Kyuubi SQL engine with all necessary integrations.

### Inputs

**Application Configuration:**
- `kyuubi`: Configuration object for Kyuubi application with the following attributes:
  - `app_name`: Name to give the deployed Kyuubi application (default: "kyuubi")
  - `base`: The operating system on which to deploy Kyuubi (default: "ubuntu@22.04")
  - `track`: Track of the Kyuubi charm (default: "3.4")
  - `config`: Map for Kyuubi configuration options (default: {})
  - `constraints`: String listing constraints for the Kyuubi application (default: "arch=amd64")
  - `resources`: Resources to attach to the Kyuubi application (default: null)
  - `revision`: Revision number of the Kyuubi charm (default: null)
  - `units`: Unit count for Kyuubi (default: 1)

**Risk Channel:**
- `risk`: Component's charms risk channel (default: "stable")

**Module Dependencies:**
- `model_uuid`: Reference to an existing model uuid (required)

**External Integrations:**
- `spark_service_account`: External integration for the Spark service account (integration hub) application (required)
- `certificates`: External integration for the certificate provider application (required)
- `data_integrator`: External integration for the data-integrator application (required)
- `metastore`: External integration for the metastore (postgresql-k8s) application (required)
- `users_db`: External integration for the Kyuubi users database (postgresql-k8s) application (required)
- `zookeeper`: External integration for the ZooKeeper application (required)

### Outputs

- `application`: Object representing the deployed Kyuubi application
- `components`: Map of the deployed applications (kyuubi)
- `requires`: Map of the requires endpoints
- `provides`: Map of the provides endpoints
- `offers`: Map of all offers exposed by the component's charms
