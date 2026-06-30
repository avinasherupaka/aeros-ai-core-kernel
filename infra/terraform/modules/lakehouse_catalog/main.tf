locals {
  create = var.enabled
}

resource "aws_glue_catalog_database" "this" {
  count = local.create ? 1 : 0
  name  = var.database_name
}

resource "aws_athena_workgroup" "this" {
  count = local.create ? 1 : 0
  name  = var.athena_workgroup

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true
    result_configuration {
      output_location = var.results_output_location
    }
  }

  tags = var.tags
}
