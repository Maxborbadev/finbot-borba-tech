from db.database import get_connection
from datetime import datetime
from utils.datetime_utils import agora_brasil_str


# ─────────────────────────────
# REGISTRAR GASTO
# ─────────────────────────────
def registrar_gasto(usuario_uuid, valor, descricao, categoria="Outros"):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # registra o gasto
        cursor.execute(
            """
    INSERT INTO compras (
        usuario_uuid,
        valor,
        descricao,
        categoria,
        data
    )
    VALUES (?, ?, ?, ?, ?)
""",
            (usuario_uuid, valor, descricao, categoria, agora_brasil_str()),
        )

        # subtrai do saldo
        cursor.execute(
            """
            UPDATE usuarios
            SET saldo = saldo - ?
            WHERE uuid = ?
        """,
            (valor, usuario_uuid),
        )

        conn.commit()

    except Exception as e:
        print(f"[ERRO] Falha ao registrar gasto: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()


# ─────────────────────────────
# TOTAL DE GASTOS POR PERÍODO
# ─────────────────────────────
def total_gastos_periodo(usuario_uuid, inicio, fim):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0)
            FROM compras
            WHERE usuario_uuid = ?
              AND datetime(data) BETWEEN datetime(?) AND datetime(?)
        """, (
            usuario_uuid,
            inicio.strftime("%Y-%m-%d %H:%M:%S"),
            fim.strftime("%Y-%m-%d %H:%M:%S"),
        ))

        total = cursor.fetchone()[0]
        return float(total)

    finally:
        if conn:
            conn.close()



# ─────────────────────────────
# MAIORES GASTOS DO PERÍODO
# ─────────────────────────────
def maiores_gastos_periodo(usuario_uuid, inicio, fim, limite=5):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT descricao, SUM(valor) AS total
            FROM compras
            WHERE usuario_uuid = ?
            AND datetime(data) BETWEEN datetime(?) AND datetime(?)
            GROUP BY descricao
            ORDER BY total DESC
            LIMIT ?
        """, (
            usuario_uuid,
            inicio.strftime("%Y-%m-%d %H:%M:%S"),
            fim.strftime("%Y-%m-%d %H:%M:%S"),
            limite,
        ))

        return cursor.fetchall()

    finally:
        if conn:
            conn.close()



# ─────────────────────────────
# LISTAR GASTOS POR PERÍODO
# ─────────────────────────────
from datetime import datetime


def listar_gastos_periodo(usuario_uuid, inicio=None, fim=None):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if inicio and fim:
            cursor.execute("""
                SELECT id, descricao, valor, categoria, data
                FROM compras
                WHERE usuario_uuid = ?
                AND datetime(data) BETWEEN datetime(?) AND datetime(?)
                ORDER BY datetime(data) DESC
            """, (
                usuario_uuid,
                inicio.strftime("%Y-%m-%d %H:%M:%S"),
                fim.strftime("%Y-%m-%d %H:%M:%S"),
            ))
        else:
            cursor.execute("""
                SELECT id, descricao, valor, categoria, data
                FROM compras
                WHERE usuario_uuid = ?
                ORDER BY data DESC
            """, (usuario_uuid,))

        resultados = cursor.fetchall()
        gastos = []

        for id, descricao, valor, categoria, data in resultados:
            if isinstance(data, str):
                data = datetime.strptime(data, "%Y-%m-%d %H:%M:%S")

            gastos.append((
                id,
                descricao,
                float(valor),
                categoria,
                data.strftime("%H:%M"),
            ))

        return gastos

    finally:
        if conn:
            conn.close()



# ─────────────────────────────
# APAGAR GASTO
# ─────────────────────────────
def apagar_gasto(gasto_id, usuario_uuid):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # busca o valor
        cursor.execute(
            """
            SELECT valor
            FROM compras
            WHERE id = ?
              AND usuario_uuid = ?
            """,
            (gasto_id, usuario_uuid),
        )

        row = cursor.fetchone()

        if not row:
            return False

        valor = float(row[0])

        # devolve o saldo
        cursor.execute(
            """
            UPDATE usuarios
            SET saldo = saldo + ?
            WHERE uuid = ?
            """,
            (valor, usuario_uuid),
        )

        # apaga o gasto
        cursor.execute(
            """
            DELETE FROM compras
            WHERE id = ?
            """,
            (gasto_id,),
        )

        conn.commit()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[ERRO] apagar_gasto: {e}")
        return False

    finally:
        if conn:
            conn.close()


# ─────────────────────────────
# EDITAR GASTO
# ─────────────────────────────
def editar_gasto(gasto_id, usuario_uuid, novo_valor, nova_descricao, nova_categoria):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT valor
            FROM compras
            WHERE id = ?
              AND usuario_uuid = ?
        """, (gasto_id, usuario_uuid))

        row = cursor.fetchone()
        if not row:
            return False

        valor_antigo = float(row["valor"])

        # devolve valor antigo
        cursor.execute("""
            UPDATE usuarios
            SET saldo = saldo + ?
            WHERE uuid = ?
        """, (valor_antigo, usuario_uuid))

        # aplica novo valor
        cursor.execute("""
            UPDATE usuarios
            SET saldo = saldo - ?
            WHERE uuid = ?
        """, (novo_valor, usuario_uuid))

        # 🔥 AQUI ATUALIZA A CATEGORIA 🔥
        cursor.execute("""
            UPDATE compras
            SET valor = ?, descricao = ?, categoria = ?
            WHERE id = ?
              AND usuario_uuid = ?
        """, (novo_valor, nova_descricao, nova_categoria, gasto_id, usuario_uuid))

        conn.commit()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        print("[ERRO] editar_gasto:", e)
        return False

    finally:
        if conn:
            conn.close()



# ========listar gastos relatorio=========
def listar_gastos_relatorio(usuario_uuid, inicio, fim):
    conn = get_connection()
    cursor = conn.cursor()

    inicio_str = inicio.strftime("%Y-%m-%d %H:%M:%S")
    fim_str = fim.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        SELECT descricao, valor, strftime('%H:%M', data)
        FROM compras
        WHERE usuario_uuid = ?
        AND datetime(data) BETWEEN datetime(?) AND datetime(?)
        ORDER BY datetime(data) ASC
    """,
        (usuario_uuid, inicio_str, fim_str),
    )

    return cursor.fetchall()
