from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://localhost:5432/routing_db"  # Will use current OS user
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 2  # TTL in seconds for route data
    
    # Security
    api_keys: str = ""  # Comma-separated list of valid API keys
    require_api_key: bool = False  # Set to True in production
    cors_origins: str = "*"  # Comma-separated origins, or "*" for all
    
    # Rate Limiting
    rate_limit_per_minute: int = 60  # Requests per minute per IP
    rate_limit_per_hour: int = 1000  # Requests per hour per IP
    
    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_format: str = "json"  # json or text
    
    # API Keys
    exchangerate_api_key: Optional[str] = None
    etherscan_api_key: Optional[str] = None
    polygonscan_api_key: Optional[str] = None
    bscscan_api_key: Optional[str] = None
    snowscan_api_key: Optional[str] = None
    arbiscan_api_key: Optional[str] = None
    optimism_api_key: Optional[str] = None
    coingecko_api_key: Optional[str] = None
    socket_api_key: Optional[str] = None
    lifi_api_key: Optional[str] = None
    transak_api_key: Optional[str] = None
    onmeta_api_key: Optional[str] = None
    zerox_api_key: Optional[str] = None
    
    # Execution Layer API Keys
    wise_api_key: Optional[str] = None
    wise_api_email: Optional[str] = None
    kraken_api_key: Optional[str] = None
    kraken_private_key: Optional[str] = None
    
    # Execution mode: "simulation" or "real"
    execution_mode: str = "simulation"  # Default to simulation for safety
    
    # Background task intervals (in seconds)
    crypto_gas_bridge_interval: int = 2
    fx_bank_liquidity_interval: int = 5  # Real-time FX updates every 5 seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

