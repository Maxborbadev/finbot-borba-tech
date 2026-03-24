from utils.formatters import parse_valor, dinheiro
from models.cofrinho import registrar_cofrinho, obter_total_cofrinho
from models.cofrinho import definir_total_cofrinho

def processar_cofrinho(usuario_uuid, mensagem_original):

    texto = mensagem_original.replace("/cofrinho", "").strip()

    if not texto:
        return (
            "🐷 *Cofrinho*\n\n"
            "Informe o valor que deseja guardar.\n\n"
            "Exemplo:\n"
            "/cofrinho 150"
        )

    try:
        valor = parse_valor(texto)
    except Exception:
        return "❌ Valor inválido. Exemplo: 150 ou 150,50"

    registrar_cofrinho(usuario_uuid, valor)

    total = obter_total_cofrinho(usuario_uuid)

    return (
        "🐷 *Valor guardado com sucesso!*\n\n"
        f"💰 Guardado agora: R$ {dinheiro(valor)}\n"
        f"📦 Total no cofrinho: R$ {dinheiro(total)}"
    )

def processar_attcofre(usuario_uuid, mensagem_original):

    texto = mensagem_original.replace("/attcofre", "").strip()

    if not texto:
        return "Informe o novo valor total.\nExemplo: /attcofre 1500"

    try:
        novo_total = parse_valor(texto)
    except Exception:
        return "Valor inválido."

    definir_total_cofrinho(usuario_uuid, novo_total)

    return (
        "🐷 Cofrinho atualizado com sucesso!\n\n"
        f"Novo total: R$ {dinheiro(novo_total)}"
    )

from utils.formatters import parse_valor, dinheiro
from models.cofrinho import registrar_cofrinho, obter_total_cofrinho
from models.cofrinho import definir_total_cofrinho


def comando_cofrinho(usuario_uuid, mensagem_original):

    if mensagem_original.startswith("/cofrinho"):
        return processar_cofrinho(usuario_uuid, mensagem_original)

    if mensagem_original.startswith("/attcofre"):
        return processar_attcofre(usuario_uuid, mensagem_original)

    return None