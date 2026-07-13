##############################################################################
# Aeros — AWS Dev Environment (tenant-isolated infrastructure)
#
# Each tenant is provisioned into its OWN VPC via the reusable tenant_vpc module,
# guaranteeing network segregation and strict data tenancy. The Aeros core image
# is identical across tenants; the tenant is selected at runtime by the
# AREOS_TENANT environment variable injected into the ECS task definition.
##############################################################################

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }

  # Configure remote state per your org standards (S3 + DynamoDB lock).
  # backend "s3" {
  #   bucket         = "aeros-dev-tfstate"
  #   key            = "control-plane/dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "aeros-dev-tflock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "aeros-control-plane"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# One isolated VPC + control-plane stack per tenant.
module "tenant" {
  source   = "./modules/tenant_vpc"
  for_each = var.tenants

  tenant_id          = each.key
  vpc_cidr           = each.value.vpc_cidr
  aws_region         = var.aws_region
  container_image    = var.container_image
  areos_tenants_dir  = var.areos_tenants_dir
  desired_task_count = try(each.value.desired_task_count, 1)
}
