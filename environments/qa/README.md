# QA environment

QA mirrors the Local parity matrix while using isolated VPCs and the near-real-time
digital-twin strategy in `data_strategy.json`. It is the release-candidate gate:

```bash
terraform -chdir=environments/qa init
terraform -chdir=environments/qa validate
terraform -chdir=environments/qa plan
```

Run the simulator with `AREOS_SIMULATOR_TARGET_URL` set to the approved ingestion
endpoint, then run `scripts/validate_deployment.py --environment qa`.
