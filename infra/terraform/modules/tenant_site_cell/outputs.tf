locals {
  tenant_site_cell_id = "${var.tenant_id}-${var.site_id}"
}

output "tenant_site_cell_id" {
  value       = local.tenant_site_cell_id
  description = "Tenant-site cell identifier."
}

output "kms_key_arn" {
  value       = aws_kms_key.cell.arn
  description = "Tenant-site cell KMS key ARN."
}

output "event_metadata_table_name" {
  value       = aws_dynamodb_table.event_metadata.name
  description = "DynamoDB table name for event metadata."
}

output "log_group_name" {
  value       = aws_cloudwatch_log_group.cell.name
  description = "Tenant-site log group name."
}

output "evidence_prefix" {
  value       = "tenant=${var.tenant_id}/site=${var.site_id}/"
  description = "Recommended S3 evidence prefix strategy."
}
