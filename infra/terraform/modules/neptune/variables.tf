variable "name" {
  type        = string
  description = "Neptune cluster name prefix."
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnets for Neptune subnet group."
  default     = []
}

variable "security_group_ids" {
  type        = list(string)
  description = "Security groups for Neptune."
  default     = []
}

variable "engine_version" {
  type        = string
  description = "Neptune engine version."
  default     = "1.3.2.0"
}

variable "enabled" {
  type        = bool
  description = "Enable Neptune resources."
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
