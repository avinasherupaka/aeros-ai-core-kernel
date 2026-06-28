variable "bucket_name" {
  type        = string
  description = "S3 bucket name for evidence artifacts."
}

variable "create_kms_key" {
  type        = bool
  description = "Whether to create a dedicated KMS key for evidence bucket encryption."
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
