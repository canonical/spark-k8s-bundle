# Spark-Core component terraform module

The `spark-core` component bundles the following charms:
- Spark History Server
- Spark Integration Hub

## Module reference

The spark-core module provides the core components for the Spark ecosystem, including the history server for tracking job execution history and the integration hub for managing integrations with external services.

### Inputs

- `history_server`: Configuration for the Spark History Server application
- `integration_hub`: Configuration for the Spark Integration Hub application
- `object_storage`: External integration for the object storage integrator application
- `object_storage_interface`: The interface of the object storage backend (s3-credentials or azure-storage-credentials)
- `model_uuid`: Reference to an existing model uuid
- `risk`: Component's charms risk channel (edge, beta, candidate, or stable; default: stable)

### Outputs

- `components`: Map of the deployed applications (history_server, integration_hub)
- `requires`: Map of the requires endpoints
- `provides`: Map of the provides endpoints
- `offers`: Map of all offers exposed by the component's charms
