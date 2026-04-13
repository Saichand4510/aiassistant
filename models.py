from sqlalchemy import Column, Integer, String, Text, ForeignKey
from db import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    transcript = Column(Text)
    summary = Column(Text)


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    task = Column(Text)
    assignee = Column(String)
    deadline = Column(String)
    status = Column(String, default="pending")