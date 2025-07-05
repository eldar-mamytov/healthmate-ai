from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .database import create_db_tables, SessionLocal, engine
from . import models 
from . import auth

from .routers import auth_router 
from .routers import llm_router  

# Load environment variables
load_dotenv()

# Ensure database tables are created on startup (remains)
# This uses models.Base.metadata.create_all(bind=engine)
models.Base.metadata.create_all(bind=engine) # This should actually be called after app initialization or in an event handler.
                                             # It's here for now but will be triggered by create_db_tables() on startup.

app = FastAPI(title="HealthMate-AI Backend")

# CORS Configuration (remains)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event for database table creation (remains)
@app.on_event("startup")
def on_startup():
    create_db_tables()

# Root and health check endpoints (good to keep in main.py for core app status)
@app.get("/")
async def read_root():
    return {"message": "Welcome to HealthMate-AI Backend"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is healthy and running."}

# --- Include Routers ---
# All endpoints defined in auth_router.py will be available under /auth/
app.include_router(auth_router.router)
# All endpoints defined in llm_router.py will be available under /ai/
app.include_router(llm_router.router)

# All other previously existing endpoint definitions (like /users/, /token, /chat, /embed)
# should now be removed from this file, as they are handled by the imported routers.
# Similarly, the direct initialization of OpenAI client, local_llm, local_embeddings
# should be removed as they are now in llm_router.py.