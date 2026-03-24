from datetime import datetime
from db.database import get_connection
from utils.fatura import competencia_fatura_pdf
from utils.formatters import dinheiro
from services.pdf import gerar_pdf_fatura


def comando_fatura(usuario_uuid):

    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 BUSCAR DADOS DO CARTÃO
    cursor.execute(
        """
        SELECT nome,dia_fechamento, dia_vencimento
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
        return "💳 Você ainda não tem um cartão cadastrado.\n\n👉 Use o comando /novocartao para adicionar um.", None
    nome_cartao = cartao['nome']
    dia_fechamento = cartao["dia_fechamento"]
    dia_vencimento = cartao["dia_vencimento"]

    # 🔹 DEFINIR COMPETÊNCIA CORRETA DA FATURA (PDF)
    mes, ano, label = competencia_fatura_pdf(dia_fechamento, dia_vencimento)

    # 🔹 BUSCAR GASTOS CORRETOS
    cursor.execute(
        """
        SELECT descricao, valor, valor_parcela, parcelado,
               parcela_numero, qtd_parcelas, categoria, data_compra
        FROM gastos_cartao
        WHERE usuario_uuid = ?
        AND mes_fatura = ?
        AND ano_fatura = ?
        ORDER BY data_compra DESC
        """,
        (usuario_uuid, mes, ano),
    )

    gastos = cursor.fetchall()

    if not gastos:
        conn.close()
        return "Sua fatura está vazia nesse período 📄", None

    # 🔹 CALCULAR TOTAL CORRETO
    cursor.execute(
        """
        SELECT COALESCE(SUM(valor_parcela), 0)
        FROM gastos_cartao
        WHERE usuario_uuid = ?
        AND mes_fatura = ?
        AND ano_fatura = ?
    """,
        (usuario_uuid, mes, ano),
    )

    total = cursor.fetchone()[0]

    conn.close()

    # 🔹 ORGANIZAR POR CATEGORIA
    gastos_por_categoria = {}

    for g in gastos:
        categoria = g["categoria"] or "Outros"

        if categoria not in gastos_por_categoria:
            gastos_por_categoria[categoria] = []

        gastos_por_categoria[categoria].append(g)

    # 🔹 GERAR PDF
    pdf_path = None

    try:
        pdf_path = gerar_pdf_fatura(usuario_uuid, gastos_por_categoria, total, label,nome_cartao)
    except Exception as e:
        print("Erro ao gerar PDF:", e)
        return "Erro ao gerar sua fatura 😓", None

    return None, pdf_path
