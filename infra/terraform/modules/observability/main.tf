resource "aws_cloudwatch_log_group" "app" {
  name              = "/areos/${var.environment}/application"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "iot" {
  name              = "/areos/${var.environment}/iot"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

# CloudTrail / AWS Config / Security Hub / GuardDuty are recommended baseline
# controls and should be enabled according to enterprise landing-zone policy.
