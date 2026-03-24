from db.database import get_connection
from utils.datetime_utils import agora_brasil_str


# ─────────────────────────────
# CRIAR CONTA FIXA
# ─────────────────────────────
def criar_conta_fixa(
    usuario_uuid,
    descricao,
    valor,
    categoria,
    periodicidade,
    dia_vencimento
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contas_fixas (
            usuario_uuid,
            descricao,
            valor,
            categoria,
            periodicidade,
            dia_vencimento,
            ativa,
            data_criacao
        )
        VALUES (?, ?, ?, ?, ?, ?, 1, ?)
    """, (
        usuario_uuid,
        descricao,
        valor,
        categoria,
        periodicidade,
        dia_vencimento,
        agora_brasil_str(),
    ))

    conn.commit()
    conn.close()


# ─────────────────────────────
# LISTAR CONTAS FIXAS
# ─────────────────────────────
def listar_contas_fixas(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, descricao, valor, categoria, periodicidade, dia_vencimento
        FROM contas_fixas
        WHERE usuario_uuid = ?
        ORDER BY dia_vencimento
    """, (usuario_uuid,))

    contas = cursor.fetchall()
    conn.close()
    return contas


# ─────────────────────────────
# REMOVER CONTA FIXA
# ─────────────────────────────
def remover_conta_fixa(conta_id, usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM contas_fixas
        WHERE id = ?
          AND usuario_uuid = ?
    """, (conta_id, usuario_uuid))

    conn.commit()
    conn.close()


# ─────────────────────────────
# TOTAL CONTAS FIXAS (MENSAL)
# ─────────────────────────────
def total_contas_fixas_mes(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM contas_fixas
        WHERE usuario_uuid = ?
          AND ativa = 1
    """, (usuario_uuid,))

    total = cursor.fetchone()[0]
    conn.close()
    return float(total)
