from db.database import get_connection
import unicodedata


# ─────────────────────────────
# NORMALIZA TEXTO
# ─────────────────────────────
def normalizar(texto: str):
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


# ─────────────────────────────
# LISTAR CATEGORIAS
# ─────────────────────────────
def listar_categorias(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM categorias
        WHERE usuario_uuid = ?
           OR usuario_uuid = 'default'
        ORDER BY nome
    """, (usuario_uuid,))

    categorias = cursor.fetchall()
    conn.close()
    return categorias



# ─────────────────────────────
# CRIAR CATEGORIA
# ─────────────────────────────
def criar_categoria(usuario_uuid, nome):
    nome = normalizar(nome)

    if not nome:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    # evita duplicata
    cursor.execute(
        """
        SELECT 1
        FROM categorias
        WHERE usuario_uuid = ?
          AND lower(nome) = ?
        """,
        (usuario_uuid, nome),
    )

    if cursor.fetchone():
        conn.close()
        return False

    cursor.execute(
        """
        INSERT INTO categorias (usuario_uuid, nome)
        VALUES (?, ?)
        """,
        (usuario_uuid, nome.title()),
    )

    conn.commit()
    conn.close()
    return True


# ─────────────────────────────
# APAGAR CATEGORIA
# ─────────────────────────────
def apagar_categoria(categoria_id, usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM categorias
        WHERE id = ?
          AND usuario_uuid = ?
        """,
        (categoria_id, usuario_uuid),
    )

    apagou = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return apagou
