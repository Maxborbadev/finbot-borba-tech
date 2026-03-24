import secrets
from datetime import datetime, timedelta
from db.database import get_connection
from services.email_service import enviar_email_recuperacao
from config import Config


def gerar_link_recuperacao(email):

    db = get_connection()

    # ==========================================
    # INVALIDAR TOKENS ANTIGOS
    # ==========================================

    db.execute(
        """
        DELETE FROM recuperacao_senha
        WHERE email = ?
        """,
        (email,)
    )

    # ==========================================
    # LIMITE DE RECUPERAÇÃO (3 POR HORA)
    # ==========================================

    limite = db.execute(
        """
        SELECT COUNT(*) as total
        FROM recuperacao_senha
        WHERE email = ?
        AND criado_em >= datetime('now', '-1 hour')
        """,
        (email,)
    ).fetchone()

    if limite["total"] >= 3:
        db.close()
        return "limite_excedido"

    usuario = db.execute(
        "SELECT email FROM usuarios WHERE email = ?",
        (email,)
    ).fetchone()

    if not usuario:
        db.close()
        return None

    token = secrets.token_urlsafe(32)

    expira = datetime.now() + timedelta(minutes=30)

    db.execute(
        """
        INSERT INTO recuperacao_senha (email, token, expira_em)
        VALUES (?, ?, ?)
        """,
        (email, token, expira)
    )

    db.commit()
    db.close()

    link = f"{Config.BASE_URL}/resetar-senha/{token}"
    enviar_email_recuperacao(email, link)

    return link




def comando_recuperar_senha(usuario_uuid):

    conn = get_connection()

    usuario = conn.execute(
        """
        SELECT email
        FROM usuarios
        WHERE uuid = ?
        """,
        (usuario_uuid,)
    ).fetchone()

    if not usuario or not usuario["email"]:
        conn.close()
        return "❌ Não encontramos um email cadastrado na sua conta."

    email = usuario["email"]

    conn.close()

    link = gerar_link_recuperacao(email)

    if link == "limite_excedido":
        return "⚠️ Você solicitou muitas recuperações recentemente. Aguarde um pouco antes de tentar novamente."

    return f"""🔑 Recuperação de senha

Clique no link abaixo para redefinir sua senha:

{link}

Este link expira em 30 minutos."""