from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.db import init_pool
from api import cache

from api.routes import auth, courses, calendar, forums, content, assignments, reports


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_pool()
    cache.init_cache()
    yield
    # Shutdown — nothing to clean up explicitly


app = FastAPI(
    title="Course Management System API",
    description="COMP3161 Final Project — Backend API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # tighten this when deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(calendar.router)
app.include_router(content.router)
app.include_router(forums.router)
app.include_router(assignments.router)
app.include_router(reports.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "CMS API is running."}
