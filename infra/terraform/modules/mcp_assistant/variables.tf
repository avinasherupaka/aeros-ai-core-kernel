variable "function_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "lambda_zip_path" {
  type = string
}

variable "bedrock_model_id" {
  type = string
}

variable "knowledge_base_id" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
