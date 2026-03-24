from db.database import get_connection
from datetime import datetime
from utils.datetime_utils import agora_brasil_str


# ─────────────────────────────
# REGISTRAR RENDA
# ─────────────────────────────
def registrar_renda(usuario_uuid, valor, descricao):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
    INSERT INTO rendas (
        usuario_uuid,
        valor,
        descricao,
        data
    )
    VALUES (?, ?, ?, ?)
""",
            (usuario_uuid, valor, descricao, agora_brasil_str()),
        )

        cursor.execute(
            """
            UPDATE usuarios
            SET saldo = saldo + ?
            WHERE uuid = ?
            """,
            (valor, usuario_uuid),
        )

        conn.commit()

    except Exception as e:
        print(f"[ERRO] Falha ao registrar renda: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()


# ─────────────────────────────
# TOTAL DE RENDAS POR PERÍODO
# ─────────────────────────────
def total_rendas_periodo(usuario_uuid, inicio=None, fim=None):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if inicio and fim:
            inicio_str = inicio.strftime("%Y-%m-%d %H:%M:%S")
            fim_str = fim.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                SELECT COALESCE(SUM(valor), 0)
                FROM rendas
                WHERE usuario_uuid = ?
                  AND data BETWEEN ? AND ?
                """,
                (usuario_uuid, inicio_str, fim_str),
            )
        else:
            cursor.execute(
                """
                SELECT COALESCE(SUM(valor), 0)
                FROM rendas
                WHERE usuario_uuid = ?
                """,
                (usuario_uuid,),
            )

        total = cursor.fetchone()[0]
        return float(total)

    except Exception as e:
        print(f"[ERRO] Falha ao calcular total de rendas: {e}")
        raise

    finally:
        if conn:
            conn.close()


# ─────────────────────────────
# LISTAR RENDAS POR PERÍODO
# ─────────────────────────────
def listar_rendas_periodo(usuario_uuid, inicio=None, fim=None):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if inicio and fim:
            inicio_str = inicio.strftime("%Y-%m-%d %H:%M:%S")
            fim_str = fim.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                SELECT id, descricao, valor, data
                FROM rendas
                WHERE usuario_uuid = ?
                  AND data BETWEEN ? AND ?
                ORDER BY data DESC
                """,
                (usuario_uuid, inicio_str, fim_str),
            )
        else:
            cursor.execute(
                """
                SELECT id, descricao, valor, data
                FROM rendas
                WHERE usuario_uuid = ?
                ORDER BY data DESC
                """,
                (usuario_uuid,),
            )

        resultados = cursor.fetchall()
        rendas = []

        for id, descricao, valor, data in resultados:

            if isinstance(data, str):
                data = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")

            rendas.append((id, descricao, float(valor), data.strftime("%H:%M")))

        return rendas

    finally:
        if conn:
            conn.close()


# ─────────────────────────────
# APAGAR RENDA
# ─────────────────────────────
def apagar_renda(renda_id, usuario_uuid):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT valor
            FROM rendas
            WHERE id = ?
              AND usuario_uuid = ?
            """,
            (renda_id, usuario_uuid),
        )

        row = cursor.fetchone()

        if not row:
            return False

        valor = float(row[0])

        cursor.execute(
            """
            UPDATE usuarios
            SET saldo = saldo - ?
            WHERE uuid = ?
            """,
            (valor, usuario_uuid),
        )

        cursor.execute(
            """
            DELETE FROM rendas
            WHERE id = ?
            """,
            (renda_id,),
        )

        conn.commit()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[ERRO] apagar_renda: {e}")
        return False

    finally:
        if conn:
            conn.close()


# ─────────────────────────────
# EDITAR RENDA
# ─────────────────────────────
def editar_renda(renda_id, usuario_uuid, novo_valor, nova_descricao):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT valor
            FROM rendas
            WHERE id = ?
              AND usuario_uuid = ?
            """,
            (renda_id, usuario_uuid),
        )

        row = cursor.fetchone()
        if not row:
            return False

        valor_antigo = float(row[0])

        cursor.execute(
            """
            UPDATE usuarios
            SET saldo = saldo - ?
            WHERE uuid = ?
            """,
            (valor_antigo, usuario_uuid),
        )

        cursor.execute(
            """
            UPDATE usuarios
            SET saldo = saldo + ?
            WHERE uuid = ?
            """,
            (novo_valor, usuario_uuid),
        )

        cursor.execute(
            """
            UPDATE rendas
            SET valor = ?, descricao = ?
            WHERE id = ?
            """,
            (novo_valor, nova_descricao, renda_id),
        )

        conn.commit()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print("[ERRO] editar_renda:", e)
        return False

    finally:
        if conn:
            conn.close()
