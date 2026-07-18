from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.data.models import PostHistory
from datetime import datetime
from typing import List

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

    async def exists(self, text: str) -> bool:
        """
        Checks if the text has EVER been posted (all-time dedup).
        Prevents the same event from being posted in different years.
        """
        stmt = select(PostHistory).where(PostHistory.content_text == text)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_todays_posts(self) -> List[str]:
        """Returns the list of content texts posted TODAY."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stmt = select(PostHistory).where(PostHistory.posted_at >= today_start)
        result = await self.session.execute(stmt)
        entries = result.scalars().all()
        return [entry.content_text for entry in entries]

    async def get_todays_post_count(self) -> int:
        """Returns the count of posts made today."""
        posts = await self.get_todays_posts()
        return len(posts)
