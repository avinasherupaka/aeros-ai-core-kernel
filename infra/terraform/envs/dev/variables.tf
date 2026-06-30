variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment name."
}

variable "aws_region" {
  type        = string
  default     = "ap-south-1"
  description = "AWS region. ap-south-1 is recommended for India residency by default."
}

variable "tenant_id" {
  type        = string
  description = "Tenant identifier."
}

variable "site_id" {
  type        = string
  description = "Site identifier."
}

variable "topic_prefix" {
  type        = string
  default     = "areos"
  description = "IoT topic prefix."
}

variable "evidence_bucket_name" {
  type        = string
  description = "Unique S3 bucket name for evidence lake."
}

variable "log_retention_days" {
  type        = number
  default     = 30
  description = "CloudWatch log retention period."
}

variable "enable_sitewise_resources" {
  type        = bool
  default     = false
  description = "Set true only when ready to create SiteWise resources."
}

variable "enable_object_lock" {
  type        = bool
  default     = false
  description = "Enable S3 Object Lock for evidence lake bucket."
}

variable "enable_neptune" {
  type        = bool
  default     = false
  description = "Enable Neptune module resources."
}

variable "enable_lakehouse_catalog" {
  type        = bool
  default     = false
  description = "Enable Glue catalog and Athena workgroup resources."
}

variable "enable_workflow_runtime" {
  type        = bool
  default     = false
  description = "Enable Step Functions, Lambda IAM, and Bedrock IAM resources."
}

variable "vpc_subnet_ids" {
  type        = list(string)
  default     = []
  description = "Subnets for Neptune when enabled."
}

variable "vpc_security_group_ids" {
  type        = list(string)
  default     = []
  description = "Security groups for Neptune when enabled."
}

variable "github_oidc_role_name" {
  type        = string
  default     = "areos-github-actions-dev"
  description = "IAM role for GitHub Actions OIDC."
}

variable "github_allowed_subjects" {
  type        = list(string)
  description = "Allowed GitHub OIDC subjects."
  default = [
    "repo:aerup/aeros-ai-core-kernel:ref:refs/heads/main",
    "repo:aerup/aeros-ai-core-kernel:pull_request"
  ]
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Additional tags."
}
