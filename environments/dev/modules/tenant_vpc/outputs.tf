output "vpc_id" {
  description = "Isolated VPC ID for this tenant."
  value       = aws_vpc.this.id
}

output "private_subnet_ids" {
  description = "Private subnet IDs (control-plane tasks)."
  value       = aws_subnet.private[*].id
}

output "secret_arn" {
  description = "Tenant-scoped Secrets Manager secret ARN."
  value       = aws_secretsmanager_secret.tenant.arn
}

output "api_endpoint" {
  description = "Public API endpoint (populate once the ALB is provisioned)."
  value       = "https://${var.tenant_id}.dev.aeros.internal"
}
