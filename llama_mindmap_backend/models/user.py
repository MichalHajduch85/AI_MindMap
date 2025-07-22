import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from llama_mindmap_backend.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    profile_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship('Conversation', backref='user', lazy=True)
    logs = relationship('Log', backref='user', lazy=True)
