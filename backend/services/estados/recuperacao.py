# ======================================================
# RECUPERAÇÃO DE SENHA
# ======================================================

from db.database import get_connection
from services.comandos.recuperar_senha import gerar_link_recuperacao


def estado_aguardando_recuperacao_email(usuario_uuid, mensagem):

    email = mensagem.strip()

    link = gerar_link_recuperacao(email)
    if link == "limite_excedido":
        return "⚠️ Você solicitou muitas recuperações recentemente. Aguarde um pouco antes de tentar novamente."

    conn = get_connection()

    conn.execute(
        """
        UPDATE usuarios
        SET estado = 'ativo'
        WHERE uuid = ?
        """,
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    if not link:
        return "❌ Email não encontrado. Verifique e tente novamente."

    return f"""🔑 Recuperação de senha

Clique no link abaixo para redefinir sua senha:

{link}

Este link expira em 30 minutos."""
