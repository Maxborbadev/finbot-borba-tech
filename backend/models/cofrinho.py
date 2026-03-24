from db.database import get_connection
from utils.datetime_utils import agora_brasil_str


def registrar_cofrinho(usuario_uuid, valor):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO cofrinho (usuario_uuid, valor, data)
        VALUES (?, ?, ?)
        """,
        (usuario_uuid, valor, agora_brasil_str()),
    )

    conn.commit()
    conn.close()


def obter_total_cofrinho(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COALESCE(SUM(valor), 0) as total
        FROM cofrinho
        WHERE usuario_uuid = ?
        """,
        (usuario_uuid,),
    )

    total = cursor.fetchone()["total"]
    conn.close()

    return total

def definir_total_cofrinho(usuario_uuid, novo_total):
    conn = get_connection()
    cursor = conn.cursor()

    # Apaga todos os registros antigos
    cursor.execute("""
        DELETE FROM cofrinho
        WHERE usuario_uuid = ?
    """, (usuario_uuid,))

    # Insere apenas o novo valor
    cursor.execute("""
        INSERT INTO cofrinho (usuario_uuid, valor, data)
        VALUES (?, ?, ?)
    """, (usuario_uuid, novo_total, agora_brasil_str()))

    conn.commit()
    conn.close()