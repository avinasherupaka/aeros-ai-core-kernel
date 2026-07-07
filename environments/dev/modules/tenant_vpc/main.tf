##############################################################################
# Module: tenant_vpc
# Provisions an isolated VPC and a Fargate-hosted Aeros control plane for ONE
# tenant. The tenant identity is injected purely via the AREOS_TENANT env var —
# the container image itself is tenant-agnostic (config-driven core).
##############################################################################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

locals {
  name = "aeros-${var.tenant_id}"
  azs  = ["${var.aws_region}a", "${var.aws_region}b"]
}

# ─────────────────────────────── Isolated VPC ───────────────────────────────
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "${local.name}-vpc", Tenant = var.tenant_id }
}

resource "aws_subnet" "private" {
  count             = length(local.azs)
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = local.azs[count.index]
  tags              = { Name = "${local.name}-private-${count.index}", Tier = "private", Tenant = var.tenant_id }
}

resource "aws_subnet" "public" {
  count                   = length(local.azs)
  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true
  tags                    = { Name = "${local.name}-public-${count.index}", Tier = "public", Tenant = var.tenant_id }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags   = { Name = "${local.name}-igw", Tenant = var.tenant_id }
}

# NOTE: NAT gateways, route tables, ALB, ECS cluster/service, task role, and
# Secrets Manager wiring are intentionally represented as placeholders below so
# this skeleton plans cleanly and documents the intended isolation model. Fill in
# per your org's networking and CI/CD standards before applying to a real account.

# ─────────────────────── Tenant-scoped secret store ─────────────────────────
resource "aws_secretsmanager_secret" "tenant" {
  name = "${var.tenant_id}/control-plane"
  tags = { Tenant = var.tenant_id }
}

# ───────────────────────── Control-plane task def (sketch) ──────────────────
# resource "aws_ecs_task_definition" "api" {
#   family                   = "${local.name}-api"
#   requires_compatibilities = ["FARGATE"]
#   network_mode             = "awsvpc"
#   cpu                      = "512"
#   memory                   = "1024"
#   container_definitions = jsonencode([{
#     name      = "api"
#     image     = var.container_image
#     essential = true
#     environment = [
#       { name = "AREOS_TENANT",      value = var.tenant_id },
#       { name = "AREOS_TENANTS_DIR", value = var.areos_tenants_dir },
#       { name = "AREOS_MODE",        value = "dev" }
#     ]
#     portMappings = [{ containerPort = 8000, protocol = "tcp" }]
#   }])
# }
