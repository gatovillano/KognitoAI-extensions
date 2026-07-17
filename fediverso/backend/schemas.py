from pydantic import BaseModel
from typing import Optional, List
import uuid

class RegisterInstanceRequest(BaseModel):
    instance_url: str

class RegisterInstanceResponse(BaseModel):
    instance_url: str
    client_id: str
    authorize_url: str

class CallbackRequest(BaseModel):
    instance_url: str
    client_id: str
    code: str

class FediversoAccountSchema(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    instance_url: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class TootRequest(BaseModel):
    account_id: uuid.UUID
    status: str
    in_reply_to_id: Optional[str] = None

class SummarizeRequest(BaseModel):
    account_id: uuid.UUID
    status_id: str

class ComposeRequest(BaseModel):
    prompt: str
    context: Optional[str] = None
