from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import Base, engine

from app.models.user_model import User
from app.models.document_model import Document

from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.document_routes import router as document_router
from app.routes.rag_routes import router as rag_router
from app.routes.roles_routes import router as roles_router

from app.rag.vector_db import _get_collection
from app.rag.embedding import _get_model
from app.rag.reranker import _get_reranker


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _get_collection()
    _get_model()
    _get_reranker()
    yield


app = FastAPI(
    title="Financial RAG System",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(dashboard_router)
app.include_router(document_router)
app.include_router(rag_router)


@app.get("/")
def home():
    return {
        "message": "Financial RAG API Running"
    }
