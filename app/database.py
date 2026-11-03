import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./interviews.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InterviewRecord(Base):
    __tablename__ = "interviews"

    interview_id = Column(String(36), primary_key=True, index=True)
    role = Column(String(100), nullable=False)
    experience_level = Column(String(50), nullable=False)
    interview_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    total_questions = Column(Integer, default=5)
    current_question_number = Column(Integer, default=0)
    status = Column(String(50), default="created")
    overall_score = Column(Float, nullable=True)
    needs_human_review = Column(Integer, default=0)  # 0 or 1
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # JSON-serialized state caches for LangGraph history and reports
    current_question_json = Column(Text, nullable=True)
    current_evaluation_json = Column(Text, nullable=True)
    history_json = Column(Text, default="[]")
    final_report_json = Column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_id": self.interview_id,
            "role": self.role,
            "experience_level": self.experience_level,
            "interview_type": self.interview_type,
            "difficulty": self.difficulty,
            "total_questions": self.total_questions,
            "current_question_number": self.current_question_number,
            "status": self.status,
            "overall_score": self.overall_score,
            "needs_human_review": bool(self.needs_human_review),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "current_question": json.loads(self.current_question_json) if self.current_question_json else None,
            "current_evaluation": json.loads(self.current_evaluation_json) if self.current_evaluation_json else None,
            "history": json.loads(self.history_json) if self.history_json else [],
            "final_report": json.loads(self.final_report_json) if self.final_report_json else None,
        }


def init_db():
    """Initializes SQLite database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")
