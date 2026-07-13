variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "container_image" {
  type    = string
  default = "000000000000.dkr.ecr.us-east-1.amazonaws.com/aeros-core:qa"
}

variable "areos_tenants_dir" {
  type    = string
  default = "/tenants"
}

variable "tenants" {
  type = map(object({
    vpc_cidr           = string
    desired_task_count = optional(number, 1)
  }))
}
