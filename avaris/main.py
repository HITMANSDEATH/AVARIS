from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from backend.api.routes import router as api_router
from backend.database.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the database
    print("Initializing Database...")
    init_db()
    yield
    # Shutdown logic
    print("Shutting down AVARIS Backend...")

app = FastAPI(title="AVARIS Environmental Monitor API", lifespan=lifespan)

# Allow React frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def root():
    return {"message": "Welcome to AVARIS Environment Monitoring System API"}

if __name__ == "__main__":
    print("Starting AVARIS Backend Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
