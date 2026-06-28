output "application_log_group_name" {
  value       = aws_cloudwatch_log_group.app.name
  description = "Application log group name."
}

output "iot_log_group_name" {
  value       = aws_cloudwatch_log_group.iot.name
  description = "IoT log group name."
}
