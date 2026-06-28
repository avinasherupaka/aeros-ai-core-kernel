# 02 AWS Account Prerequisites

## Tooling (macOS)

```bash
brew install awscli terraform
aws --version
terraform version
```

## AWS authentication

Preferred:
- AWS IAM Identity Center (SSO) for humans.
- GitHub Actions OIDC for CI/CD (no long-lived AWS keys).

Example SSO profile setup:

```bash
aws configure sso
aws sso login --profile areos-dev
aws sts get-caller-identity --profile areos-dev
```

## Account baseline expectations

- Dedicated dev account/sub-account.
- CloudTrail enabled by platform policy.
- Budget alerts enabled.
- Region target: `ap-south-1` (configurable).
