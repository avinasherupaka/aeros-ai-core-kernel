locals {
  tenant_site = "${var.tenant_id}/${var.site_id}"
  gateway_id  = "${var.tenant_id}-${var.site_id}-gateway"
}

resource "aws_iot_thing_type" "site_gateway" {
  name = var.thing_type_name

  properties {
    description = "Areos tenant-site edge gateway thing type"
  }
}

resource "aws_iot_thing" "site_gateway" {
  name       = local.gateway_id
  thing_type = aws_iot_thing_type.site_gateway.name

  attributes = {
    tenant_id = var.tenant_id
    site_id   = var.site_id
  }
}

resource "aws_iot_policy" "tenant_site" {
  name = "areos-${var.tenant_id}-${var.site_id}-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["iot:Connect"]
        Resource = [
          "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:client/${var.client_id_prefix}-${var.tenant_id}-${var.site_id}-*"
        ]
      },
      {
        Effect = "Allow"
        Action = ["iot:Publish", "iot:Subscribe", "iot:Receive"]
        Resource = [
          "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/${var.topic_prefix}/${local.tenant_site}/*",
          "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topicfilter/${var.topic_prefix}/${local.tenant_site}/*"
        ]
      }
    ]
  })
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

resource "aws_iam_role" "iot_rule_logs" {
  name = "areos-${var.tenant_id}-${var.site_id}-iot-rule-logs"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "iot.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "iot_rule_logs" {
  name = "allow-cloudwatch-logs"
  role = aws_iam_role.iot_rule_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${var.cloudwatch_log_group_arn}:*"
    }]
  })
}

resource "aws_iot_topic_rule" "tenant_site_route" {
  name        = replace("areos_${var.tenant_id}_${var.site_id}_ingest", "-", "_")
  enabled     = true
  sql         = "SELECT * FROM '${var.topic_prefix}/${local.tenant_site}/#'"
  sql_version = "2016-03-23"

  cloudwatch_logs {
    log_group_name = var.cloudwatch_log_group_name
    role_arn       = aws_iam_role.iot_rule_logs.arn
  }
}

# Certificate provisioning/attachment is intentionally handled outside Terraform
# runbooks for safer key custody and rotation practices.
