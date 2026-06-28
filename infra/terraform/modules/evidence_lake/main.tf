resource "aws_kms_key" "evidence" {
  count                   = var.create_kms_key ? 1 : 0
  description             = "KMS key for Areos evidence artifacts"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  tags                    = var.tags
}

resource "aws_kms_alias" "evidence" {
  count         = var.create_kms_key ? 1 : 0
  name          = "alias/${var.bucket_name}-evidence"
  target_key_id = aws_kms_key.evidence[0].key_id
}

resource "aws_s3_bucket" "evidence" {
  bucket = var.bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "evidence" {
  bucket = aws_s3_bucket.evidence.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "evidence" {
  bucket = aws_s3_bucket.evidence.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.create_kms_key ? "aws:kms" : "AES256"
      kms_master_key_id = var.create_kms_key ? aws_kms_key.evidence[0].arn : null
    }
  }
}

resource "aws_s3_bucket_public_access_block" "evidence" {
  bucket                  = aws_s3_bucket.evidence.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# NOTE: Object Lock can be enabled for immutable-style evidence retention,
# but must be configured at bucket creation time and aligned to customer policy.
