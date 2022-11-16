from fastapi import FastAPI

from .routes import main_router

app = FastAPI(
    title="Pamps",
    version="0.1.0",
    description="Pamps is a posting app",
)

# To use an UI Cors might be needed
# from starlette.middleware.cors import CORSMiddleware
# if settings.server and settings.server.get("cors_origins", None):
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.server.cors_origins,
#         allow_credentials=settings.get("server.cors_allow_credentials", True),
#         allow_methods=settings.get("server.cors_allow_methods", ["*"]),
#         allow_headers=settings.get("server.cors_allow_headers", ["*"]),
#     )

app.include_router(main_router)


@app.get("/")
async def index():
    return {"hello": "world"}
