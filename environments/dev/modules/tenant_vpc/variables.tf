variable "tenant_id" {
  description = "Tenant identifier; injected into the container as AREOS_TENANT."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR for this tenant's isolated VPC. Must not overlap other tenants."
  type        = string
}

variable "aws_region" {
  description = "AWS region."
  type        = string
}

variable "container_image" {
  description = "ECR image URI for the (tenant-agnostic) Aeros core API."
  type        = string
}

variable "areos_tenants_dir" {
  description = "Container path where the tenants config bundle is available."
  type        = string
  default     = "/tenants"
}

variable "desired_task_count" {
  description = "Number of API tasks to run for this tenant."
  type        = number
  default     = 1
}
