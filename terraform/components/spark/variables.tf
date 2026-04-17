# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

variable "model_uuid" {
  description = "Reference to an existing model uuid."
  type        = string
  nullable    = false
}

variable "history_server" {
  type = object({
    app_name    = optional(string, "history-server")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "3/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}

variable "integration_hub" {
  type = object({
    app_name    = optional(string, "integration-hub")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "3/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}


variable "kyuubi" {
  type = object({
    app_name    = optional(string, "kyuubi")
    base        = optional(string, "ubuntu@22.04")
    channel     = optional(string, "3.4/stable")
    config      = optional(map(string), {})
    constraints = optional(string, "arch=amd64")
    resources   = optional(map(string), {})
    revision    = optional(number)
    units       = optional(number, 1)
  })
  default = {}
}

variable "data_integrator" {
  description = "External integration for the data-integrator application"
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })

  validation {
    condition     = contains(["endpoint", "offer"], var.data_integrator.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.data_integrator.kind == "endpoint" ? (
        var.data_integrator.name != null && var.data_integrator.name != "" &&
        var.data_integrator.endpoint != null && var.data_integrator.endpoint != ""
      ) : true
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.data_integrator.kind == "offer" ? (
        var.data_integrator.url != null && var.data_integrator.url != ""
      ) : true
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}



variable "metastore" {
  description = "External integration for the metastore (postgresql-k8s) application."
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })

  validation {
    condition     = contains(["endpoint", "offer"], var.metastore.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.metastore.kind == "endpoint" ? (
        var.metastore.name != null && var.metastore.name != "" &&
        var.metastore.endpoint != null && var.metastore.endpoint != ""
      ) : true
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.metastore.kind == "offer" ? (
        var.metastore.url != null && var.metastore.url != ""
      ) : true
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}

variable "certificates" {
  description = "External integration for the certificate provider application."
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })

  validation {
    condition     = contains(["endpoint", "offer"], var.certificates.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.certificates.kind == "endpoint" ? (
        var.certificates.name != null && var.certificates.name != "" &&
        var.certificates.endpoint != null && var.certificates.endpoint != ""
      ) : true
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.certificates.kind == "offer" ? (
        var.certificates.url != null && var.certificates.url != ""
      ) : true
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}

variable "users_db" {
  description = "External integration for the Kyuubi users database (postgresql-k8s) application."
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })

  validation {
    condition     = contains(["endpoint", "offer"], var.users_db.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.users_db.kind == "endpoint" ? (
        var.users_db.name != null && var.users_db.name != "" &&
        var.users_db.endpoint != null && var.users_db.endpoint != ""
      ) : true
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.users_db.kind == "offer" ? (
        var.users_db.url != null && var.users_db.url != ""
      ) : true
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}

variable "zookeeper" {
  description = "External integration for the ZooKeeper application."
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })

  validation {
    condition     = contains(["endpoint", "offer"], var.zookeeper.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.zookeeper.kind == "endpoint" ? (
        var.zookeeper.name != null && var.zookeeper.name != "" &&
        var.zookeeper.endpoint != null && var.zookeeper.endpoint != ""
      ) : true
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.zookeeper.kind == "offer" ? (
        var.zookeeper.url != null && var.zookeeper.url != ""
      ) : true
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}

variable "object_storage" {
  description = "External integration for the object storage integrator application."
  type = object({
    kind     = string
    name     = optional(string, null)
    endpoint = optional(string, null)
    url      = optional(string, null)
  })

  validation {
    condition     = contains(["endpoint", "offer"], var.object_storage.kind)
    error_message = "The 'kind' attribute must be either 'endpoint' or 'offer'."
  }

  validation {
    condition = (
      var.object_storage.kind == "endpoint" ? (
        var.object_storage.name != null && var.object_storage.name != "" &&
        var.object_storage.endpoint != null && var.object_storage.endpoint != ""
      ) : true
    )
    error_message = "Both 'name' and 'endpoint' attributes must be provided for an in-model integration."
  }

  validation {
    condition = (
      var.object_storage.kind == "offer" ? (
        var.object_storage.url != null && var.object_storage.url != ""
      ) : true
    )
    error_message = "The 'url' attribute must be provided for a cross-model integration."
  }
}

variable "object_storage_interface" {
  description = "The interface of the object storage backend."
  type        = string

  validation {
    condition     = contains(["s3-credentials", "azure-storage-credentials"], var.object_storage_interface)
    error_message = "The only object storage interfaces supported are 's3-credentials' and 'azure-storage-credentials'."
  }
}
