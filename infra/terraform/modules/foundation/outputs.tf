output "account_id" {
  value       = data.aws_caller_identity.current.account_id
  description = "Current AWS account id."
}

output "region" {
  value       = data.aws_region.current.name
  description = "Current AWS region."
}

output "common_tags" {
  value       = local.resolved_tags
  description = "Merged common tags for downstream modules."
}
