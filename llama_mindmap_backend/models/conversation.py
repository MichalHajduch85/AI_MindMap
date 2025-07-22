import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from llama_mindmap_backend.extensions import db

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    root_topic = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    nodes = relationship('Node', backref='conversation', lazy=True)
