"""
Middleware for request logging and performance monitoring
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .logger import log_api_request, log_error

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Get request details
        method = request.method
        url = str(request.url)
        path = request.url.path
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful request
            log_api_request(
                endpoint=path,
                method=method,
                status_code=response.status_code,
                duration=duration,
                url=url
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            log_error(
                error=e,
                context=f"Request {method} {path}",
                endpoint=path,
                method=method,
                duration=duration,
                url=url
            )
            
            # Re-raise the exception
            raise 