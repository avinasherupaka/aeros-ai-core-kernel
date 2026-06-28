locals {
  tenant_site_cell_id = "${var.tenant_id}-${var.site_id}"
}

resource "aws_kms_key" "cell" {
  description             = "KMS key for tenant-site cell ${local.tenant_site_cell_id}"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  tags                    = var.tags
}

resource "aws_kms_alias" "cell" {
  name          = "alias/areos/${local.tenant_site_cell_id}"
  target_key_id = aws_kms_key.cell.key_id
}

resource "aws_dynamodb_table" "event_metadata" {
  name         = "areos-${local.tenant_site_cell_id}-event-metadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.cell.arn
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "cell" {
  name              = "/areos/${var.environment}/tenant-site/${local.tenant_site_cell_id}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cell.arn
  tags              = var.tags
}

# IAM permissions boundaries and cross-role scope constraints should be wired
# in enterprise landing-zone accounts. This module keeps core identifiers/outputs.
