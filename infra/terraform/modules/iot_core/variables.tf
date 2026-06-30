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
  description = "Top-level IoT topic prefix."
  default     = "areos"
}

variable "thing_type_name" {
  type        = string
  description = "IoT thing type name for site gateways."
  default     = "areos-site-gateway"
}

variable "client_id_prefix" {
  type        = string
  description = "Allowed MQTT client ID prefix."
  default     = "areos-gw"
}

variable "cloudwatch_log_group_name" {
  type        = string
  description = "CloudWatch log group name for IoT topic rule action."
}

variable "cloudwatch_log_group_arn" {
  type        = string
  description = "CloudWatch log group ARN for IoT topic rule IAM policy."
}
