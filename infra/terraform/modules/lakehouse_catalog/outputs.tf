output "glue_database_name" {
  value       = local.create ? aws_glue_catalog_database.this[0].name : null
  description = "Glue database name."
}

output "athena_workgroup_name" {
  value       = local.create ? aws_athena_workgroup.this[0].name : null
  description = "Athena workgroup name."
}
