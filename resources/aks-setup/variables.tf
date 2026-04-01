variable "num_nodes" {
  description = "Number of nodes in the AKS cluster"
  type        = number
  default     = 3
}

variable "cluster_name" {
  description = "The name of the AKS cluster to be created"
  type        = string
  default     = "TestAKSCluster"
}

variable "region" {
  description = "The region in which cloud resources are to be created"
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "The name of the resource group under which the resources will be created"
  type        = string
  default     = "TestSparkAKSRG"
}