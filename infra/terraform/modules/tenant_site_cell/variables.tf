variable "environment" {
  type        = string
  description = "Environment name."
}

variable "tenant_id" {
  type        = string
  description = "Tenant identifier."
}

variable "site_id" {
  type        = string
  description = "Site identifier."
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch retention period."
  default     = 30
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
