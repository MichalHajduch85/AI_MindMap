import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from llama_mindmap_backend.extensions import db

class Node(db.Model):
    __tablename__ = 'nodes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('nodes.id'), nullable=True)
    content = Column(Text, nullable=False)
    level = Column(Integer, nullable=False, default=0)
    steps = Column(JSONB, nullable=True)
    analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship('Node', backref=db.backref('parent', remote_side=[id]), lazy=True)
