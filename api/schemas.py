from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from models.models import ExecutionStatus

class RunRequest(BaseModel):
    source : str

class ScriptCreate(BaseModel):
    name : str
    source : str    

class ScriptResponse(BaseModel):
    id : UUID
    name : str
    source : str
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)

class ExecutionResponse(BaseModel):
    id : UUID
    script_id : UUID
    status : ExecutionStatus
    started_at : datetime | None
    finished_at : datetime | None
    error_message : str | None

    model_config = ConfigDict(from_attributes=True)


class ExecutionLogResponse(BaseModel):
    id: UUID
    execution_id: UUID

    step: str
    event_type: str
    name: str | None

    message: str
    status: str

    line: int | None
    col: int | None

    args: dict | None
    result_summary: dict | None

    duration_ms: int | None
    timestamp: datetime

    sequence: int

    model_config = ConfigDict(from_attributes=True)