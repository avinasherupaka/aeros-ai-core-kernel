variable "environment" {
  type        = string
  description = "Environment name."
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days."
  default     = 30
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
