variable "name_prefix" {
  type        = string
  description = "Prefix for workflow runtime resources."
}

variable "enabled" {
  type        = bool
  description = "Enable workflow runtime resources."
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
