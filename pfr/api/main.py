from fastapi import FastAPI
from datetime import datetime

from api.routers import ask, articles

app = FastAPI(
    title="PFR API",
    description="API docs for our 'projet fil rouge' 🚀. Don't forget the schemas are at the BOTTOM of the page.",
    summary="Made during 2023-2024 school year at CentraleSupélec",
    version="1.0.0",
)

app.include_router(ask.router)
# app.include_router(articles.router)


# @app.get("/")
# async def root():
#     return {"message": "Hello world !"}
#
#
# @app.get("/time")
# async def time():
#     return {"message": datetime.now()}
