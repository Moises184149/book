from fastapi import APIRouter

from backend.database.connection import conectar

router = APIRouter()


@router.get("/genres")
def obtener_generos():
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT DISTINCT genero FROM libros")
    generos = cursor.fetchall()
    db.close()

    return {"generos": generos}


@router.get("/onboarding/books/{genero}")
def libros_onboarding(genero: str):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id_libro, titulo, autor, genero
        FROM libros
        WHERE genero = %s
        LIMIT 10
        """,
        (genero,),
    )

    libros = cursor.fetchall()
    db.close()

    return {"libros": libros}


@router.get("/recommendations/{id_usuario}")
def obtener_recomendaciones_usuario(id_usuario: int):
    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id_libro, titulo, autor, genero
        FROM libros
        ORDER BY RAND()
        LIMIT 6
        """
    )

    libros = cursor.fetchall()
    db.close()

    return {"recommendations": libros}
