# ======================================================
# BIBLIOTECAS PADRÃO PYTHON
# ======================================================

from datetime import datetime, timedelta
from functools import wraps
from services.mensagens import msg_plano_premium_ativado


# ======================================================
# BIBLIOTECAS EXTERNAS
# ======================================================

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    jsonify,
)
from config import Config
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash


# ======================================================
# BANCO DE DADOS
# ======================================================

from db.database import get_connection


# ======================================================
# SERVICES
# ======================================================

from services.admin_service import (
    grafico_mes_usuario,
    grafico_pizza_gastos,
    total_gastos_sistema,
    total_premium,
    total_rendas_sistema,
    saldo_geral,
    resumo_usuario,
)

from services.categoria_auto import listar_categorias_auto
from admin_painel.extensions import csrf
from services.email_service import enviar_email_recuperacao

from services.conta_fixa_service import (
    listar_contas_fixas,
    total_contas_fixas_mes,
    remover_conta_fixa,
)

from services.cartao import calcular_faturas_cartao

from services.pagamentos_service import processar_pagamento
from services.permissoes import usuario_premium
from admin_painel.routes.cartao_routes import cartao_bp
from admin_painel.routes.gastos_routes import gastos_bp
from admin_painel.routes.admin_routes import admin_bp
from admin_painel.routes.usuario_routes import usuario_bp
from admin_painel.routes.auth_routes import auth_bp


# ======================================================
# MODELS
# ======================================================

from models.gasto import (
    apagar_gasto,
    editar_gasto,
    total_gastos_periodo,
    maiores_gastos_periodo,
)

from models.renda import (
    apagar_renda,
    editar_renda,
    total_rendas_periodo,
)

from models.categoria import (
    listar_categorias,
    criar_categoria,
    apagar_categoria,
)

from models.usuario import buscar_usuario_por_uuid


# ======================================================
# UTILS
# ======================================================

from utils.whatsapp import enviar_whatsapp
from utils.datetime_utils import agora_brasil
from utils.formatters import dinheiro


app = Flask(__name__)

app.secret_key = "finbot_admin_secret"

csrf.init_app(app)

app.register_blueprint(cartao_bp)
app.register_blueprint(gastos_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(auth_bp)

app.jinja_env.filters["dinheiro"] = dinheiro

from datetime import date


def atualizar_parcelas_automatico(db, gasto):

    if not gasto["qtd_parcelas"] or gasto["quitado"] == 1:
        return

    hoje = date.today()

    if not gasto["ultima_atualizacao"]:
        ultima = date.fromisoformat(gasto["data_compra"])
    else:
        ultima = date.fromisoformat(gasto["ultima_atualizacao"])

    meses_passados = (hoje.year - ultima.year) * 12 + (hoje.month - ultima.month)

    if meses_passados <= 0:
        return

    novas_pag = gasto["parcelas_pagas"] + meses_passados

    quitado = 0
    if novas_pag >= gasto["qtd_parcelas"]:
        novas_pag = gasto["qtd_parcelas"]
        quitado = 1

    db.execute(
        """
        UPDATE gastos_cartao
        SET parcelas_pagas = ?,
            quitado = ?,
            ultima_atualizacao = ?
        WHERE id = ?
    """,
        (novas_pag, quitado, hoje, gasto["id"]),
    )


# ======================================================
# DECORATORS DE AUTENTICAÇÃO
# ======================================================
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_uuid" not in session and "admin_uuid" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


def usuario_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_uuid" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admin_uuid" not in session:
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


# ======================================================
# CONEXÃO PADRÃO
# ======================================================
def get_db():
    return get_connection()


# ======================================================
# ADMIN — USUÁRIO INDIVIDUAL
# ======================================================
@app.route("/usuario/<uuid>")
@admin_required
def usuario_detalhe(uuid):
    db = get_db()
    usuario = db.execute(
        "SELECT * FROM usuarios WHERE uuid = ?",
        (uuid,),
    ).fetchone()

    if not usuario:
        return redirect(url_for("admin.painel"))

    return render_template(
        "usuario_painel.html",
        usuario=usuario,
        resumo=resumo_usuario(uuid),
        categorias=listar_categorias_auto(),
        contas_fixas=listar_contas_fixas(uuid),
    )


@app.route("/webhook/mercadopago", methods=["POST"])
@csrf.exempt
def webhook_mercadopago():

    data = request.json

    print("Webhook recebido:", data)

    if not data:
        return "ok"

    if data.get("type") != "payment":
        return "ok"

    payment_id = data.get("data", {}).get("id")

    if not payment_id:
        return "ok"

    processar_pagamento(payment_id)

    return "ok"


@app.route("/remover_premium/<uuid>")
@admin_required
def remover_premium(uuid):
    db = get_db()
    db.execute(
        """
        UPDATE usuarios
        SET plano = 'free',
            plano_expira_em = NULL
        WHERE uuid = ?
        """,
        (uuid,),
    )
    db.commit()
    db.close()
    return redirect(url_for("admin.painel"))


@app.route("/bloquear/<uuid>")
@admin_required
def bloquear_usuario(uuid):
    db = get_db()
    db.execute(
        "UPDATE usuarios SET status = 'bloqueado' WHERE uuid = ?",
        (uuid,),
    )
    db.commit()
    db.close()
    return redirect(url_for("admin.painel"))


@app.route("/desbloquear/<uuid>")
@admin_required
def desbloquear_usuario(uuid):
    db = get_db()
    db.execute(
        "UPDATE usuarios SET status = 'ativo' WHERE uuid = ?",
        (uuid,),
    )
    db.commit()
    db.close()
    return redirect(url_for("admin.painel"))


@app.route("/apagar_usuario/<uuid>")
@admin_required
def apagar_usuario(uuid):
    db = get_db()
    db.execute("DELETE FROM usuarios WHERE uuid = ?", (uuid,))
    db.commit()
    db.close()
    return redirect(url_for("admin.painel"))


@app.route("/admin/usuario/<uuid>")
@admin_required
def admin_usuario(uuid):

    db = get_db()

    pagina_gastos = request.args.get("pg", 1, type=int)
    pagina_rendas = request.args.get("pr", 1, type=int)

    limite = 10
    offset_gastos = (pagina_gastos - 1) * limite
    offset_rendas = (pagina_rendas - 1) * limite

    usuario = db.execute("SELECT * FROM usuarios WHERE uuid = ?", (uuid,)).fetchone()

    cartoes = db.execute(
        "SELECT * FROM cartoes WHERE usuario_uuid = ?", (uuid,)
    ).fetchall()

    gastos = db.execute(
        """
        SELECT *
        FROM gastos_cartao
        WHERE usuario_uuid = ?
        ORDER BY data_compra DESC
        LIMIT ? OFFSET ?
        """,
        (uuid, limite, offset_gastos),
    ).fetchall()

    rendas = db.execute(
        """
        SELECT *
        FROM rendas
        WHERE usuario_uuid = ?
        ORDER BY data DESC
        LIMIT ? OFFSET ?
        """,
        (uuid, limite, offset_rendas),
    ).fetchall()

    total_gastos = db.execute(
        "SELECT COUNT(*) FROM gastos_cartao WHERE usuario_uuid = ?", (uuid,)
    ).fetchone()[0]

    total_rendas = db.execute(
        "SELECT COUNT(*) FROM rendas WHERE usuario_uuid = ?", (uuid,)
    ).fetchone()[0]

    import math

    total_paginas_gastos = math.ceil(total_gastos / limite)
    total_paginas_rendas = math.ceil(total_rendas / limite)

    db.close()

    return render_template(
        "admin_usuario.html",
        usuario=usuario,
        cartoes=cartoes,
        gastos=gastos,
        rendas=rendas,
        pagina_gastos=pagina_gastos,
        pagina_rendas=pagina_rendas,
        total_gastos=total_gastos,
        total_rendas=total_rendas,
        total_paginas_gastos=total_paginas_gastos,
        total_paginas_rendas=total_paginas_rendas,
        limite=limite,
    )


@app.route("/admin/usuarios")
@admin_required
def admin_usuarios():

    db = get_db()

    usuarios = db.execute(
        """
        SELECT *
        FROM usuarios
        ORDER BY data_cadastro DESC
        """
    ).fetchall()

    # contadores
    total = len(usuarios)

    premium = sum(1 for u in usuarios if u["plano"] == "premium")

    bloqueados = sum(1 for u in usuarios if u["status"] == "bloqueado")

    db.close()

    return render_template(
        "admin_usuarios.html",
        usuarios=usuarios,
        total=total,
        premium=premium,
        bloqueados=bloqueados,
    )


@app.route("/resetar_cartao/<uuid>")
@admin_required
def resetar_cartao(uuid):

    db = get_db()

    db.execute(
        """
        DELETE FROM cartoes
        WHERE usuario_uuid = ?
        """,
        (uuid,),
    )

    db.commit()
    db.close()

    return redirect(url_for("admin.admin_usuarios"))


@app.route("/apagar_gastos/<uuid>")
@admin_required
def apagar_gastos(uuid):

    db = get_db()

    db.execute(
        """
        DELETE FROM gastos_cartao
        WHERE usuario_uuid = ?
        """,
        (uuid,),
    )

    db.commit()
    db.close()

    return redirect(url_for("admin.admin_usuarios"))


# ======================================================
# GRÁFICOS
# ======================================================
@app.route("/grafico/usuario")
@login_required
def grafico_usuario():
    usuario_uuid = session.get("usuario_uuid") or request.args.get("usuario")
    return grafico_mes_usuario(usuario_uuid)


@app.route("/grafico/pizza")
@login_required
def grafico_pizza():
    usuario_uuid = session.get("usuario_uuid") or request.args.get("usuario")
    return grafico_pizza_gastos(usuario_uuid)


# ======================================================
# SALVAR TODOS OS GASTOS
# ======================================================
@app.route("/gastos/salvar_todos", methods=["POST"])
@login_required
def salvar_todos_gastos():
    if "usuario_uuid" in session:
        usuario_uuid = session["usuario_uuid"]
    else:
        usuario_uuid = request.form.get("usuario_uuid")

    gasto_ids = request.form.getlist("gasto_id[]")
    descricoes = request.form.getlist("descricao[]")
    categorias = request.form.getlist("categoria[]")
    valores = request.form.getlist("valor[]")

    for i in range(len(gasto_ids)):
        editar_gasto(
            int(gasto_ids[i]),
            usuario_uuid,
            float(valores[i]),
            descricoes[i],
            categorias[i],
        )

    return redirect(request.referrer or "/usuario_painel")


# ======================================================
# START
# ======================================================
if __name__ == "__main__":
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_for=1)
    app.run(host="0.0.0.0", port=5001)
