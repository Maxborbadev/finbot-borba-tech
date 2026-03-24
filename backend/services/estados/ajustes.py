from db.database import get_connection
from utils.formatters import parse_valor, dinheiro

from models.usuario import atualizar_salario, atualizar_saldo


def estado_ajustar_salario(usuario_uuid, mensagem_original):

    try:
        valor = parse_valor(mensagem_original)
    except Exception:
        return "❌ Valor inválido. Exemplo: 3500 ou 3.500"

    atualizar_salario(usuario_uuid, valor)

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'ativo' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return (
        "✅ *Salário atualizado com sucesso!*\n\n"
        f"💼 Novo salário mensal: R$ {dinheiro(valor)}"
    )


def estado_ajustar_saldo(usuario_uuid, mensagem_original):

    try:
        valor = parse_valor(mensagem_original)
    except Exception:
        return "❌ Valor inválido. Exemplo: 1250 ou 1.250"

    atualizar_saldo(usuario_uuid, valor)

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'ativo' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return (
        "✅ *Saldo atualizado com sucesso!*\n\n"
        f"💳 Saldo atual em mãos: R$ {dinheiro(valor)}"
    )