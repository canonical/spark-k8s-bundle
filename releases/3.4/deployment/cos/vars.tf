# cos specifics
variable "model" {
  type        = string
  default     = null
  description = "cos"  
}

variable "COS_TLS_CERT" {
  type        = string
  default     = ""
  description = "COS certificate"
}
variable "COS_TLS_KEY" {
  type        = string
  default     = ""
  description = "COS certificate key"
}
variable "COS_TLS_CA" {
  type        = string
  default     = ""
  description = "COS CA certificate"
}