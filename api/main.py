from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import init_db, close_db
from api.routes.alerts import router as alerts_router
from api.routes.posts import router as posts_router
from api.routes.export import router as export_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="HateWatch API",
    version="0.1.0",
    description="Hate speech intelligence platform API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts_router)
app.include_router(posts_router)
app.include_router(export_router)


@app.get("/")
async def root():
    return {"message": "HateWatch API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
