from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text

from .database import Base


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    specialty = Column(String(255))
    institution = Column(String(255))


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), index=True)
    interaction_type = Column(String(100))
    date = Column(String(50))
    time = Column(String(50))
    attendees = Column(Text)
    topics_discussed = Column(Text)
    materials_shared = Column(JSON, default=list)
    samples_distributed = Column(JSON, default=list)
    sentiment = Column(String(50))
    outcomes = Column(Text)
    follow_up_date = Column(String(50))
    follow_up_actions = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
