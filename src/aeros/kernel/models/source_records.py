from pydantic import BaseModel


class SourceRecord(BaseModel):
    source_system: str
    record_type: str
    record_id: str
    summary: str
