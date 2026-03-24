from services.conta_fixa_service import (
    criar_conta_fixa,
    listar_contas_fixas,
    remover_conta_fixa,
)

from utils.formatters import parse_valor, dinheiro


def comando_conta_fixa(usuario_uuid, mensagem_original):

    texto = mensagem_original.replace("/contafixa", "").strip()

    if "|" not in texto:
        return (
            "📌 *Cadastrar conta fixa*\n\n"
            "Use o formato:\n"
            "/contafixa descrição | valor | categoria | mensal | dia\n\n"
            "Exemplo:\n"
            "/contafixa linha do celular | 35,00 | Contas Fixas | mensal | 15"
        )

    partes = [p.strip() for p in texto.split("|")]

    if len(partes) != 5:
        return "❌ Formato inválido. Use exatamente 5 campos separados por |"

    try:

        descricao = partes[0]
        valor = parse_valor(partes[1])
        categoria = partes[2]
        periodicidade = partes[3].lower()
        dia_vencimento = int(partes[4])

        if periodicidade not in ["mensal", "semanal", "anual"]:
            return "❌ Periodicidade inválida. Use: mensal, semanal ou anual."

        if not (1 <= dia_vencimento <= 31):
            return "❌ Dia de vencimento inválido. Use um número entre 1 e 31."

        criar_conta_fixa(
            usuario_uuid,
            descricao,
            valor,
            categoria,
            periodicidade,
            dia_vencimento,
        )

        return (
            "✅ *Conta fixa cadastrada com sucesso!*\n\n"
            f"📌 {descricao}\n"
            f"💰 R$ {dinheiro(valor)}\n"
            f"📅 Todo dia {dia_vencimento} ({periodicidade})"
        )

    except Exception as e:
        return f"❌ Erro ao cadastrar conta fixa:\n{str(e)}"


def comando_listar_contas(usuario_uuid):

    contas = listar_contas_fixas(usuario_uuid)

    if not contas:
        return "📭 Você não possui contas fixas cadastradas."

    resposta = "📌 *Suas contas fixas*\n\n"

    for c in contas:
        resposta += (
            f"#{c['id']} — {c['descricao']}\n"
            f"💰 R$ {dinheiro(c['valor'])}\n"
            f"📅 {c['periodicidade']} — dia {c['dia_vencimento']}\n\n"
        )

    return resposta


def comando_remover_conta(usuario_uuid, mensagem):

    try:

        conta_id = int(mensagem.replace("/removerconta", "").strip())

        removida = remover_conta_fixa(conta_id, usuario_uuid)

        if not removida:
            return (
                "❌ Conta não encontrada.\n\n"
                "Verifique o ID usando /fixas"
            )

        return "🗑️ Conta fixa removida com sucesso."

    except ValueError:
        return (
            "❌ Use o comando assim:\n"
            "/removerconta ID\n\n"
            "Exemplo:\n"
            "/removerconta 2"
        )