terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "aeros-control-plane"
      Environment = "qa"
      ManagedBy   = "terraform"
    }
  }
}

module "tenant" {
  source   = "../dev/modules/tenant_vpc"
  for_each = var.tenants

  tenant_id          = each.key
  vpc_cidr           = each.value.vpc_cidr
  aws_region         = var.aws_region
  container_image    = var.container_image
  areos_tenants_dir  = var.areos_tenants_dir
  desired_task_count = try(each.value.desired_task_count, 1)
}

output "tenant_vpc_ids" {
  value = { for id, tenant in module.tenant : id => tenant.vpc_id }
}

output "tenant_endpoints" {
  value = { for id, tenant in module.tenant : id => tenant.api_endpoint }
}
