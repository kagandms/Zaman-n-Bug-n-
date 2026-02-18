from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.data.models import PostHistory
from datetime import datetime, timedelta

class HistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_entry(self, text: str, category: str = None, tweet_id: str = None):
        """Adds a new entry to the history."""
        new_entry = PostHistory(
            content_text=text,
            source_category=category,
            tweet_id=tweet_id
        )
        self.session.add(new_entry)
        await self.session.commit()

    async def exists(self, text: str, days_lookback: int = 365) -> bool:
        """
        Checks if the text has been posted recently.
        We check a large window (e.g., 1 year) to avoid repetition.
        """
        stmt = select(PostHistory).where(PostHistory.content_text == text)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_todays_posts(self) -> int:
        """Returns the count of posts made today."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stmt = select(PostHistory).where(PostHistory.posted_at >= today_start)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
