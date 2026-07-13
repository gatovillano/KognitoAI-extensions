import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from api.galleries import AlbumResponse


class JitsiRoomCreate(BaseModel):
    album_id: Optional[uuid.UUID] = Field(None, description="ID del álbum asociado a la sala.")
    display_name: str = Field(..., max_length=255, description="Título o nombre visible de la sala.")
    password: Optional[str] = Field(None, min_length=4, max_length=255, description="Contraseña opcional para la sala.")
    is_active: bool = Field(True, description="Indica si la sala está activa.")


class JitsiRoomResponse(BaseModel):
    id: uuid.UUID
    album_id: Optional[uuid.UUID] = None
    account_id: uuid.UUID
    room_name: str
    display_name: Optional[str]
    has_password: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JitsiRoomWithAlbumResponse(JitsiRoomResponse):
    album: Optional[AlbumResponse] = None

    class Config:
        from_attributes = True
