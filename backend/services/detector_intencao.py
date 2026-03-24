import re

# =========================
# PADRÕES DE GASTOS
# =========================
PADRAO_GASTOS = re.compile(
    r"\b("
    r"gastei|gasto|gastou|"
    r"paguei|pago|pagamento|pagou|"
    r"comprei|compra|compramos|"
    r"transferi|transferência|"
    r"mandei|enviei|"
    r"anota|anotar|anotei|"
    r"marca|marcar|"
    r"coloca|colocar|"
    r"registra|registrar|"
    r"debitei|debitar|"
    r"cobrou|cobrança|"
    r"passou no crédito|passou no debito|"
    r"débito|debito"
    r")\b"
)

PADRAO_PIX_SAIDA = re.compile(r"\bpix\b")


# =========================
# PADRÕES DE RENDA
# =========================
PADRAO_RENDA = re.compile(
    r"\b("
    r"recebi|recebimento|"
    r"ganhei|ganho|"
    r"entrou|entrada|"
    r"depositaram|deposito|depósito|"
    r"salário|salario|"
    r"pagamento recebido|"
    r"caiu na conta|"
    r"fiz uma venda|vendi|venda|"
    r"comissão|comissao|"
    r"reembolso|"
    r"retorno"
    r")\b"
)

PADRAO_PIX_ENTRADA = re.compile(r"\bpix recebido\b|\bpix entrou\b")


# =========================
# FUNÇÕES
# =========================

def eh_registro_gasto(mensagem: str) -> bool:
    mensagem = mensagem.lower()
    return bool(PADRAO_GASTOS.search(mensagem) or PADRAO_PIX_SAIDA.search(mensagem))


def eh_registro_renda(mensagem: str) -> bool:
    mensagem = mensagem.lower()
    return bool(PADRAO_RENDA.search(mensagem) or PADRAO_PIX_ENTRADA.search(mensagem))
