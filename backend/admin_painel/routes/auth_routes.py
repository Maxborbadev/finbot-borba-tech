from flask import Blueprint, render_template, request, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import secrets

from config import Config
from services.email_service import enviar_email_recuperacao
from db.database import get_connection
from admin_painel.extensions import csrf

auth_bp = Blueprint("auth", __name__)


def get_db():
    return get_connection()


# ======================================================
# LOGIN
# ======================================================
@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        db = get_db()

        ip = request.remote_addr

        # ==========================================
        # VERIFICAR TENTATIVAS RECENTES
        # ==========================================
        tentativas = db.execute(
            """
            SELECT COUNT(*) as total
            FROM tentativas_login
            WHERE email = ?
            AND data >= datetime('now','-10 minutes')
            """,
            (email,),
        ).fetchone()

        if tentativas["total"] >= 5:
            return render_template(
                "login.html", erro="Muitas tentativas de login. Aguarde 10 minutos."
            )

        user = db.execute(
            "SELECT * FROM usuarios WHERE email = ? AND status = 'ativo'",
            (email,),
        ).fetchone()

        # ==========================================
        # LOGIN CORRETO
        # ==========================================
        if user and check_password_hash(user["senha"], senha):

            session.clear()

            # limpa tentativas antigas
            db.execute("DELETE FROM tentativas_login WHERE email = ?", (email,))

            db.commit()

            if user["tipo_usuario"] == "admin":
                session["admin_uuid"] = user["uuid"]
                return redirect(url_for("admin.painel"))
            else:
                session["usuario_uuid"] = user["uuid"]
                return redirect(url_for("usuario.usuario_painel"))

        # ==========================================
        # REGISTRAR TENTATIVA ERRADA
        # ==========================================
        db.execute(
            """
            INSERT INTO tentativas_login (email, ip)
            VALUES (?, ?)
            """,
            (email, ip),
        )

        db.commit()

        return render_template("login.html", erro="Credenciais inválidas")

    return render_template("login.html")


# ======================================================
# LOGOUT
# ======================================================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# ======================================================
# ESQUECI SENHA
# ======================================================
@auth_bp.route("/esqueci-senha")
def esqueci_senha():
    return render_template("recuperar_senha.html")


# ======================================================
# GERAR TOKEN DE RECUPERAÇÃO
# ======================================================
import secrets


@auth_bp.route("/enviar-recuperacao", methods=["POST"])
@csrf.exempt
def enviar_recuperacao():

    email = request.form.get("email")

    db = get_db()

    usuario = db.execute(
        "SELECT uuid FROM usuarios WHERE email = ?", (email,)
    ).fetchone()

    # só gera token se usuário existir
    if usuario:

        token = secrets.token_urlsafe(32)

        expira = datetime.now() + timedelta(minutes=30)

        db.execute(
            """
            INSERT INTO recuperacao_senha (email, token, expira_em)
            VALUES (?, ?, ?)
            """,
            (email, token, expira),
        )

        db.commit()

        link = f"{Config.BASE_URL}/resetar-senha/{token}"

        print("LINK RECUPERAÇÃO:", link)

        enviar_email_recuperacao(email, link)

    db.close()

    # sempre mostra toast (segurança)
    return render_template("recuperar_senha.html", enviado=True)


# ======================================================
# ABRIR PÁGINA DE NOVA SENHA
# ======================================================
@auth_bp.route("/resetar-senha/<token>")
def resetar_senha(token):

    db = get_db()

    registro = db.execute(
        """
        SELECT *
        FROM recuperacao_senha
        WHERE token = ?
        """,
        (token,),
    ).fetchone()

    if not registro:
        db.close()
        return "Link inválido"

    # verificar se já foi usado
    if registro["usado"] == 1:
        db.close()
        return "Este link já foi utilizado"

    # verificar expiração
    expira = datetime.fromisoformat(registro["expira_em"])

    if datetime.now() > expira:
        db.close()
        return "Este link expirou"

    db.close()

    return render_template("nova_senha.html", token=token)


# ======================================================
# SALVAR NOVA SENHA
# ======================================================
@auth_bp.route("/salvar-nova-senha", methods=["POST"])
@csrf.exempt
def salvar_nova_senha():

    token = request.form.get("token")
    senha = request.form.get("senha")
    confirmar = request.form.get("confirmar")
    # valida senha mínima
    if not senha or len(senha) < 6:
        return render_template(
            "nova_senha.html",
            token=token,
            erro="A senha deve ter pelo menos 6 caracteres.",
        )

    # valida confirmação
    if senha != confirmar:
        return render_template(
            "nova_senha.html", token=token, erro="As senhas não coincidem."
        )

    db = get_db()

    registro = db.execute(
        """
        SELECT *
        FROM recuperacao_senha
        WHERE token = ?
        AND usado = 0
        """,
        (token,),
    ).fetchone()

    if not registro:
        db.close()
        return "Token inválido"

    # verifica expiração
    expira = datetime.fromisoformat(registro["expira_em"])

    if datetime.now() > expira:
        db.close()
        return "Link expirado"

    email = registro["email"]

    from werkzeug.security import generate_password_hash

    senha_hash = generate_password_hash(senha)

    db.execute(
        """
        UPDATE usuarios
        SET senha = ?
        WHERE email = ?
        """,
        (senha_hash, email),
    )

    db.execute(
        """
        UPDATE recuperacao_senha
        SET usado = 1
        WHERE token = ?
        """,
        (token,),
    )

    db.commit()
    db.close()

    return render_template("nova_senha.html", sucesso=True)
