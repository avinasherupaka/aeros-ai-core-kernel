data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  lambda_name = "${var.function_name}-${var.environment}"
  tags = merge(var.tags, {
    Name        = local.lambda_name
    Environment = var.environment
    Service     = "mcp-assistant"
  })
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "this" {
  name               = "${local.lambda_name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = local.tags
}

data "aws_iam_policy_document" "access" {
  statement {
    sid = "CloudWatchLogs"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    sid = "BedrockAccess"

    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
      "bedrock:Retrieve",
      "bedrock:RetrieveAndGenerate"
    ]

    resources = ["*"]
  }

  statement {
    sid = "DynamoDBReadOnly"

    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]

    resources = ["*"]
  }

  statement {
    sid = "S3ReadOnly"

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:ListBucket"
    ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "this" {
  name   = "${local.lambda_name}-policy"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.access.json
}

resource "aws_lambda_function" "this" {
  function_name    = local.lambda_name
  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)
  handler          = "app.handler"
  role             = aws_iam_role.this.arn
  runtime          = "python3.11"
  timeout          = 30
  memory_size      = 512

  environment {
    variables = {
      AREOS_MODE        = var.environment
      BEDROCK_MODEL_ID  = var.bedrock_model_id
      KNOWLEDGE_BASE_ID = var.knowledge_base_id
    }
  }

  tags = local.tags
}

resource "aws_lambda_permission" "apigateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*/*/*/*"
}
