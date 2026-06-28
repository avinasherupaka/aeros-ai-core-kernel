variable "role_name" {
  type        = string
  description = "IAM role name for GitHub Actions OIDC."
}

variable "allowed_subjects" {
  type        = list(string)
  description = "Allowed GitHub OIDC subjects, e.g. repo:aerup/aeros-ai-core-kernel:ref:refs/heads/main"
}

variable "inline_policy_json" {
  type        = string
  description = "Least-privilege IAM policy JSON attached to the role."
}

variable "tags" {
  type        = map(string)
  description = "Resource tags."
  default     = {}
}
