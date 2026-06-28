output "sitewise_model_template" {
  value       = local.model_template
  description = "SiteWise model template scaffold for OSD scenario assets and measurements."
}

output "site_asset_model_id" {
  value       = var.enable_sitewise_resources ? aws_iotsitewise_asset_model.site[0].id : null
  description = "Created SiteWise site model id when enabled."
}
