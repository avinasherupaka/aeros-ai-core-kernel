variable "site_name" {
  type        = string
  description = "Site name used for model template naming."
}

variable "enable_sitewise_resources" {
  type        = bool
  description = "Enable actual SiteWise resources. Off by default to keep cost/scope controlled."
  default     = false
}
