from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

class PostHistory(Base):
    __tablename__ = "post_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content_text: Mapped[str] = mapped_column(nullable=False) # The raw text of the event
    posted_at: Mapped[datetime] = mapped_column(server_default=func.now())
    source_category: Mapped[str] = mapped_column(nullable=True) # events, births, deaths
    tweet_id: Mapped[str] = mapped_column(nullable=True) # ID of the first tweet in chain
    
    def __repr__(self) -> str:
        return f"<PostHistory(id={self.id}, text='{self.content_text[:20]}...', posted_at={self.posted_at})>"
