output "thing_name" {
  value       = aws_iot_thing.site_gateway.name
  description = "Simulated site gateway thing name."
}

output "policy_name" {
  value       = aws_iot_policy.tenant_site.name
  description = "Tenant-site scoped IoT policy name."
}

output "topic_rule_name" {
  value       = aws_iot_topic_rule.tenant_site_route.name
  description = "IoT topic rule name."
}
