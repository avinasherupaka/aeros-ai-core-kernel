terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  account_id          = module.foundation.account_id
  evidence_bucket_arn = module.evidence_lake.bucket_arn
  table_arn           = "arn:aws:dynamodb:${var.aws_region}:${local.account_id}:table/${module.tenant_site_cell.event_metadata_table_name}"
  app_log_group_arn   = "arn:aws:logs:${var.aws_region}:${local.account_id}:log-group:${module.observability.application_log_group_name}"
  iot_log_group_arn   = "arn:aws:logs:${var.aws_region}:${local.account_id}:log-group:${module.observability.iot_log_group_name}"
  cell_log_group_arn  = "arn:aws:logs:${var.aws_region}:${local.account_id}:log-group:${module.tenant_site_cell.log_group_name}"
  iot_thing_arn       = "arn:aws:iot:${var.aws_region}:${local.account_id}:thing/${module.iot_core.thing_name}"
  iot_policy_arn      = "arn:aws:iot:${var.aws_region}:${local.account_id}:policy/${module.iot_core.policy_name}"
  iot_rule_arn        = "arn:aws:iot:${var.aws_region}:${local.account_id}:rule/${module.iot_core.topic_rule_name}"
  sitewise_model_arn  = "arn:aws:iotsitewise:${var.aws_region}:${local.account_id}:asset-model/*"
}

module "foundation" {
  source      = "../../modules/foundation"
  environment = var.environment
  tags        = var.tags
}

module "evidence_lake" {
  source         = "../../modules/evidence_lake"
  bucket_name    = var.evidence_bucket_name
  create_kms_key = true
  tags           = module.foundation.common_tags
}

module "observability" {
  source             = "../../modules/observability"
  environment        = var.environment
  log_retention_days = var.log_retention_days
  tags               = module.foundation.common_tags
}

module "tenant_site_cell" {
  source             = "../../modules/tenant_site_cell"
  environment        = var.environment
  tenant_id          = var.tenant_id
  site_id            = var.site_id
  log_retention_days = var.log_retention_days
  tags               = module.foundation.common_tags
}

module "iot_core" {
  source                    = "../../modules/iot_core"
  tenant_id                 = var.tenant_id
  site_id                   = var.site_id
  topic_prefix              = var.topic_prefix
  cloudwatch_log_group_name = module.observability.iot_log_group_name
  cloudwatch_log_group_arn  = "arn:aws:logs:${var.aws_region}:${module.foundation.account_id}:log-group:${module.observability.iot_log_group_name}"
}

module "sitewise" {
  source                    = "../../modules/sitewise"
  site_name                 = var.site_id
  enable_sitewise_resources = var.enable_sitewise_resources
}

module "github_oidc" {
  source           = "../../modules/iam_github_oidc"
  role_name        = var.github_oidc_role_name
  allowed_subjects = var.github_allowed_subjects
  inline_policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = [local.evidence_bucket_arn]
      },
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = ["${local.evidence_bucket_arn}/*"]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:DescribeTable",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [local.table_arn]
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents", "logs:DescribeLogGroups", "logs:DescribeLogStreams"]
        Resource = [local.app_log_group_arn, "${local.app_log_group_arn}:*", local.iot_log_group_arn, "${local.iot_log_group_arn}:*", local.cell_log_group_arn, "${local.cell_log_group_arn}:*"]
      },
      {
        Effect   = "Allow"
        Action   = ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
        Resource = compact([module.evidence_lake.kms_key_arn, module.tenant_site_cell.kms_key_arn])
      },
      {
        Effect = "Allow"
        Action = [
          "iot:CreateThing",
          "iot:DeleteThing",
          "iot:DescribeThing",
          "iot:CreatePolicy",
          "iot:DeletePolicy",
          "iot:GetPolicy",
          "iot:CreateTopicRule",
          "iot:DeleteTopicRule",
          "iot:GetTopicRule",
          "iot:ReplaceTopicRule"
        ]
        Resource = [local.iot_thing_arn, local.iot_policy_arn, local.iot_rule_arn]
      },
      {
        Effect   = "Allow"
        Action   = ["iotsitewise:CreateAssetModel", "iotsitewise:UpdateAssetModel", "iotsitewise:DeleteAssetModel", "iotsitewise:DescribeAssetModel"]
        Resource = [local.sitewise_model_arn]
      },
      {
        Effect   = "Allow"
        Action   = ["sts:GetCallerIdentity", "iotsitewise:ListAssetModels", "kms:ListAliases", "iot:ListThings", "iot:ListPolicies", "iot:ListTopicRules"]
        Resource = ["*"]
      }
    ]
  })
  tags = module.foundation.common_tags
}
