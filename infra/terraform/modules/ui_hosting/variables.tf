variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "domain_name" {
  type    = string
  default = null
}

variable "tags" {
  type    = map(string)
  default = {}
}
