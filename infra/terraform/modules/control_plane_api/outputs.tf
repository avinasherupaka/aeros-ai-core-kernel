output "service_arn" {
  value = aws_apprunner_service.this.arn
}

output "service_url" {
  value = aws_apprunner_service.this.service_url
}

output "service_id" {
  value = aws_apprunner_service.this.service_id
}
