from db.database import get_connection
from datetime import datetime
from models.cofrinho import obter_total_cofrinho

from models.gasto import (
    total_gastos_periodo,
    listar_gastos_periodo,
)
from models.renda import (
    total_rendas_periodo,
    listar_rendas_periodo,
)


# ─────────────────────────────
# TOTAL DE GASTOS DO SISTEMA
# ─────────────────────────────
def total_gastos_sistema():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM compras")
    total = cursor.fetchone()[0]

    conn.close()
    return float(total)


# ─────────────────────────────
# TOTAL DE RENDAS DO SISTEMA
# ─────────────────────────────
def total_rendas_sistema():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM rendas")
    total = cursor.fetchone()[0]

    conn.close()
    return float(total)


# ─────────────────────────────
# SALDO GERAL
# ─────────────────────────────
def saldo_geral():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(saldo), 0) FROM usuarios")
    total = cursor.fetchone()[0]

    conn.close()
    return float(total)


# ─────────────────────────────
# TOTAL PREMIUM
# ─────────────────────────────
def total_premium():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM usuarios 
        WHERE plano IN ('BASIC', 'PREMIUM')
        """
    )

    total = cursor.fetchone()[0]

    conn.close()
    return total


# ─────────────────────────────
# RESUMO DO USUÁRIO
# ─────────────────────────────
def resumo_usuario(usuario_uuid):
    agora = datetime.now()
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0)

    total_cofrinho = obter_total_cofrinho(usuario_uuid)

    return {
        "total_gastos": total_gastos_periodo(usuario_uuid, inicio_mes, agora),
        "total_rendas": total_rendas_periodo(usuario_uuid, inicio_mes, agora),
        "gastos": listar_gastos_periodo(usuario_uuid, inicio_mes, agora),
        "rendas": listar_rendas_periodo(usuario_uuid, inicio_mes, agora),
        "total_cofrinho": total_cofrinho,
    }


# ─────────────────────────────
# GRÁFICO LINHA
# ─────────────────────────────
def grafico_mes_usuario(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0)

    cursor.execute(
        """
        SELECT strftime('%d', data), SUM(valor)
        FROM compras
        WHERE usuario_uuid = ?
          AND data >= ?
        GROUP BY 1
        ORDER BY 1
    """,
        (usuario_uuid, inicio_mes),
    )

    gastos = cursor.fetchall()

    cursor.execute(
        """
        SELECT strftime('%d', data), SUM(valor)
        FROM rendas
        WHERE usuario_uuid = ?
          AND data >= ?
        GROUP BY 1
        ORDER BY 1
    """,
        (usuario_uuid, inicio_mes),
    )

    rendas = cursor.fetchall()
    conn.close()

    dias = [str(i).zfill(2) for i in range(1, 32)]
    mapa_gastos = {d: 0 for d in dias}
    mapa_rendas = {d: 0 for d in dias}

    for d, v in gastos:
        mapa_gastos[d] = float(v)

    for d, v in rendas:
        mapa_rendas[d] = float(v)

    return {
        "dias": dias,
        "gastos": list(mapa_gastos.values()),
        "rendas": list(mapa_rendas.values()),
    }


# ─────────────────────────────
# GRÁFICO PIZZA
# ─────────────────────────────
def grafico_pizza_gastos(usuario_uuid):

    conn = get_connection()
    cursor = conn.cursor()

    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0)

    cursor.execute(
        """
        SELECT categoria, SUM(valor)
        FROM compras
        WHERE usuario_uuid = ?
          AND data >= ?
        GROUP BY categoria
    """,
        (usuario_uuid, inicio_mes),
    )

    dados = cursor.fetchall()
    conn.close()

    categorias = []
    valores = []

    for cat, total in dados:
        categorias.append(cat or "Outros")
        valores.append(float(total))

    return {"categorias": categorias, "valores": valores}
