# This file defines the database models for the learning assistant application.

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    feedback = Column(String, nullable=False)

# Create the engine and session factory
# For a file-based SQLite, you could use "sqlite:///database.db"
engine = create_engine("sqlite:///./learning_assistant.db", echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
