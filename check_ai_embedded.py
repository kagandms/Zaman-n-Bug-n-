import asyncio
import os

os.environ["API_KEY"] = "mock"
os.environ["API_SECRET"] = "mock"
os.environ["ACCESS_TOKEN"] = "mock"
os.environ["ACCESS_TOKEN_SECRET"] = "mock"

from dotenv import load_dotenv

# Ensure .env is loaded before importing project modules that might depend on it immediately
load_dotenv()

from src.services.ai_service import AIService
from src.core.logger import logger

async def main():
    logger.info("Starting Embedded AI Check...")
    try:
        ai = AIService()
        
        event_text = ("Galileo Galilei, Dünya'nın Güneş etrafında döndüğünü savunduğu "
                      "için Engizisyon mahkemesince yargılandı ve ömür boyu ev hapsine çarptırıldı.")
        date_str = "22 Haziran"
        year_str = "1633"
        
        logger.info("Sending historical event to AI Service...")
        
        tweets, poll_options, image_prompt = await ai.rewrite_event_safe(event_text, date_str, year_str)
        
        print("\n" + "="*50)
        print("🤖 AI SERVICE TEST RESULTS")
        print("="*50)
        print(f"Total Tweets Generated: {len(tweets)}\n")
        
        for i, tw in enumerate(tweets, 1):
            print(f"--- Tweet {i} ---")
            print(tw)
            print()
            
        print(f"Poll Options: {poll_options}")
        print(f"Image Prompt: {image_prompt}")
        print("="*50 + "\n")
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
