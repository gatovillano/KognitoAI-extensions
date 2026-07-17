import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base

class FediversoAccount(Base):
    """
    Representa una cuenta del Fediverso vinculada a una cuenta universal de KognitoAI.
    """
    __tablename__ = "fediverso_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    instance_url = Column(String(255), nullable=False, comment="URL de la instancia (ej: https://mastodon.social)")
    client_id = Column(String(255), nullable=False, comment="Client ID registrado en la instancia")
    username = Column(String(255), nullable=False, comment="Nombre de usuario en Mastodon")
    display_name = Column(String(255), nullable=True)
    avatar_url = Column(String(1024), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
