output "lambda_execution_role_arn" {
  value       = local.create ? aws_iam_role.lambda_execution[0].arn : null
  description = "Lambda execution role ARN."
}

output "bedrock_runtime_role_arn" {
  value       = local.create ? aws_iam_role.bedrock_runtime[0].arn : null
  description = "Bedrock runtime role ARN."
}

output "state_machine_arn" {
  value       = local.create ? aws_sfn_state_machine.assurance[0].arn : null
  description = "Step Functions state machine ARN."
}
