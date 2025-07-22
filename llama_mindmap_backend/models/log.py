import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, String, DateTime, ForeignKey
from llama_mindmap_backend.extensions import db

class Log(db.Model):
    __tablename__ = 'logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSONB, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
