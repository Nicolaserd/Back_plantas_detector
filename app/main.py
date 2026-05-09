# app/main.py
from fastapi import FastAPI
from app.api import health_routes, websocket_routes
from app.core import config, cors
from app.utils.logger import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title=config.APP_NAME,
        description="Backend for real-time plant detection using WebSockets.",
        version="1.0.0"
    )

    # Setup CORS
    cors.setup_cors(app)

    # Include routes
    app.include_router(health_routes.router, prefix="/api")
    app.include_router(websocket_routes.router)

    @app.get("/")
    async def root():
        return {
            "message": f"Welcome to {config.APP_NAME}",
            "health_check": "/api/health",
            "websocket_endpoint": "/ws/analyze"
        }

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {config.APP_NAME} in {config.APP_ENV} mode...")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"Shutting down {config.APP_NAME}...")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
