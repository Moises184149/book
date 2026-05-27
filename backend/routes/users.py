from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import mysql.connector

from backend.database.connection import conectar

router = APIRouter()


class UserSchema(BaseModel):
    username: str
    contrasena: str
    tipo: int


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    contrasena: Optional[str] = None
    tipo: Optional[int] = None


class OnboardingSchema(BaseModel):
    id_usuario: int


@router.get("/api/users")
def api_obtener_usuarios():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id_usuario, username, tipo, primer_ingreso
        FROM usuarios
        """
    )

    usuarios = cursor.fetchall()
    db.close()

    return usuarios


@router.post("/api/users")
def api_crear_usuario(user: UserSchema):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE username = %s", (user.username,))

    if cursor.fetchone():
        db.close()
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")

    cursor.execute(
        """
        INSERT INTO usuarios
        (username, contrasena, tipo, primer_ingreso)
        VALUES (%s, %s, %s, 1)
        """,
        (user.username, user.contrasena, user.tipo),
    )

    db.commit()
    db.close()

    return {"message": "Usuario creado con éxito."}


@router.put("/api/users/{id_usuario}")
def api_modificar_usuario(id_usuario: int, user: UserUpdateSchema):
    db = None
    cursor = None

    try:
        db = conectar()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        usuario_actual = cursor.fetchone()

        if not usuario_actual:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")

        nuevo_nom = user.username if user.username else usuario_actual["username"]
        nueva_pass = user.contrasena if user.contrasena else usuario_actual["contrasena"]
        nuevo_tipo = user.tipo if user.tipo is not None else usuario_actual["tipo"]

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE username = %s
              AND id_usuario <> %s
            LIMIT 1
            """,
            (nuevo_nom, id_usuario),
        )

        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")

        cursor.execute(
            """
            UPDATE usuarios
            SET username = %s,
                contrasena = %s,
                tipo = %s
            WHERE id_usuario = %s
            """,
            (nuevo_nom, nueva_pass, nuevo_tipo, id_usuario),
        )

        db.commit()
        return {"message": "Registro actualizado correctamente."}

    except HTTPException:
        if db:
            db.rollback()
        raise

    except mysql.connector.IntegrityError:
        if db:
            db.rollback()
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")

    except mysql.connector.Error as e:
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")

    except Exception as e:
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@router.delete("/api/users/{id_usuario}")
def api_eliminar_usuario(id_usuario: int):
    db = conectar()
    cursor = db.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))

    db.commit()
    db.close()

    return {"message": "Usuario eliminado correctamente."}


@router.put("/finish-onboarding")
def finalizar_onboarding(data: OnboardingSchema):
    db = conectar()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE usuarios
        SET primer_ingreso = 0
        WHERE id_usuario = %s
        """,
        (data.id_usuario,),
    )

    db.commit()
    db.close()

    return {"message": "Perfil configurado"}
