# Tenant fleet — one isolated VPC per tenant. Non-overlapping CIDRs.
# Onboarding a new facility = add an entry here + a tenants/<id>/ config folder.
tenants = {
  pharma_co_a = {
    vpc_cidr           = "10.10.0.0/16"
    desired_task_count = 1
  }
  pharma_co_b = {
    vpc_cidr           = "10.20.0.0/16"
    desired_task_count = 1
  }
}
