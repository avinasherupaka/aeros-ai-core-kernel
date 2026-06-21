from pydantic import BaseModel


class Settings(BaseModel):
    env: str = "dev"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    evidence_root: str = "artifacts/evidence"
    aws_region: str = "ap-south-1"
