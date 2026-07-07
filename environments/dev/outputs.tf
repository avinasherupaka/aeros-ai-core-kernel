output "tenant_endpoints" {
  description = "Per-tenant control-plane API endpoints (ALB DNS names)."
  value       = { for id, m in module.tenant : id => m.api_endpoint }
}

output "tenant_vpc_ids" {
  description = "Per-tenant VPC IDs (isolation boundary)."
  value       = { for id, m in module.tenant : id => m.vpc_id }
}
