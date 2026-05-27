from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.auth_service import ejecutar_login

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
def login(credentials: LoginRequest):
    resultado = ejecutar_login(credentials.username, credentials.password)

    if not resultado:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    return {
        "id_usuario": resultado["id_usuario"],
        "username": resultado["username"],
        "tipo": resultado["tipo"],
        "primer_ingreso": resultado["primer_ingreso"],
    }
