from db.database import get_connection
from datetime import date, datetime
import uuid
from services.categoria_auto import detectar_categoria


# ================= REGISTRAR GASTOS NO CARTÃO =================
def registrar_gasto_cartao(
    usuario_uuid, valor, descricao, parcelas=1, parcelas_pagas=0
):
    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 buscar cartão ativo
    cursor.execute(
        """
        SELECT id, dia_fechamento
        FROM cartoes
        WHERE usuario_uuid = ?
          AND ativo = 1
        LIMIT 1
    """,
        (usuario_uuid,),
    )

    cartao = cursor.fetchone()

    if not cartao:
        raise Exception("Usuário não possui cartão cadastrado")

    cartao_id = cartao["id"]
    dia_fechamento = cartao["dia_fechamento"]

    hoje = date.today()

    valor_parcela = round(valor / max(parcelas, 1), 2)
    categoria = detectar_categoria(descricao)
    parcelado = 1 if parcelas > 1 else 0

    # 🔥 gerar id único da compra
    compra_id = str(uuid.uuid4())

    # 🔹 define mês base da primeira parcela
    mes_base = hoje.month
    ano_base = hoje.year

    # se passou do fechamento → próxima fatura
    if hoje.day > dia_fechamento:
        mes_base += 1
        if mes_base > 12:
            mes_base = 1
            ano_base += 1

    # 🔹 registra apenas parcelas restantes
    for i in range(parcelas_pagas, parcelas):

        parcela_numero = i + 1

        mes_fatura = mes_base + (i - parcelas_pagas)
        ano_fatura = ano_base

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
        "valor_parcela": valor_parcela
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
    mes = agora.month
    ano = agora.year

    # busca vencimento do cartão ativo
    cursor.execute(
        """
        SELECT dia_vencimento
        FROM cartoes
        WHERE usuario_uuid = ?
          AND ativo = 1
        LIMIT 1
    """,
        (usuario_uuid,),
    )
    cartao = cursor.fetchone()

    # se já passou do vencimento, muda para próxima fatura
    if cartao and agora.day > cartao["dia_vencimento"]:
        mes += 1
        if mes == 13:
            mes = 1
            ano += 1

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

    agora = datetime.now()
    mes = agora.month
    ano = agora.year

    cursor.execute(
        """
        SELECT dia_fechamento
        FROM cartoes
        WHERE usuario_uuid = ?
          AND ativo = 1
        LIMIT 1
    """,
        (usuario_uuid,),
    )

    cartao = cursor.fetchone()

    if cartao and agora.day > cartao["dia_fechamento"]:
        mes += 1
        if mes == 13:
            mes = 1
            ano += 1

    # próxima fatura
    mes_proximo = mes + 1
    ano_proximo = ano

    if mes_proximo == 13:
        mes_proximo = 1
        ano_proximo += 1

    cursor.execute(
        """
        SELECT COALESCE(SUM(valor_parcela),0)
        FROM gastos_cartao
        WHERE usuario_uuid = ?
        AND mes_fatura = ?
        AND ano_fatura = ?
        AND quitado = 0
        AND parcelas_pagas < qtd_parcelas
        """,
        (usuario_uuid, mes, ano),
    )

    total_atual = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COALESCE(SUM(valor_parcela),0)
        FROM gastos_cartao
        WHERE usuario_uuid = ?
        AND mes_fatura = ?
        AND ano_fatura = ?
        AND quitado = 0
        AND parcelas_pagas < qtd_parcelas
        """,
        (usuario_uuid, mes_proximo, ano_proximo),
    )

    total_proximo = cursor.fetchone()[0]

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

    conn.close()

    return {
        "total_atual": float(total_atual),
        "total_proximo": float(total_proximo),
        "label_atual": meses[mes],
        "label_proximo": meses[mes_proximo],
    }


# ================= ATUALIZAR PARCELAS CARTÃO =================
def atualizar_parcelas(gasto, cursor):

    if not gasto["qtd_parcelas"]:
        return

    if gasto["quitado"]:
        return

    hoje = date.today()

    if not gasto["ultima_atualizacao"]:
        cursor.execute(
            """
            UPDATE gastos_cartao
            SET ultima_atualizacao = ?
            WHERE id = ?
        """,
            (hoje, gasto["id"]),
        )
        return

    ultima = date.fromisoformat(gasto["ultima_atualizacao"])

    meses_passados = (hoje.year - ultima.year) * 12 + (hoje.month - ultima.month)

    # evita atualização repetida no mesmo mês
    if meses_passados <= 0:
        return

    novas_pag = gasto["parcelas_pagas"] + meses_passados

    quitado = 0
    if novas_pag >= gasto["qtd_parcelas"]:
        novas_pag = gasto["qtd_parcelas"]
        quitado = 1

    # só atualiza se realmente mudou
    if novas_pag != gasto["parcelas_pagas"]:
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
