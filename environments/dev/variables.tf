variable "aws_region" {
  description = "AWS region for the dev environment."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment stage used for tags and control-plane policy."
  type        = string
  default     = "dev"
}

variable "container_image" {
  description = "ECR image URI for the Aeros core API (identical across tenants)."
  type        = string
  default     = "000000000000.dkr.ecr.us-east-1.amazonaws.com/aeros-core:dev"
}

variable "areos_tenants_dir" {
  description = "Path inside the container where the tenants config bundle is mounted/synced."
  type        = string
  default     = "/tenants"
}

variable "tenants" {
  description = <<-EOT
    Map of tenant_id => tenant settings. Each tenant is provisioned into its own
    isolated VPC. CIDRs MUST NOT overlap. Adding a tenant is a config-only change:
    add an entry here and re-apply.
  EOT
  type = map(object({
    vpc_cidr           = string
    desired_task_count = optional(number, 1)
  }))
}
