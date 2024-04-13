""" 
FastApi entrypoint

Will launch a univcorn instance with parameters specified inside .env
"""

import uvicorn

# App services & repositories
from api.boot import logger
from api.boot import app
from api.boot import config

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware


# ----------------------
# LAUNCH APP
# ----------------------


# Define a custom middleware class
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # Log the request method and path
        logger.info(f"Received request: {request.method} {request.url}")

        # Continue handling the request
        response = await call_next(request)

        return response


# Add the middleware to the FastAPI app
app.add_middleware(LoggingMiddleware)

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":

    logger.info("=== Start API ===")

    uvicorn.run(
        app=config["APP"],
        host=config["HOST"],
        port=int(config["PORT"]),
        reload=config["RELOAD"],
        workers=int(config["WORKERS"]),
        access_log=config["ACCESS_LOG"],
        proxy_headers=config["PROXY_HEADERS"],
    )

    logger.info("=== Close API ===")
