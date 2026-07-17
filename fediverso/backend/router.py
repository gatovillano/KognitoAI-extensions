import logging
import httpx
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Dict, Any

from core.database import get_db, Account
from core.repositories.secret_repository import SecretRepository
from core.llm_manager import get_llm_for_user
from utils.security import get_current_account_id

from extensions.fediverso.backend.models import FediversoAccount
from extensions.fediverso.backend.schemas import (
    RegisterInstanceRequest, RegisterInstanceResponse, CallbackRequest,
    FediversoAccountSchema, TootRequest, SummarizeRequest, ComposeRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/fediverso", tags=["fediverso"])

REDIRECT_URI = "http://localhost:3000/fediverso"

def _sanitize_instance_url(url: str) -> str:
    url = url.strip().lower()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
    return url.rstrip("/")

@router.post("/register-instance", response_model=RegisterInstanceResponse)
async def register_instance(
    req: RegisterInstanceRequest,
    db: AsyncSession = Depends(get_db),
    current_account_id: str = Depends(get_current_account_id)
):
    instance = _sanitize_instance_url(req.instance_url)
    account_uuid = uuid.UUID(current_account_id)
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{instance}/api/v1/apps",
                data={
                    "client_name": "KognitoAI Fediverso Client",
                    "redirect_uris": REDIRECT_URI,
                    "scopes": "read write",
                    "website": "https://github.com/gatovillano/KognitoAI"
                },
                timeout=10.0
            )
            resp.raise_for_status()
            data = resp.json()
            
            client_id = data["client_id"]
            client_secret = data["client_secret"]
            
            # Guardar el client_secret de forma segura
            secret_repo = SecretRepository(db)
            await secret_repo.set_secret(
                account_uuid,
                f"FEDIVERSO_{current_account_id}_{instance}_CLIENT_SECRET",
                client_secret,
                f"Client secret para instancia {instance}"
            )
            
            authorize_url = f"{instance}/oauth/authorize?client_id={client_id}&redirect_uri={REDIRECT_URI}&response_type=code&scope=read+write"
            
            return RegisterInstanceResponse(
                instance_url=instance,
                client_id=client_id,
                authorize_url=authorize_url
            )
    except Exception as e:
        logger.error(f"Error al registrar app en {instance}: {e}")
        raise HTTPException(status_code=400, detail=f"No se pudo registrar la aplicación en {instance}: {str(e)}")

@router.post("/callback", response_model=FediversoAccountSchema)
async def callback(
    req: CallbackRequest,
    db: AsyncSession = Depends(get_db),
    current_account_id: str = Depends(get_current_account_id)
):
    instance = _sanitize_instance_url(req.instance_url)
    account_uuid = uuid.UUID(current_account_id)
    secret_repo = SecretRepository(db)
    
    # Obtener client_secret guardado
    client_secret = await secret_repo.get_decrypted_secret(
        account_uuid,
        f"FEDIVERSO_{current_account_id}_{instance}_CLIENT_SECRET"
    )
    if not client_secret:
        raise HTTPException(status_code=400, detail="Falta el client secret para esta instancia")

    try:
        # 1. Intercambiar código por token de acceso
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                f"{instance}/oauth/token",
                data={
                    "client_id": req.client_id,
                    "client_secret": client_secret,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code",
                    "code": req.code,
                    "scope": "read write"
                },
                timeout=10.0
            )
            token_resp.raise_for_status()
            token_data = token_resp.json()
            access_token = token_data["access_token"]
            
            # Guardar el access token de forma segura
            await secret_repo.set_secret(
                account_uuid,
                f"FEDIVERSO_{current_account_id}_{instance}_ACCESS_TOKEN",
                access_token,
                f"Access token para instancia {instance}"
            )
            
            # 2. Verificar credenciales del perfil en Mastodon
            profile_resp = await client.get(
                f"{instance}/api/v1/accounts/verify_credentials",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            profile_resp.raise_for_status()
            profile_data = profile_resp.json()
            
            username = profile_data["username"]
            display_name = profile_data.get("display_name")
            avatar_url = profile_data.get("avatar")
            
            # 3. Guardar o actualizar registro en base de datos
            stmt = select(FediversoAccount).where(
                FediversoAccount.account_id == account_uuid,
                FediversoAccount.instance_url == instance,
                FediversoAccount.username == username
            )
            result = await db.execute(stmt)
            existing = result.scalars().first()
            
            if existing:
                existing.client_id = req.client_id
                existing.display_name = display_name
                existing.avatar_url = avatar_url
                existing.is_active = True
                db_acc = existing
            else:
                db_acc = FediversoAccount(
                    account_id=account_uuid,
                    instance_url=instance,
                    client_id=req.client_id,
                    username=username,
                    display_name=display_name,
                    avatar_url=avatar_url,
                    is_active=True
                )
                db.add(db_acc)
            
            await db.commit()
            await db.refresh(db_acc)
            return db_acc
            
    except Exception as e:
        logger.error(f"Error en OAuth callback para {instance}: {e}")
        raise HTTPException(status_code=400, detail=f"Fallo en la autenticación con Mastodon: {str(e)}")

@router.get("/accounts", response_model=List[FediversoAccountSchema])
async def get_accounts(
    db: AsyncSession = Depends(get_db),
    current_account_id: str = Depends(get_current_account_id)
):
    stmt = select(FediversoAccount).where(
        FediversoAccount.account_id == uuid.UUID(current_account_id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get("/feed")
async def get_feed(
    account_id: uuid.UUID,
    feed_type: str = "home",
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_account_id: str = Depends(get_current_account_id)
):
    account_uuid = uuid.UUID(current_account_id)
    
    # Buscar cuenta federada
    stmt = select(FediversoAccount).where(
        FediversoAccount.id == account_id,
        FediversoAccount.account_id == account_uuid
    )
    result = await db.execute(stmt)
    fed_acc = result.scalars().first()
    if not fed_acc:
        raise HTTPException(status_code=404, detail="Cuenta del Fediverso no encontrada")
        
    secret_repo = SecretRepository(db)
    access_token = await secret_repo.get_decrypted_secret(
        account_uuid,
        f"FEDIVERSO_{current_account_id}_{fed_acc.instance_url}_ACCESS_TOKEN"
    )
    if not access_token:
        raise HTTPException(status_code=401, detail="No se encontró token de acceso para la cuenta")

    url_map = {
        "home": f"{fed_acc.instance_url}/api/v1/timelines/home",
        "local": f"{fed_acc.instance_url}/api/v1/timelines/public?local=true",
        "public": f"{fed_acc.instance_url}/api/v1/timelines/public?local=false",
        "notifications": f"{fed_acc.instance_url}/api/v1/notifications"
    }
    
    target_url = url_map.get(feed_type, url_map["home"])
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{target_url}&limit={limit}" if "?" in target_url else f"{target_url}?limit={limit}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Error al traer feed {feed_type} de {fed_acc.instance_url}: {e}")
        raise HTTPException(status_code=400, detail=f"Error al obtener feed: {str(e)}")

@router.post("/toot")
async def post_toot(
    req: TootRequest,
    db: AsyncSession = Depends(get_db),
    current_account_id: str = Depends(get_current_account_id)
):
    account_uuid = uuid.UUID(current_account_id)
    
    stmt = select(FediversoAccount).where(
        FediversoAccount.id == req.account_id,
        FediversoAccount.account_id == account_uuid
    )
    result = await db.execute(stmt)
    fed_acc = result.scalars().first()
    if not fed_acc:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        
    secret_repo = SecretRepository(db)
    access_token = await secret_repo.get_decrypted_secret(
        account_uuid,
        f"FEDIVERSO_{current_account_id}_{fed_acc.instance_url}_ACCESS_TOKEN"
    )
    
    try:
        async with httpx.AsyncClient() as client:
            payload = {"status": req.status}
            if req.in_reply_to_id:
                payload["in_reply_to_id"] = req.in_reply_to_id
                
            resp = await client.post(
                f"{fed_acc.instance_url}/api/v1/statuses",
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
                timeout=10.0
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Error al publicar toot: {e}")
        raise HTTPException(status_code=400, detail=f"No se pudo publicar el toot: {str(e)}")

@router.post("/ai/summarize-thread")
async def ai_summarize_thread(
    req: SummarizeRequest,
    db: AsyncSession = Depends(get_db),
    current_account_id: str = Depends(get_current_account_id)
):
    account_uuid = uuid.UUID(current_account_id)
    
    stmt = select(FediversoAccount).where(
        FediversoAccount.id == req.account_id,
        FediversoAccount.account_id == account_uuid
    )
    result = await db.execute(stmt)
    fed_acc = result.scalars().first()
    if not fed_acc:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
        
    secret_repo = SecretRepository(db)
    access_token = await secret_repo.get_decrypted_secret(
        account_uuid,
        f"FEDIVERSO_{current_account_id}_{fed_acc.instance_url}_ACCESS_TOKEN"
    )
    
    try:
        # 1. Recuperar contexto del hilo de discusión
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{fed_acc.instance_url}/api/v1/statuses/{req.status_id}/context",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            resp.raise_for_status()
            context_data = resp.json()
            
            # Obtener también el toot original
            orig_resp = await client.get(
                f"{fed_acc.instance_url}/api/v1/statuses/{req.status_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            orig_resp.raise_for_status()
            orig_toot = orig_resp.json()
            
        # Formatear el hilo de conversación
        thread_text = f"Post Inicial de {orig_toot['account']['acct']}: \"{orig_toot['content']}\"\n\n"
        
        # Agregar ancestros y descendientes
        for t in context_data.get("ancestors", []):
            thread_text += f"- Respondiendo a {t['account']['acct']}: \"{t['content']}\"\n"
        for t in context_data.get("descendants", []):
            thread_text += f"- Réplica de {t['account']['acct']}: \"{t['content']}\"\n"

        # 2. Llamar al LLM de KognitoAI
        llm = await get_llm_for_user(current_account_id, purpose="main")
        if not llm:
            raise HTTPException(status_code=500, detail="No se pudo configurar el servicio LLM")
            
        prompt = (
            "Eres un asistente de IA integrado en KognitoAI. Analiza y resume el siguiente hilo del Fediverso. "
            "Genera un resumen ejecutivo breve, puntos clave de la discusión y el sentimiento predominante.\n\n"
            f"Hilo de conversación:\n{thread_text}"
        )
        
        # Invocar al LLM
        response = await llm.ainvoke(prompt)
        return {"summary": response.content}
        
    except Exception as e:
        logger.error(f"Error al resumir hilo: {e}")
        raise HTTPException(status_code=400, detail=f"No se pudo analizar el hilo con la IA: {str(e)}")

@router.post("/ai/compose")
async def ai_compose(
    req: ComposeRequest,
    current_account_id: str = Depends(get_current_account_id)
):
    try:
        llm = await get_llm_for_user(current_account_id, purpose="main")
        if not llm:
            raise HTTPException(status_code=500, detail="No se pudo configurar el servicio LLM")
            
        prompt = (
            "Eres el redactor creativo de KognitoAI para el Fediverso. Tu tarea es generar o refinar un post "
            "interesante respetando las siguientes reglas:\n"
            "- Longitud estricta menor a 500 caracteres.\n"
            "- Tono cercano y natural (evita lenguaje de marketing agresivo).\n"
            "- Incluye 2 o 3 hashtags relevantes al final del toot.\n\n"
            f"Petición del usuario: {req.prompt}\n"
        )
        if req.context:
            prompt += f"Contexto de la conversación (si estás respondiendo a un post): {req.context}\n"
            
        response = await llm.ainvoke(prompt)
        return {"draft": response.content}
        
    except Exception as e:
        logger.error(f"Error en composición de IA: {e}")
        raise HTTPException(status_code=400, detail=f"Fallo al redactar con IA: {str(e)}")
