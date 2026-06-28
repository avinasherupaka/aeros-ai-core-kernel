# 05 IoT Core Publish Test

After deploying IoT scaffolding:

1. Provision certificate/key outside Terraform per security policy.
2. Attach IoT policy to certificate.
3. Publish to tenant/site scoped topic:

```text
areos/<tenant_id>/<site_id>/utility/compression_room/ahu_03/relative_humidity
```

4. Confirm message arrival in CloudWatch IoT log group.

Use only non-production simulated telemetry during bootstrap.
