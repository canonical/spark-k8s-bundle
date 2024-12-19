variable "azure" {
  description = "Azure Object storage information"
  type = object({
    container            = optional(string, "azurecontainer")
    storage_account      = optional(string, "azurestorageaccount")
    protocol             = optional(string, "abfss")
    secret_key           = optional(string, "secret-key")
    path                 = optional(string, "spark-events")
  })
  default = {}
}


variable "cos_model" {
  description = "The name of the model where cos is deployed. If null, don't deploy cos related charms."
  type = string
  nullable = true
  default = null
}

variable "spark_model" {
  description = "The name of the model where spark is deployed. If null, don't deploy cos related charms."
  type = string
  nullable = true
  default = null
}