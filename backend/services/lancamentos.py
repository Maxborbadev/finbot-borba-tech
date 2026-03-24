import re

from utils.formatters import parse_valor, dinheiro
from services import mensagens
from services.categoria_auto import detectar_categoria

from models.usuario import buscar_usuario_por_uuid
from models.gasto import registrar_gasto
from models.renda import registrar_renda

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

        return mensagens.msg_renda_registrada(
            descricao, dinheiro(valor), dinheiro(saldo_atual)
        )

    # =========================
    # GASTO
    # =========================
    if intencao == "gasto":

        categoria = detectar_categoria(mensagem_original)

        registrar_gasto(usuario_uuid, valor, descricao, categoria)

        usuario_atualizado = buscar_usuario_por_uuid(usuario_uuid)

        saldo_atual = usuario_atualizado["saldo"]

        return mensagens.msg_gasto_registrado(
            descricao, categoria, dinheiro(valor), dinheiro(saldo_atual)
        )
