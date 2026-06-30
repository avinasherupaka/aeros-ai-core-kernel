locals {
  create = var.enabled && length(var.subnet_ids) > 0
}

resource "aws_neptune_subnet_group" "this" {
  count       = local.create ? 1 : 0
  name        = "${var.name}-subnets"
  subnet_ids  = var.subnet_ids
  description = "Subnets for ${var.name}"
  tags        = var.tags
}

resource "aws_neptune_cluster" "this" {
  count                           = local.create ? 1 : 0
  cluster_identifier              = var.name
  engine_version                  = var.engine_version
  neptune_subnet_group_name       = aws_neptune_subnet_group.this[0].name
  vpc_security_group_ids          = var.security_group_ids
  iam_database_authentication_enabled = true
  backup_retention_period         = 7
  apply_immediately               = true
  storage_encrypted               = true
  tags                            = var.tags
}

resource "aws_neptune_cluster_instance" "this" {
  count              = local.create ? 1 : 0
  cluster_identifier = aws_neptune_cluster.this[0].id
  instance_class     = "db.r6g.large"
  engine             = "neptune"
  apply_immediately  = true
  tags               = var.tags
}
