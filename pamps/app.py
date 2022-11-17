"""Main API app"""
from fastapi import FastAPI

from .routes import main_router

app = FastAPI(
    title="Pamps",
    version="0.1.0",
    description="Pamps is a posting app",
)

app.include_router(main_router)
