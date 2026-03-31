import re

from utils.formatters import parse_valor, dinheiro
from services import mensagens
from services.categoria_auto import detectar_categoria
from datetime import datetime
from db.database import get_connection

from models.usuario import buscar_usuario_por_uuid
from models.gasto import registrar_gasto
from models.renda import registrar_renda
from services.mensagens import msg_limite_atingido, msg_aviso_limite
from services.comandos.cartao import processar_cartao


PALAVRAS_GASTO = [
    "gastei",
    "paguei",
    "comprei",
    "gasto",
    "pago",
]

PALAVRAS_RENDA = [
    "recebi",
    "ganhei",
    "ganho",
    "recebido",
]


def contar_lancamentos_mes(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    agora = datetime.now()
    mes = agora.month
    ano = agora.year

    # Contar gastos (compras)
    cursor.execute(
        """
        SELECT COUNT(*) as total
        FROM compras
        WHERE usuario_uuid = ?
        AND strftime('%m', data) = ?
        AND strftime('%Y', data) = ?
    """,
        (usuario_uuid, f"{mes:02d}", str(ano)),
    )

    total_gastos = cursor.fetchone()["total"]

    # Contar rendas
    cursor.execute(
        """
        SELECT COUNT(*) as total
        FROM rendas
        WHERE usuario_uuid = ?
        AND strftime('%m', data) = ?
        AND strftime('%Y', data) = ?
    """,
        (usuario_uuid, f"{mes:02d}", str(ano)),
    )

    total_rendas = cursor.fetchone()["total"]

    conn.close()

    return total_gastos + total_rendas


def detectar_valor(texto):

    numeros = re.findall(r"\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:[.,]\d+)?", texto)

    if not numeros:
        return None

    try:
        return parse_valor(numeros[0])
    except Exception:
        return None


def detectar_intencao(texto):

    for palavra in PALAVRAS_RENDA:
        if palavra in texto:
            return "renda"

    for palavra in PALAVRAS_GASTO:
        if palavra in texto:
            return "gasto"

    return None


def extrair_descricao(texto_original):

    descricao = re.sub(
        r"\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:[.,]\d+)?", "", texto_original
    )

    descricao = re.sub(
        r"^(cartao|cartão|gastei|paguei|comprei|pix|recebi|ganhei)\s*",
        "",
        descricao,
        flags=re.IGNORECASE,
    )

    return descricao.strip()


def processar_lancamento(
    usuario_uuid, mensagem, mensagem_original, buscar_cartao_ativo
):
    # =========================
    # CONTROLE DE LIMITE POR PLANO
    # =========================
    usuario = buscar_usuario_por_uuid(usuario_uuid)
    plano = usuario["plano"]

    from db.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM planos WHERE nome = ?", (plano,))
    plano_dados = cursor.fetchone()
    conn.close()

    # Segurança: se não achar plano
    if not plano_dados:
        limite = 10  # fallback FREE
    else:
        limite = plano_dados["limite_mensal"]

    total = contar_lancamentos_mes(usuario_uuid)

    # BLOQUEIO
    if total >= limite:
        return msg_limite_atingido()

    # AVISO (faltando 3)
    restantes = limite - total
    aviso_limite = None

    if restantes == 3:
        aviso_limite = msg_aviso_limite()

    # =========================
    # COMANDO CARTAO
    # =========================
    if mensagem.startswith("cartao") or mensagem.startswith("cartão"):

        resposta = processar_cartao(
            usuario_uuid, mensagem_original, buscar_cartao_ativo
        )

        if resposta:
            return resposta

    valor = detectar_valor(mensagem)

    if not valor:
        return (
            "❌ Não encontrei o valor na sua mensagem.\n\n"
            "Digite o valor junto com a descrição.\n\n"
            "Exemplos:\n"
            "• gastei 35 mercado\n"
            "• recebi 500 freelance\n"
            "• cartão 200 ifood"
        )

    texto_sem_numero = re.sub(
        r"\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:[.,]\d+)?", "", mensagem_original
    ).strip()

    if texto_sem_numero == "":
        return (
            "Você enviou apenas um valor.\n\n"
            "Diga o que aconteceu com esse valor.\n\n"
            "Exemplos:\n"
            "• gastei 50 mercado\n"
            "• recebi 120 freelance\n"
            "• cartão 30 lanche"
        )

    descricao = extrair_descricao(mensagem_original)

    # =========================
    # RENDA
    # =========================
    intencao = detectar_intencao(mensagem)

    if not intencao:
        intencao = "gasto"

    # =========================
    # RENDA
    # =========================
    if intencao == "renda":

        registrar_renda(usuario_uuid, valor, descricao)

        usuario_atualizado = buscar_usuario_por_uuid(usuario_uuid)

        saldo_atual = usuario_atualizado["saldo"]

        resposta = mensagens.msg_renda_registrada(
            descricao, dinheiro(valor), dinheiro(saldo_atual)
        )

        if aviso_limite:
            resposta += "\n\n" + aviso_limite

        return resposta

    # =========================
    # GASTO
    # =========================
    if intencao == "gasto":

        categoria = detectar_categoria(mensagem_original)

        registrar_gasto(usuario_uuid, valor, descricao, categoria)

        usuario_atualizado = buscar_usuario_por_uuid(usuario_uuid)

        saldo_atual = usuario_atualizado["saldo"]

        resposta = mensagens.msg_gasto_registrado(
            descricao, categoria, dinheiro(valor), dinheiro(saldo_atual)
        )

        if aviso_limite:
            resposta += "\n\n" + aviso_limite

        return resposta
