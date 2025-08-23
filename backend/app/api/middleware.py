"""
API middleware for error handling and logging
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from app.utils.logger import app_logger


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log successful requests
            process_time = time.time() - start_time
            app_logger.info(
                f"Request {request_id} - {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Time: {process_time:.3f}s"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except HTTPException as e:
            # FastAPI HTTP exceptions - let them pass through
            process_time = time.time() - start_time
            app_logger.warning(
                f"Request {request_id} - {request.method} {request.url.path} - "
                f"HTTP Error: {e.status_code} - {e.detail} - Time: {process_time:.3f}s"
            )
            raise
            
        except ValidationError as e:
            # Pydantic validation errors
            process_time = time.time() - start_time
            app_logger.error(
                f"Request {request_id} - {request.method} {request.url.path} - "
                f"Validation Error: {e} - Time: {process_time:.3f}s"
            )
            
            return JSONResponse(
                status_code=422,
                content={
                    "error": "Validation Error",
                    "message": "Invalid input data",
                    "details": e.errors(),
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )
            
        except SQLAlchemyError as e:
            # Database errors
            process_time = time.time() - start_time
            app_logger.error(
                f"Request {request_id} - {request.method} {request.url.path} - "
                f"Database Error: {e} - Time: {process_time:.3f}s"
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Database Error",
                    "message": "An error occurred while accessing the database",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )
            
        except Exception as e:
            # Unexpected errors
            process_time = time.time() - start_time
            app_logger.error(
                f"Request {request_id} - {request.method} {request.url.path} - "
                f"Unexpected Error: {e} - Time: {process_time:.3f}s",
                exc_info=True
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred",
                    "request_id": request_id
                },
                headers={"X-Request-ID": request_id}
            )


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware with detailed logging"""
    
    def __init__(self, app, allow_origins: list = None, allow_methods: list = None, allow_headers: list = None):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allow_headers = allow_headers or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            response.headers["Access-Control-Max-Age"] = "86400"
            return response
        
        response = await call_next(request)
        
        # Add CORS headers to response
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response