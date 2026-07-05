locals {
  service_name = "${var.app_name}-${var.environment}-control-plane-api"
  tags = merge(var.tags, {
    Name        = local.service_name
    Environment = var.environment
    Service     = "control-plane-api"
    Region      = var.region
  })
}

data "aws_iam_policy_document" "apprunner_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["build.apprunner.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "apprunner_access" {
  name               = "${local.service_name}-access"
  assume_role_policy = data.aws_iam_policy_document.apprunner_assume_role.json
  tags               = local.tags
}

resource "aws_iam_role_policy_attachment" "ecr_access" {
  role       = aws_iam_role.apprunner_access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

resource "aws_apprunner_auto_scaling_configuration_version" "this" {
  auto_scaling_configuration_name = "${local.service_name}-scaling"
  min_size                        = var.min_instances
  max_size                        = var.max_instances
  tags                            = local.tags
}

resource "aws_apprunner_service" "this" {
  service_name                   = local.service_name
  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.this.arn

  source_configuration {
    auto_deployments_enabled = false

    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_access.arn
    }

    image_repository {
      image_identifier      = var.image_uri
      image_repository_type = "ECR"

      image_configuration {
        port = tostring(var.port)

        runtime_environment_variables = {
          AREOS_MODE = var.environment
          LOG_LEVEL  = "INFO"
        }
      }
    }
  }

  instance_configuration {
    cpu    = var.cpu
    memory = var.memory
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  tags = local.tags
}
