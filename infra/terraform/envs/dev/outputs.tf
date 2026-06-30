output "tenant_site_cell_id" {
  value = module.tenant_site_cell.tenant_site_cell_id
}

output "evidence_bucket_name" {
  value = module.evidence_lake.bucket_name
}

output "event_metadata_table_name" {
  value = module.tenant_site_cell.event_metadata_table_name
}

output "iot_thing_name" {
  value = module.iot_core.thing_name
}

output "github_oidc_role_arn" {
  value = module.github_oidc.github_actions_role_arn
}

output "neptune_cluster_endpoint" {
  value = module.neptune.cluster_endpoint
}

output "glue_database_name" {
  value = module.lakehouse_catalog.glue_database_name
}

output "athena_workgroup_name" {
  value = module.lakehouse_catalog.athena_workgroup_name
}

output "workflow_state_machine_arn" {
  value = module.workflow_runtime.state_machine_arn
}
