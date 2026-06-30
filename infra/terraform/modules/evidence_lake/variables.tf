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

variable "enable_object_lock" {
  type        = bool
  description = "Enable S3 Object Lock at bucket creation time."
  default     = false
}

variable "object_lock_retention_days" {
  type        = number
  description = "Default governance mode retention days when Object Lock is enabled."
  default     = 30
}
