"""
FastAPI main application module for IoT Device Simulator
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from app.core.config import settings
from app.core.database import create_tables
from app.api.v1 import projects, devices, payloads, targets, simulation, connectors
from app.api.middleware import ErrorHandlingMiddleware
from app.utils.logger import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    app_logger.info("Starting IoT Device Simulator API...")
    
    # Create database tables if they don't exist
    try:
        create_tables()
        app_logger.info("Database tables created/verified")
    except Exception as e:
        app_logger.error(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down IoT Device Simulator API...")


app = FastAPI(
    title="IoT Device Simulator API",
    description="API for simulating IoT devices and sending telemetry data to multiple target systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add custom error handling middleware
app.add_middleware(ErrorHandlingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    projects.router, 
    prefix="/api/v1/projects", 
    tags=["Projects"],
    responses={404: {"description": "Project not found"}}
)
app.include_router(
    devices.router, 
    prefix="/api/v1/devices", 
    tags=["Devices"],
    responses={404: {"description": "Device not found"}}
)
app.include_router(
    payloads.router, 
    prefix="/api/v1/payloads", 
    tags=["Payloads"],
    responses={404: {"description": "Payload not found"}}
)
app.include_router(
    targets.router, 
    prefix="/api/v1/targets", 
    tags=["Target Systems"],
    responses={404: {"description": "Target system not found"}}
)
app.include_router(
    simulation.router, 
    prefix="/api/v1/simulation", 
    tags=["Simulation"],
    responses={404: {"description": "Simulation not found"}}
)
app.include_router(
    connectors.router, 
    prefix="/api/v1", 
    tags=["Connectors"],
    responses={404: {"description": "Connector not found"}}
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "IoT Device Simulator API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }


@app.get("/info", tags=["Info"])
async def get_api_info():
    """Get API information and statistics"""
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "api": {
            "name": "IoT Device Simulator API",
            "version": "1.0.0",
            "description": "API for simulating IoT devices and sending telemetry data"
        },
        "database": {
            "status": db_status,
            "url": settings.database_url.split("://")[0] + "://***"  # Hide credentials
        },
        "features": {
            "target_systems": ["HTTP", "MQTT", "Kafka", "WebSocket", "FTP", "Pub/Sub"],
            "payload_types": ["Visual JSON Builder", "Python Code"],
            "simulation": "Real-time device simulation with configurable intervals"
        }
    }


# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    app_logger.error(f"Internal server error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )