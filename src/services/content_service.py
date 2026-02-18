import httpx
import random
import re
import unicodedata
from datetime import datetime
from src.core.logger import logger
from src.core.config import settings

class ContentService:
    def __init__(self):
        self.base_url = "https://tr.wikipedia.org/api/rest_v1/feed/onthisday"
        self.turkish_keywords = [
            "türk", "türkiye", "osmanlı", "ottoman", "istanbul", "ankara", "atatürk", 
            "selçuklu", "kıbrıs", "akdeniz", "karadeniz", "mehmed", "süleyman"
        ]
        self.pattern = re.compile('|'.join(map(re.escape, self.turkish_keywords)), re.IGNORECASE)

    def _is_turkish(self, text: str) -> bool:
        """Checks if the text is related to Turkey."""
        # Normalize
        s = unicodedata.normalize('NFKC', text)
        s = s.replace('İ', 'i').replace('I', 'ı').lower()
        return bool(self.pattern.search(s))

    async def fetch_events(self, month: int, day: int) -> dict:
        """Fetches events from Wikipedia for the given date."""
        categories = ["selected", "events", "births", "deaths"]
        raw_items = []
        
        async with httpx.AsyncClient() as client:
            client.headers.update({'User-Agent': 'TarihBot/4.0 (Elite Edition)'})
            
            for cat in categories:
                url = f"{self.base_url}/{cat}/{month}/{day}"
                try:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        items = data.get(cat, [])
                        for item in items:
                            item['_category'] = cat
                            raw_items.append(item)
                except Exception as e:
                    logger.error(f"Failed to fetch {cat}: {e}")
                    
        return raw_items

    def select_best_event(self, items: list, used_texts: list) -> dict:
        """
        Selects the best event:
        1. Must not be in used_texts.
        2. Priority: Turkish Content > 'Selected' Category > High Source Count.
        """
        # Filter duplicates
        candidates = [i for i in items if i.get('text') not in used_texts]
        
        if not candidates:
            return None
            
        turkish_items = [i for i in candidates if self._is_turkish(i.get('text', ''))]
        
        if turkish_items:
            logger.info(f"Found {len(turkish_items)} Turkish events.")
            return random.choice(turkish_items)
            
        # Fallback: Important items
        important = [i for i in candidates if i.get('_category') == 'selected']
        if important:
             logger.info(f"Fallback to 'Selected' category ({len(important)} items).")
             return random.choice(important)
             
        logger.warning("No priority content found, choosing random.")
        return random.choice(candidates)
