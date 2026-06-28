output "bucket_name" {
  value       = aws_s3_bucket.evidence.bucket
  description = "Evidence S3 bucket name."
}

output "bucket_arn" {
  value       = aws_s3_bucket.evidence.arn
  description = "Evidence S3 bucket ARN."
}

output "kms_key_arn" {
  value       = var.create_kms_key ? aws_kms_key.evidence[0].arn : null
  description = "KMS key ARN when create_kms_key is true."
}
