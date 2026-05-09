# app/core/cors.py
from fastapi.middleware.cors import CORSMiddleware
from app.core import config

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
