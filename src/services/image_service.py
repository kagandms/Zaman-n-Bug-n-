import httpx
import os
from src.core.config import settings
from src.core.logger import logger

class ImageService:
    def __init__(self):
        self.max_size = 5 * 1024 * 1024 # 5MB

    async def download_image(self, url: str, filename: str = "temp_image.jpg") -> str:
        """Downloads an image from URL."""
        headers = {'User-Agent': f'{settings.APP_NAME} Bot'}
        
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream("GET", url, headers=headers, timeout=20.0) as resp:
                    if resp.status_code != 200:
                        logger.warning(f"Image download failed: {resp.status_code}")
                        return None
                        
                    with open(filename, "wb") as f:
                        total_downloaded = 0
                        async for chunk in resp.aiter_bytes():
                            f.write(chunk)
                            total_downloaded += len(chunk)
                            if total_downloaded > self.max_size:
                                logger.warning("Image too large, aborting.")
                                return None
                                
                return filename
            except Exception as e:
                logger.error(f"Image download error: {e}")
                return None

    def cleanup(self, filename: str):
        """Removes the temporary file."""
        if os.path.exists(filename):
            os.remove(filename)
            logger.debug(f"Cleaned up {filename}")
