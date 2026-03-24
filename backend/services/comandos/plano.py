from models.usuario import buscar_usuario_por_uuid
from services import mensagens


def comando_plano(usuario_uuid):

    usuario = buscar_usuario_por_uuid(usuario_uuid)

    plano = usuario["plano"]
    expira = usuario["plano_expira_em"]

    if plano == "premium":
        return mensagens.msg_plano_premium(expira)

    return mensagens.msg_plano_free()