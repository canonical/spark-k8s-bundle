# Copyright 2024 Canonical Ltd.
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
  default = {
    app_name    = "history-server"
    base        = "ubuntu@22.04"
    constraints = "arch=amd64"
    units       = 1
  }
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
  default = {
    app_name    = "integration-hub"
    base        = "ubuntu@22.04"
    constraints = "arch=amd64"
    units       = 1
  }
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
  default = {
    app_name    = "kyuubi"
    base        = "ubuntu@22.04"
    constraints = "arch=amd64"
    units       = 1
  }
}


variable "admin_password" {
  description = "The password for the admin user."
  type        = string
  sensitive   = true
  default     = null
}


# variable "driver_pod_template" {
#   description = "Define K8s driver pod from a file accessible to the `spark-submit` process."
#   type        = string
#   default     = null
# }

# variable "enable_dynamic_allocation" {
#   description = "Enable dynamic allocation of pods for Spark jobs."
#   type        = bool
#   default     = false
# }

# variable "executor_pod_template" {
#   description = "Define K8s executor pod from a file accessible to the `spark-submit` process."
#   type        = string
#   default     = null
# }

# variable "history_server_image" {
#   description = "Image for spark-history-server-k8s"
#   type        = map(string)
#   nullable    = false
# }

# variable "history_server_revision" {
#   description = "Charm revision for spark-history-server-k8s"
#   type        = number
#   nullable    = false
# }

# variable "integration_hub_image" {
#   description = "Image for spark-integration-hub-k8s"
#   type        = map(string)
#   nullable    = false
# }

# variable "integration_hub_monitored_service_accounts" {
#   description = "Comma-separated patterns for namespaces and service accounts to monitor and update"
#   type        = string
#   default     = null
# }

# variable "integration_hub_revision" {
#   description = "Charm revision for spark-integration-hub-k8s"
#   type        = number
#   nullable    = false
# }

# variable "kyuubi_driver_pod_template" {
#   description = "Define K8s driver pod from a file accessible in the object storage."
#   type        = string
#   default     = null
# }

# variable "kyuubi_executor_cores" {
#   description = "Set kyuubi executor pods cpu cores."
#   type        = number
#   default     = null
# }

# variable "kyuubi_executor_memory" {
#   description = "Set kyuubi executor pods memory (in GB)."
#   type        = number
#   default     = null
# }

# variable "kyuubi_executor_pod_template" {
#   description = "Define K8s executor pod from a file accessible in the object storage."
#   type        = string
#   default     = null
# }

# variable "kyuubi_gpu_enable" {
#   description = "Enable GPU acceleration for SparkSQLEngine."
#   type        = bool
#   nullable    = false
# }

# variable "kyuubi_gpu_engine_executors_limit" {
#   description = "Limit the number of GPUs an engine can schedule executor pods on."
#   type        = number
#   nullable    = false
# }

# variable "kyuubi_gpu_pinned_memory" {
#   description = "Set the host memory (in GB) per executor reserved for fast data transfer on GPUs."
#   type        = number
#   nullable    = false
# }

# variable "kyuubi_image" {
#   description = "Image for kyuubi-k8s"
#   type        = map(string)
#   nullable    = false
# }

# variable "kyuubi_k8s_node_selectors" {
#   description = "Comma separated label:value selectors for K8s pods in Kyuubi."
#   type        = string
#   default     = null
# }

# variable "kyuubi_loadbalancer_extra_annotations" {
#   description = "Optional extra annotations to be supplied to the load balancer service in Kyuubi."
#   type        = string
#   default     = null
# }

# variable "kyuubi_profile" {
#   description = "The profile to be used for Kyuubi; should be one of 'testing', 'staging' and 'production'."
#   type        = string
#   nullable    = false
#   default     = "production"
# }

# variable "kyuubi_revision" {
#   description = "Charm revision for kyuubi-k8s"
#   type        = number
#   nullable    = false
# }

# variable "kyuubi_units" {
#   description = "Number of Kyuubi units. 3 units are recommended for high availability."
#   type        = number
#   default     = 3
#   nullable    = false
# }

# variable "kyuubi_user" {
#   description = "User name to be used for running Kyuubi engines."
#   type        = string
#   nullable    = false
#   default     = "kyuubi-spark-engine"
# }





variable "data_integrator_endpoint" {
  description = "In-model endpoint for the data-integrator application."
  type = object({
    name     = string
    endpoint = optional(string, "kyuubi")
  })
}

variable "metastore_endpoint" {
  description = "In-model endpoint for the metastore (postgresql-k8s) application."
  type = object({
    name     = string
    endpoint = optional(string, "database")
  })
}

variable "tls_endpoint" {
  description = "In-model endpoint for the TLS certificates provider."
  type = object({
    name     = string
    endpoint = optional(string, "certificates")
  })
}

variable "tls_private_key" {
  description = "The private key to be used for TLS certificates."
  type        = string
  sensitive   = true
  default     = null
}

variable "users_db_endpoint" {
  description = "In-model endpoint for the Kyuubi users database (postgresql-k8s) application."
  type = object({
    name     = string
    endpoint = optional(string, "database")
  })
}

variable "zookeeper_endpoint" {
  description = "In-model endpoint for the ZooKeeper application."
  type = object({
    name     = string
    endpoint = optional(string, "zookeeper")
  })
}

variable "object_storage_endpoint" {
  description = "In-model endpoint for the object storage integrator application."
  type = object({
    name     = string
    endpoint = optional(string, "s3_credentials")
  })
}

