"""
Rate Limiting Middleware
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key - prefer API key if available, otherwise use IP.
    """
    # Try to get API key from header or query
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    
    if api_key:
        # Rate limit by API key (allows higher limits for authenticated users)
        return f"api_key:{api_key}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Initialize rate limiter with custom key function
limiter = Limiter(key_func=get_rate_limit_key)


async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Custom handler for rate limit exceeded.
    """
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}")
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "retry_after": 60
        }
    )

