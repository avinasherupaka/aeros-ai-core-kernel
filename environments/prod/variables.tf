variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "container_image" {
  type        = string
  description = "Validated immutable production image digest or release tag."
}

variable "areos_tenants_dir" {
  type    = string
  default = "/tenants"
}

variable "tenants" {
  type = map(object({
    vpc_cidr           = string
    desired_task_count = optional(number, 2)
  }))
}
