terraform {
  required_version = ">= 1.6.0"
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  resolved_tags = merge(
    {
      project           = "areos"
      managed_by        = "terraform"
      assurance_runtime = "aws-native"
      environment       = var.environment
    },
    var.tags
  )
}
