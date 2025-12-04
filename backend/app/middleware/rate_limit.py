"""
Rate limiting middleware
"""
import time
from typing import Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as aioredis
from app.core.config import settings
from loguru import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client: aioredis.Redis = None
        self._redis_initialized = False
    
    async def _get_redis(self):
        """Get or create Redis client"""
        if not self._redis_initialized:
            try:
                self.redis_client = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                self._redis_initialized = True
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                self._redis_initialized = False
        return self.redis_client
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with rate limiting
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/", "/health", "/api/docs", "/api/redoc", "/api/openapi.json"]:
            return await call_next(request)
        
        redis_client = await self._get_redis()
        
        if redis_client:
            # Get client identifier (IP address)
            client_ip = request.client.host if request.client else "unknown"
            
            # Rate limit keys
            minute_key = f"rate_limit:minute:{client_ip}"
            hour_key = f"rate_limit:hour:{client_ip}"
            
            try:
                # Check minute limit
                minute_count = await redis_client.get(minute_key)
                if minute_count and int(minute_count) >= settings.RATE_LIMIT_PER_MINUTE:
                    logger.warning(f"Rate limit exceeded (minute) for {client_ip}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later."
                    )
                
                # Check hour limit
                hour_count = await redis_client.get(hour_key)
                if hour_count and int(hour_count) >= settings.RATE_LIMIT_PER_HOUR:
                    logger.warning(f"Rate limit exceeded (hour) for {client_ip}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later."
                    )
                
                # Increment counters
                current_minute = int(time.time() / 60)
                current_hour = int(time.time() / 3600)
                
                pipe = redis_client.pipeline()
                pipe.incr(minute_key)
                pipe.expire(minute_key, 60)
                pipe.incr(hour_key)
                pipe.expire(hour_key, 3600)
                await pipe.execute()
            
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Rate limiting error: {str(e)}")
                # Continue without rate limiting if Redis fails
        
        return await call_next(request)

