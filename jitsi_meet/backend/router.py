import uuid
import secrets
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from core.database import get_db_session, Album, Account
from api.auth import get_current_account_id
from api.galleries import AlbumResponse
from .models import JitsiRoom
from .schemas import JitsiRoomCreate, JitsiRoomResponse, JitsiRoomWithAlbumResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/meet", tags=["meet-extension"])
jitsi_meet_extension_router = router


async def get_current_account(account_id: str = Depends(get_current_account_id), db: AsyncSession = Depends(get_db_session)) -> Account:
    account = await db.get(Account, uuid.UUID(account_id))
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada.")
    return account


@router.post("/rooms", response_model=JitsiRoomResponse, summary="Crear sala de Jitsi Meet")
async def create_jitsi_room(
    room_data: JitsiRoomCreate,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db_session),
):
    if room_data.album_id is not None:
        album = await db.get(Album, room_data.album_id)
        if not album or album.account_id != current_account.id:
            raise HTTPException(status_code=404, detail="Álbum no encontrado o no autorizado.")

    # Generar nombre de sala único
    room_name = f"kognito-{secrets.token_urlsafe(12)}"
    existing = await db.execute(select(JitsiRoom).where(JitsiRoom.room_name == room_name))
    while existing.scalar_one_or_none():
        room_name = f"kognito-{secrets.token_urlsafe(12)}"
        existing = await db.execute(select(JitsiRoom).where(JitsiRoom.room_name == room_name))

    room = JitsiRoom(
        album_id=room_data.album_id,
        account_id=current_account.id,
        room_name=room_name,
        display_name=room_data.display_name,
        password=room_data.password,
        is_active=room_data.is_active,
    )
    db.add(room)
    await db.commit()
    return JitsiRoomResponse(
        id=room.id,
        album_id=room.album_id,
        account_id=room.account_id,
        room_name=room.room_name,
        display_name=room.display_name,
        has_password=bool(room.password),
        is_active=room.is_active,
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


@router.get("/rooms", response_model=List[JitsiRoomWithAlbumResponse], summary="Listar salas de Jitsi Meet")
async def list_jitsi_rooms(
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db_session),
):
    stmt = (
        select(JitsiRoom)
        .options(selectinload(JitsiRoom.album))
        .where(JitsiRoom.account_id == current_account.id)
        .order_by(JitsiRoom.created_at.desc())
    )
    result = await db.execute(stmt)
    rooms = result.scalars().all()
    response = []
    for room in rooms:
        room_resp = JitsiRoomWithAlbumResponse(
            id=room.id,
            album_id=room.album_id,
            account_id=room.account_id,
            room_name=room.room_name,
            display_name=room.display_name,
            has_password=bool(room.password),
            is_active=room.is_active,
            created_at=room.created_at,
            updated_at=room.updated_at,
            album=AlbumResponse(
                id=room.album.id,
                name=room.album.name,
                description=room.album.description,
                created_at=room.album.created_at,
                updated_at=room.album.updated_at,
            ) if room.album else None,
        )
        response.append(room_resp)
    return response


@router.get("/rooms/{room_id}", response_model=JitsiRoomWithAlbumResponse, summary="Obtener sala de Jitsi Meet")
async def get_jitsi_room(
    room_id: uuid.UUID,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db_session),
):
    room = await db.get(JitsiRoom, room_id)
    if not room or room.account_id != current_account.id:
        raise HTTPException(status_code=404, detail="Sala no encontrada.")

    return JitsiRoomWithAlbumResponse(
        id=room.id,
        album_id=room.album_id,
        account_id=room.account_id,
        room_name=room.room_name,
        display_name=room.display_name,
        has_password=bool(room.password),
        is_active=room.is_active,
        created_at=room.created_at,
        updated_at=room.updated_at,
        album=AlbumResponse(
            id=room.album.id,
            name=room.album.name,
            description=room.album.description,
            created_at=room.album.created_at,
            updated_at=room.album.updated_at,
        ) if room.album else None,
    )


@router.delete("/rooms/{room_id}", status_code=204, summary="Eliminar sala de Jitsi Meet")
async def delete_jitsi_room(
    room_id: uuid.UUID,
    current_account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db_session),
):
    room = await db.get(JitsiRoom, room_id)
    if not room or room.account_id != current_account.id:
        raise HTTPException(status_code=404, detail="Sala no encontrada.")

    await db.delete(room)
    await db.commit()
    return Response(status_code=204)
