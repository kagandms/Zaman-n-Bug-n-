import tweepy
from tweepy.asynchronous import AsyncClient
from src.core.config import settings
from src.core.logger import logger
import asyncio
from typing import Any, Optional

POST_MAX_ATTEMPTS = 3


def _extract_status_code(error: Exception) -> Optional[int]:
    """Reads the HTTP status code from Tweepy exceptions when available."""
    response = getattr(error, "response", None)
    if response is None:
        return None

    status_code = getattr(response, "status_code", None)
    if status_code is not None:
        return status_code
    return getattr(response, "status", None)


def _format_twitter_error(error: Exception) -> str:
    """Formats Tweepy exceptions with status code and API messages."""
    status_code = _extract_status_code(error)
    api_messages = getattr(error, "api_messages", None)

    if status_code is None:
        return str(error)
    if api_messages:
        return f"{status_code} - {' | '.join(api_messages)}"
    return str(error)


def _is_retryable_twitter_error(error: Exception) -> bool:
    """Retries only transient upstream failures."""
    status_code = _extract_status_code(error)
    if status_code is None:
        return False
    return status_code >= 500

class TwitterService:
    def __init__(self):
        # V2 Client (Async)
        self.client = AsyncClient(
            consumer_key=settings.API_KEY.get_secret_value(),
            consumer_secret=settings.API_SECRET.get_secret_value(),
            access_token=settings.ACCESS_TOKEN.get_secret_value(),
            access_token_secret=settings.ACCESS_TOKEN_SECRET.get_secret_value()
        )
        
        # V1.1 API (Sync for Media Upload - Tweepy Async doesn't confirm support for media_upload yet)
        # We will wrap it in asyncio.to_thread for now or use the sync API in a separate thread.
        auth = tweepy.OAuth1UserHandler(
            settings.API_KEY.get_secret_value(),
            settings.API_SECRET.get_secret_value(),
            settings.ACCESS_TOKEN.get_secret_value(),
            settings.ACCESS_TOKEN_SECRET.get_secret_value()
        )
        self.api_v1 = tweepy.API(auth)

    async def verify_credentials(self) -> bool:
        """Verifies API credentials."""
        try:
            me = await self.client.get_me(user_auth=True)
            logger.info(f"Connected to Twitter as: {me.data.username}")
            return True
        except tweepy.HTTPException as error:
            logger.error(
                "Twitter Auth Verification Failed: "
                f"{_format_twitter_error(error)}"
            )
            logger.error(
                "X API v2 posting requires keys and tokens from an app "
                "attached to a Project with write access."
            )
            return False
        except Exception as error:
            logger.error(f"Twitter Auth Verification Failed: {error}")
            return False

    async def upload_media(self, filename: str) -> str:
        """Uploads media using V1.1 API (wrapped in thread)."""
        loop = asyncio.get_event_loop()
        try:
            media = await loop.run_in_executor(None, self.api_v1.media_upload, filename)
            logger.info(f"Media uploaded: {media.media_id_string}")
            return media.media_id_string
        except Exception as e:
            logger.error(f"Media Upload Failed: {e}")
            return None

    async def _create_tweet(
        self,
        params: dict[str, Any],
        tweet_number: int,
        total_tweets: int
    ) -> Optional[str]:
        """Creates a tweet with retries for transient X API failures."""
        for attempt in range(1, POST_MAX_ATTEMPTS + 1):
            try:
                response = await self.client.create_tweet(**params, user_auth=True)
                tweet_id = response.data["id"]
                logger.info(f"Posted tweet {tweet_number}/{total_tweets}: {tweet_id}")
                return tweet_id
            except tweepy.HTTPException as error:
                error_details = _format_twitter_error(error)
                if not _is_retryable_twitter_error(error) or attempt == POST_MAX_ATTEMPTS:
                    logger.error(
                        f"Failed to post tweet {tweet_number}: {error_details}"
                    )
                    return None

                retry_delay = 3 * attempt
                logger.warning(
                    f"Transient X API failure for tweet {tweet_number}: {error_details}. "
                    f"Retrying in {retry_delay}s..."
                )
                await asyncio.sleep(retry_delay)
            except Exception as error:
                logger.error(f"Failed to post tweet {tweet_number}: {error}")
                return None

        return None

    async def post_thread(self, tweets: list, media_id: str = None, poll_options: list = None):
        """Posts a chain of tweets."""
        if settings.DRY_RUN:
            logger.info(f"[DRY RUN] Would post {len(tweets)} tweets.")
            return True

        last_id = None
        
        for i, text in enumerate(tweets):
            params = {"text": text}
            
            # First tweet media
            if i == 0 and media_id:
                params["media_ids"] = [media_id]
            
            # Reply to previous
            if last_id:
                params["in_reply_to_tweet_id"] = last_id
                
            # Last tweet poll
            if i == len(tweets) - 1 and poll_options and len(poll_options) >= 2:
                params["poll_options"] = poll_options
                params["poll_duration_minutes"] = 1440

            tweet_id = await self._create_tweet(params, i + 1, len(tweets))
            if tweet_id is None:
                return False

            last_id = tweet_id
            await asyncio.sleep(2)

        return True
