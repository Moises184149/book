from backend.database.connection import conectar
import requests
import random
import time  

def importar_desde_api():
    temas = [
        "fiction", "horror", "sci-fi", "history", "fantasy", "mystery", "thriller", "science", "biography",
        "romance", "drama", "poetry", "business", "art", "music", "classics", "adventure", "children", "travel"
    ]
    import random
    import requests

    tema_azar = random.choice(temas)
    pagina_azar = random.randint(1, 100)

    print(f"\n [API] Trayendo libros de '{tema_azar}' (Página {pagina_azar})...")
    url = f"https://openlibrary.org/search.json?q={tema_azar}&limit=10&page={pagina_azar}"

    headers_navegador = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        respuesta = requests.get(url, headers=headers_navegador, timeout=10)

        if respuesta.status_code != 200:
            print(f" OpenLibrary nos bloqueó temporalmente. Código de error: {respuesta.status_code}")
            time.sleep(2)  # Pausa antes de salir para calmar al servidor
            return  # Salimos de la función sin romper el sistema

        res = respuesta.json()

        db = conectar()
        cursor = db.cursor()

        libros_nuevos = 0

        for doc in res.get('docs', []):
            titulo = doc.get('title', 'Sin título')[:100]

            lista_autores = doc.get('author_name', [])
            autor = lista_autores[0][:50] if lista_autores else 'Anónimo'

            anio = doc.get('first_publish_year', 0)

            generos_api = doc.get('subject', [])
            genero = "General"

            for g in generos_api:
                if g.lower() not in ["fiction", "general", "accessible book", "protected daisy"]:
                    genero = g.capitalize()
                    break

            if genero == "General":
                genero = tema_azar.capitalize()

            query = """
                INSERT IGNORE INTO libros
                (titulo, genero, autor, anio)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(query, (titulo, genero, autor, anio))

            if cursor.rowcount > 0:
                libros_nuevos += 1

        db.commit()
        db.close()

        print(f" ¡Éxito! Se agregaron {libros_nuevos} libros nuevos.")

        time.sleep(1.5)

    except ValueError:
        print(" Error de Formato: OpenLibrary no respondió con un JSON válido.")
        time.sleep(1.5)
    except Exception as e:
        print(f" Error fatal en la API: {e}")
        raise e

def obtener_libros():

    db = conectar()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_libro, titulo, autor, genero
        FROM libros
        LIMIT 20
    """)

    libros = cursor.fetchall()

    db.close()

    return libros