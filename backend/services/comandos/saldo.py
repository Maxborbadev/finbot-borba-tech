from models.usuario import buscar_usuario_por_uuid
from utils.formatters import dinheiro


def comando_saldo(usuario_uuid):

    usuario = buscar_usuario_por_uuid(usuario_uuid)
    saldo = usuario["saldo"]

    return (
        "💳 *Saldo atual*\n"
        "━━━━━━━━━━━━━━\n"
        f"💰 R$ {dinheiro(saldo)}\n\n"
        "📅 Atualizado em tempo real\n"
    )