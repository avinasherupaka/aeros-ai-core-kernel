output "cluster_endpoint" {
  value       = local.create ? aws_neptune_cluster.this[0].endpoint : null
  description = "Neptune cluster endpoint."
}

output "cluster_arn" {
  value       = local.create ? aws_neptune_cluster.this[0].arn : null
  description = "Neptune cluster ARN."
}
