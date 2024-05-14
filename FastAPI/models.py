from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Float


class TodoMeow(Base):
    __tablename__ = 'todo'

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    completed = Column(Boolean)
    isEditing = Column(Boolean)