from fastapi import APIRouter
from pydantic import BaseModel

from backend.database.connection import conectar

router = APIRouter()


class RatingSchema(BaseModel):
    id_usuario: int
    id_libro: int
    calificacion: int


@router.post("/ratings")
def guardar_calificacion(rating: RatingSchema):
    db = conectar()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO puntuacion
        (id_usuario, id_libro, calificacion)
        VALUES (%s, %s, %s)

        ON DUPLICATE KEY UPDATE
        calificacion = VALUES(calificacion)
        """,
        (rating.id_usuario, rating.id_libro, rating.calificacion),
    )

    db.commit()
    db.close()

    return {"message": "Calificación guardada"}
