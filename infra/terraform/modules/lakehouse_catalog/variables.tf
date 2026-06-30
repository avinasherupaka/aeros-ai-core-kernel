variable "database_name" {
  type        = string
  description = "Glue database name for bronze/silver/gold tables."
}

variable "athena_workgroup" {
  type        = string
  description = "Athena workgroup name."
}

variable "results_output_location" {
  type        = string
  description = "S3 output location for Athena query results."
}

variable "enabled" {
  type        = bool
  description = "Enable Glue/Athena resources."
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
