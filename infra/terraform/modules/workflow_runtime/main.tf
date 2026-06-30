locals {
  create = var.enabled
}

resource "aws_iam_role" "lambda_execution" {
  count = local.create ? 1 : 0
  name  = "${var.name_prefix}-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  count      = local.create ? 1 : 0
  role       = aws_iam_role.lambda_execution[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "bedrock_runtime" {
  count = local.create ? 1 : 0
  name  = "${var.name_prefix}-bedrock-runtime"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "bedrock_invoke" {
  count = local.create ? 1 : 0
  name  = "allow-bedrock-runtime"
  role  = aws_iam_role.bedrock_runtime[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["bedrock:InvokeModel", "bedrock:ApplyGuardrail"]
      Resource = "*"
    }]
  })
}

resource "aws_iam_role" "step_functions" {
  count = local.create ? 1 : 0
  name  = "${var.name_prefix}-sfn"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "states.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
  tags = var.tags
}

resource "aws_iam_role_policy" "step_functions" {
  count = local.create ? 1 : 0
  name  = "allow-pass-through"
  role  = aws_iam_role.step_functions[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["lambda:InvokeFunction"]
      Resource = "*"
    }]
  })
}

resource "aws_sfn_state_machine" "assurance" {
  count    = local.create ? 1 : 0
  name     = "${var.name_prefix}-assurance"
  role_arn = aws_iam_role.step_functions[0].arn
  definition = jsonencode({
    Comment = "Areos assurance workflow scaffold"
    StartAt = "Pass"
    States = {
      Pass = {
        Type = "Pass"
        End  = true
      }
    }
  })
  tags = var.tags
}
