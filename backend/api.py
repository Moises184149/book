from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.auth import router as auth_router
from backend.routes.users import router as users_router
from backend.routes.ratings import router as ratings_router
from backend.routes.recommendations import router as recommendations_router
from backend.routes.books import router as books_router

app = FastAPI(title="Sistema de Recomendación de Libros - API Unificada")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(ratings_router)
app.include_router(recommendations_router)
app.include_router(books_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
