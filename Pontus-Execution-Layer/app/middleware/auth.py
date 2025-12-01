"""
API Key Authentication Middleware
"""
from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(request: Request, api_key: Optional[str] = None) -> bool:
    """
    Verify API key from header or query parameter.
    
    Args:
        request: FastAPI request object
        api_key: API key from header (if provided)
        
    Returns:
        True if API key is valid, False otherwise
    """
    from app.config import settings
    
    # If API key not required, allow all requests
    if not settings.require_api_key:
        return True
    
    # Get API key from header or query parameter
    if not api_key:
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    
    if not api_key:
        logger.warning(f"API key missing from request: {request.url}")
        return False
    
    # Check against configured API keys
    valid_keys = [k.strip() for k in settings.api_keys.split(",") if k.strip()]
    
    if api_key in valid_keys:
        logger.debug(f"Valid API key used: {api_key[:8]}...")
        return True
    
    logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
    return False


async def api_key_auth_middleware(request: Request, call_next):
    """
    Middleware to check API key authentication.
    """
    from app.config import settings
    from fastapi.responses import JSONResponse
    
    # Skip auth for health check and docs
    if request.url.path in ["/health", "/docs", "/openapi.json", "/", "/redoc"]:
        return await call_next(request)
    
    # Check API key
    if settings.require_api_key:
        is_valid = await verify_api_key(request)
        if not is_valid:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Unauthorized",
                    "detail": "Invalid or missing API key. Provide X-API-Key header or api_key query parameter."
                }
            )
    
    return await call_next(request)

