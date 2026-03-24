from models.usuario import listar_usuarios_ativos
from services.relatorio_service import (
    relatorio_semanal,
    relatorio_mensal
)


def enviar_relatorio_semanal():
    usuarios = listar_usuarios_ativos()

    for usuario in usuarios:
        mensagem = relatorio_semanal(usuario["id"])

        # AQUI futuramente entra WhatsApp
        print(f"[SEMANAL] Enviando para {usuario['telefone']}")
        print(mensagem)
        print("-" * 40)


def enviar_relatorio_mensal():
    usuarios = listar_usuarios_ativos()

    for usuario in usuarios:
        mensagem = relatorio_mensal(usuario["id"])

        print(f"[MENSAL] Enviando para {usuario['telefone']}")
        print(mensagem)
        print("-" * 40)
