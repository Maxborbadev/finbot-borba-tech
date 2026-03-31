from db.database import get_connection
from services.comandos.upgrade import comando_upgrade_escolha


def estado_escolhendo_plano(usuario_uuid, mensagem, usuario):

    # ESCOLHA DE PLANO
    if mensagem in ["1", "2"]:
        return comando_upgrade_escolha(usuario, mensagem)

    # CANCELAR
    if mensagem in ["0", "sair", "cancelar"]:
        db = get_connection()
        db.execute(
            "UPDATE usuarios SET estado = 'ativo' WHERE uuid = ?",
            (usuario_uuid,),
        )
        db.commit()
        db.close()

        return "❌ Operação cancelada."

    return "❌ Opção inválida. Digite 1, 2 ou 0 para cancelar."