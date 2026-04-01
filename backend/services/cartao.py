from db.database import get_connection
from datetime import date, datetime
import uuid
from services.categoria_auto import detectar_categoria
from utils.datetime_utils import agora_brasil


# ================= REGISTRAR GASTOS NO CARTÃO =================
def registrar_gasto_cartao(
    usuario_uuid, valor, descricao, parcelas=1, parcelas_pagas=0
):
    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 buscar cartão ativo (AGORA COM VENCIMENTO)
    cursor.execute(
        """
        SELECT id, dia_fechamento, dia_vencimento
        FROM cartoes
        WHERE usuario_uuid = ?
          AND ativo = 1
        LIMIT 1
    """,
        (usuario_uuid,),
    )

    cartao = cursor.fetchone()

    if not cartao:
        conn.close()
        raise Exception("Usuário não possui cartão cadastrado")

    cartao_id = cartao["id"]
    dia_fechamento = cartao["dia_fechamento"]
    dia_vencimento = cartao["dia_vencimento"]

    hoje = date.today()

    valor_parcela = round(valor / max(parcelas, 1), 2)
    categoria = detectar_categoria(descricao)
    parcelado = 1 if parcelas > 1 else 0

    # 🔥 ID único da compra
    compra_id = str(uuid.uuid4())

    # ======================================================
    # 🔥 REGRA CORRETA (MESMA DA FATURA)
    # ======================================================

    mes_base, ano_base = calcular_mes_fatura_base(hoje, dia_fechamento, dia_vencimento)

    # ======================================================
    # 🔹 salvar parcelas
    # ======================================================

    for i in range(parcelas_pagas, parcelas):

        parcela_numero = i + 1

        mes_fatura = mes_base + (i - parcelas_pagas)
        ano_fatura = ano_base

        # 🔹 ajuste de virada de ano
        while mes_fatura > 12:
            mes_fatura -= 12
            ano_fatura += 1

        cursor.execute(
            """
            INSERT INTO gastos_cartao (
                usuario_uuid,
                cartao_id,
                valor,
                descricao,
                categoria,
                data_compra,
                mes_fatura,
                ano_fatura,
                parcelado,
                qtd_parcelas,
                valor_parcela,
                parcelas_pagas,
                compra_id,
                parcela_numero
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                usuario_uuid,
                cartao_id,
                valor,
                descricao,
                categoria,
                hoje,
                mes_fatura,
                ano_fatura,
                parcelado,
                parcelas,
                valor_parcela,
                parcelas_pagas,
                compra_id,
                parcela_numero,
            ),
        )

    conn.commit()
    conn.close()

    return {
        "descricao": descricao,
        "categoria": categoria,
        "valor": valor,
        "parcelas": parcelas,
        "parcelas_pagas": parcelas_pagas,
        "valor_parcela": valor_parcela,
    }


# ================= TOTAL DE GASTOS NO CARTÃO =================
def total_gastos_cartao_periodo(usuario_uuid, inicio, fim):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(valor_parcela), 0)
            FROM gastos_cartao
            WHERE usuario_uuid = ?
            AND strftime('%Y-%m', data_compra) = strftime('%Y-%m', 'now')
        """,
            (usuario_uuid,),
        )

        total = cursor.fetchone()[0]
        return float(total)

    except Exception as e:
        print(f"[ERRO] Falha ao calcular total do cartão: {e}")
        raise

    finally:
        if conn:
            conn.close()


# ================= MAIORES GASTOS NO CARTÃO =================
def maiores_gastos_cartao_periodo(usuario_uuid, inicio, fim, limite=5):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        mes = inicio.month
        ano = inicio.year

        cursor.execute(
            """
            SELECT descricao, SUM(valor) AS total
            FROM gastos_cartao
            WHERE usuario_uuid = ?
              AND mes_fatura = ?
              AND ano_fatura = ?
            GROUP BY descricao
            ORDER BY total DESC
            LIMIT ?
        """,
            (usuario_uuid, mes, ano, limite),
        )

        return cursor.fetchall()

    except Exception as e:
        print(f"[ERRO] Falha ao buscar gastos do cartão: {e}")
        raise

    finally:
        if conn:
            conn.close()


# ================= TOTAL FATURA ATUAL =================
def total_cartao_fatura_atual(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    agora = datetime.now()

    cursor.execute(
        """
        SELECT dia_fechamento, dia_vencimento
        FROM cartoes
        WHERE usuario_uuid = ?
        AND ativo = 1
        LIMIT 1
    """,
        (usuario_uuid,),
    )

    cartao = cursor.fetchone()

    if not cartao:
        conn.close()
        return 0.0

    mes, ano = calcular_mes_fatura_base(
        agora, cartao["dia_fechamento"], cartao["dia_vencimento"]
    )

    cursor.execute(
        """
        SELECT COALESCE(SUM(valor_parcela), 0)
        FROM gastos_cartao
        WHERE usuario_uuid = ?
        AND mes_fatura = ?
        AND ano_fatura = ?
        AND quitado = 0
        AND parcelas_pagas < qtd_parcelas
    """,
        (usuario_uuid, mes, ano),
    )

    total = cursor.fetchone()[0]
    conn.close()

    return float(total)


# ================= CALCULAR FATURA CARTÃO =================
def calcular_faturas_cartao(usuario_uuid):

    conn = get_connection()
    cursor = conn.cursor()

    agora = agora_brasil()

    # 🔹 Buscar cartão ativo
    cursor.execute(
        """
        SELECT dia_fechamento, dia_vencimento
        FROM cartoes
        WHERE usuario_uuid = ?
        AND ativo = 1
        LIMIT 1
    """,
        (usuario_uuid,),
    )

    cartao = cursor.fetchone()

    if not cartao:
        conn.close()
        return {"faturas": [], "total_atual": 0, "total_proximo": 0}

    dia_fechamento = cartao["dia_fechamento"]
    dia_vencimento = cartao["dia_vencimento"]

    mes = agora.month
    ano = agora.year

    # ======================================================
    # 🔥 REGRA PRINCIPAL (PADRÃO CARTÃO REAL)
    # ======================================================

    mes, ano = calcular_mes_fatura_base(agora, dia_fechamento, dia_vencimento)

    # ======================================================
    # 🔹 Função interna para somar fatura
    # ======================================================

    def get_total(m, a):
        cursor.execute(
            """
            SELECT COALESCE(SUM(valor_parcela), 0)
            FROM gastos_cartao
            WHERE usuario_uuid = ?
            AND mes_fatura = ?
            AND ano_fatura = ?
            AND quitado = 0
            AND parcelas_pagas < qtd_parcelas
            """,
            (usuario_uuid, m, a),
        )
        return float(cursor.fetchone()[0])

    # ======================================================
    # 🔹 Labels dos meses
    # ======================================================

    meses = [
        "",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    # ======================================================
    # 🔹 Montar 3 faturas
    # ======================================================

    faturas = []

    for i in range(3):
        m = mes + i
        a = ano

        if m > 12:
            m -= 12
            a += 1

        faturas.append({"label": meses[m], "total": get_total(m, a)})

    conn.close()

    total_atual = faturas[0]["total"] if faturas else 0
    total_proximo = faturas[1]["total"] if len(faturas) > 1 else 0

    return {
        "faturas": faturas,
        "total_atual": total_atual,
        "total_proximo": total_proximo,
    }


# ================= ATUALIZAR PARCELAS CARTÃO =================
def atualizar_parcelas(gasto, cursor, dia_vencimento):

    if not gasto["qtd_parcelas"]:
        return

    if gasto["quitado"]:
        return

    hoje = date.today()

    # 🔥 só atualiza no dia do vencimento
    if hoje.day != dia_vencimento:
        return

    # 🔥 evita atualizar duas vezes no mesmo mês
    if gasto["ultima_atualizacao"]:
        ultima = date.fromisoformat(gasto["ultima_atualizacao"])
        if ultima.month == hoje.month and ultima.year == hoje.year:
            return

    novas_pag = gasto["parcelas_pagas"] + 1

    quitado = 0
    if novas_pag >= gasto["qtd_parcelas"]:
        novas_pag = gasto["qtd_parcelas"]
        quitado = 1

    cursor.execute(
        """
        UPDATE gastos_cartao
        SET parcelas_pagas = ?,
            quitado = ?,
            ultima_atualizacao = ?
        WHERE id = ?
        """,
        (novas_pag, quitado, hoje, gasto["id"]),
    )


# ================== CALCULAR MES FATURAS =========================
def calcular_mes_fatura_base(data, dia_fechamento, dia_vencimento):
    mes = data.month
    ano = data.year

    # 1️⃣ ainda não venceu → fatura anterior
    if data.day <= dia_vencimento:
        mes -= 1
        if mes < 1:
            mes = 12
            ano -= 1

    # 2️⃣ passou fechamento → próxima fatura
    elif data.day > dia_fechamento:
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

    return mes, ano
