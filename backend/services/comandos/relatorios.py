from services.relatorio_service import (
    relatorio_diario,
    relatorio_semanal,
    relatorio_mensal,
    relatorio_avancado,
)


def comando_relatorio_diario(usuario_uuid):
    return relatorio_diario(usuario_uuid)


def comando_relatorio_semanal(usuario_uuid):
    return relatorio_semanal(usuario_uuid)


def comando_relatorio_mensal(usuario_uuid):
    try:
        return relatorio_mensal(usuario_uuid)
    except Exception as e:
        return f"❌ Erro no relatório mensal:\n{str(e)}"


def comando_relatorio_avancado(usuario_uuid):
    try:
        return relatorio_avancado(usuario_uuid)
    except Exception as e:
        return f"❌ Erro no relatório avançado:\n{str(e)}"