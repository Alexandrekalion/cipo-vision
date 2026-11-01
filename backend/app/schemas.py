from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DevLogin(BaseModel): username: str
class Token(BaseModel): access_token: str; token_type: str = "bearer"
class RequestCreate(BaseModel):
    employee: str; occurrence_type: str; occurred_at: datetime; location: str; camera_area: str | None = None; reason: str; manager_id: int
class Decision(BaseModel):
    decision: str; manager_signature: bool = False; witness_id: int | None = None; rh_required: bool | None = None; reason: str | None = None
class RequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int; protocol: str; status: str; employee: str; requester_id: int; manager_id: int; witness_id: int | None; rh_required: bool | None
