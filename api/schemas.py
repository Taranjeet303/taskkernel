from pydantic import BaseModel

class RunRequest(BaseModel):
    source : str