variable "app_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "image_uri" {
  type = string
}

variable "port" {
  type    = number
  default = 8000
}

variable "cpu" {
  type    = string
  default = "1 vCPU"
}

variable "memory" {
  type    = string
  default = "2 GB"
}

variable "min_instances" {
  type    = number
  default = 1
}

variable "max_instances" {
  type    = number
  default = 2
}

variable "region" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
