from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from opendiscourse.core.config import settings

class Base(DeclarativeBase):
    pass

class Politician(Base):
    """
    Master Identity Layer for Politicians.
    This links all disparate data sources (OpenStates, Congress, FEC) 
    to a single UUID-based entity.
    """
    __tablename__ = "politicians"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Core Identity
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_party: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    current_state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    
    # External IDs mapping (The most important part for Entity Resolution)
    bioguide_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    openstates_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    fec_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    govtrack_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    opensecrets_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)

    # General metadata
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Politician(id={self.id}, name='{self.first_name} {self.last_name}')>"

# Setup Database connection using the core configuration
DATABASE_URL = settings.database_url

def get_engine():
    return create_engine(DATABASE_URL)

def get_session():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def init_db():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
