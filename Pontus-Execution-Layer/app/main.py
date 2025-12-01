from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.api.routes_data import router, set_aggregator
from app.api.routes_optimization import (
    router as optimization_router,
    set_routing_service,
    set_aggregator_for_routing
)
from app.api.routes_execution import (
    router as execution_router,
    set_execution_service
)
from app.api.routes_treasury import (
    router as treasury_router,
    set_services as set_treasury_services
)
from app.api.routes_fx_intelligence import (
    router as fx_intelligence_router,
    set_services as set_fx_services
)
from app.services.aggregator_service import AggregatorService
from app.services.routing_service import RoutingService
from app.services.execution.execution_service import ExecutionService
from app.infra.database import init_db
from app.infra.redis_client import init_redis
from app.tasks.background_tasks import start_background_tasks, stop_background_tasks
from app.infra.logging_config import setup_logging
from app.middleware.rate_limit import limiter, rate_limit_handler
from app.middleware.auth import verify_api_key
from app.config import settings
from slowapi.errors import RateLimitExceeded

# Setup logging first
logger = setup_logging()
logger.info("Starting Pontus Routing API...")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    
    logger.info("Initializing Redis...")
    await init_redis()
    
    logger.info("Initializing aggregator service...")
    aggregator = AggregatorService()
    set_aggregator(aggregator)
    set_aggregator_for_routing(aggregator)
    
    logger.info("Initializing routing service...")
    # Auto-detect CPLEX: use CPLEX if available, OR-Tools as graceful fallback
    routing_service = RoutingService(use_cplex=None)  # None = auto-detect CPLEX, fallback to OR-Tools
    set_routing_service(routing_service)
    
    logger.info("Initializing execution service...")
    execution_service = ExecutionService(
        routing_service=routing_service,
        aggregator_service=aggregator
    )
    set_execution_service(execution_service)
    
    logger.info("Initializing treasury service...")
    set_treasury_services(aggregator, routing_service)
    
    logger.info("Initializing FX intelligence service...")
    set_fx_services(aggregator, routing_service)
    
    logger.info("Starting background tasks...")
    await start_background_tasks()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Stopping background tasks...")
    await stop_background_tasks()
    
    logger.info("Closing aggregator...")
    await aggregator.close()
    
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Pontus Routing API",
    description="Cross-border routing optimizer with data layer and optimization engine",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",")] if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)
logger.info(f"CORS configured for origins: {cors_origins}")

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
logger.info(f"Rate limiting configured: {settings.rate_limit_per_minute} req/min, {settings.rate_limit_per_hour} req/hour")

# API Key Authentication Middleware (if enabled)
if settings.require_api_key:
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        # Skip auth for health check, docs, and root
        if request.url.path in ["/health", "/docs", "/openapi.json", "/", "/redoc"]:
            return await call_next(request)
        
        is_valid = await verify_api_key(request)
        if not is_valid:
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "detail": "Invalid or missing API key"}
            )
        
        return await call_next(request)
    logger.info("API key authentication enabled")
else:
    logger.info("API key authentication disabled (set REQUIRE_API_KEY=true to enable)")

# Include routers
app.include_router(router)  # Data layer endpoints
app.include_router(optimization_router)  # Routing optimization endpoints
app.include_router(execution_router)  # Execution layer endpoints
app.include_router(treasury_router)  # Treasury management endpoints
app.include_router(fx_intelligence_router)  # FX intelligence endpoints


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pontus Routing API - Complete System",
        "version": "3.0.0",
        "components": {
            "data_layer": "✅ Complete",
            "routing_engine": "✅ Complete",
            "execution_layer": "✅ Complete (Simulation)"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

