import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import db
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.connect()
    yield
    # Shutdown
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
origins = settings.BACKEND_CORS_ORIGINS or []
if "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")
if "http://127.0.0.1:5173" not in origins:
    origins.append("http://127.0.0.1:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve built frontend statically if directory exists
frontend_dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
if os.path.exists(frontend_dist_path):
    # Mount assets folder
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="static_assets")
    
    # Catch-all to serve index.html for SPA (React Router client routing)
    @app.get("/{catchall:path}")
    async def serve_frontend(catchall: str):
        # Allow requests to API endpoints to fall through to the routers
        if catchall.startswith("api/v1") or catchall.startswith("docs") or catchall.startswith("openapi.json"):
            return None
        
        index_file = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Welcome to DeepMediaCheck API"}
else:
    @app.get("/")
    def root():
        return {"message": "Welcome to DeepMediaCheck API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

