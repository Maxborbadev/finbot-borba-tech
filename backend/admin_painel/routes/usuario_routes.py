from datetime import datetime
from flask import Blueprint, render_template, request, session, redirect, url_for
from admin_painel.decorators import usuario_required
from utils.datetime_utils import agora_brasil
from models.usuario import buscar_usuario_por_uuid
from models.gasto import total_gastos_periodo, maiores_gastos_periodo
from models.renda import total_rendas_periodo
from models.categoria import listar_categorias, criar_categoria, apagar_categoria
from datetime import timedelta

from db.database import get_connection
from services.admin_service import resumo_usuario
from services.categoria_auto import listar_categorias_auto
from services.conta_fixa_service import listar_contas_fixas, total_contas_fixas_mes
from services.cartao import calcular_faturas_cartao
from services.conta_fixa_service import remover_conta_fixa
from services.permissoes import usuario_premium

usuario_bp = Blueprint("usuario", __name__)


def get_db():
    return get_connection()


# ======================================================
# PAINEL USUÁRIO
# ======================================================
@usuario_bp.route("/usuario_painel")
@usuario_required
def usuario_painel():
    db = get_db()

    usuario = db.execute(
        "SELECT * FROM usuarios WHERE uuid = ?",
        (session["usuario_uuid"],),
    ).fetchone()

    # verificar se existe
    if not usuario:
        return redirect(url_for("logout"))

    usuario = dict(usuario)

    # verificar se premium
    if not usuario_premium(usuario["plano"]):
        return render_template("bloqueado.html", usuario=usuario)

    # calcular dias restantes
    if usuario["plano"] == "premium" and usuario["plano_expira_em"]:
        data = datetime.fromisoformat(usuario["plano_expira_em"])
        usuario["dias_restantes"] = (data - datetime.now()).days
    else:
        usuario["dias_restantes"] = None

    # ======================================================
    # 🔹 CALCULAR FATURAS DO CARTÃO (service)
    # ======================================================

    faturas = calcular_faturas_cartao(usuario["uuid"])

    # ======================================================
    # 🔹 RENDERIZA O PAINEL
    # ======================================================

    return render_template(
        "usuario_painel.html",
        usuario=usuario,
        resumo=resumo_usuario(usuario["uuid"]),
        categorias=listar_categorias_auto(),
        contas_fixas=listar_contas_fixas(usuario["uuid"]),
        total_fixas=total_contas_fixas_mes(usuario["uuid"]),
        total_cartao_atual=faturas["total_atual"],
        total_cartao_proximo=faturas["total_proximo"],
        fatura_label_atual=faturas["label_atual"],
        fatura_label_proximo=faturas["label_proximo"],
    )


# ======================================================
# PAGINA DE RESUMO DO USUARIO
# ======================================================
@usuario_bp.route("/resumo")
def resumo():

    usuario_uuid = session.get("usuario_uuid")

    if not usuario_uuid:
        return "Usuário não autenticado", 401

    usuario = buscar_usuario_por_uuid(usuario_uuid)

    saldo = usuario["saldo"]

    agora = agora_brasil()

    inicio_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_semana = agora - timedelta(days=7)
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    gastos_hoje = total_gastos_periodo(usuario_uuid, inicio_dia, agora)
    gastos_semana = total_gastos_periodo(usuario_uuid, inicio_semana, agora)
    gastos_mes = total_gastos_periodo(usuario_uuid, inicio_mes, agora)

    rendas_mes = total_rendas_periodo(usuario_uuid, inicio_mes, agora)

    maiores = maiores_gastos_periodo(usuario_uuid, inicio_mes, agora, 1)

    maior_gasto = maiores[0] if maiores else None

    return render_template(
        "resumo.html",
        saldo=saldo,
        gastos_hoje=gastos_hoje,
        gastos_semana=gastos_semana,
        gastos_mes=gastos_mes,
        rendas_mes=rendas_mes,
        maior_gasto=maior_gasto,
    )


# ======================================================
# CATEGORIAS
# ======================================================
@usuario_bp.route("/categorias")
@usuario_required
def categorias():
    return render_template(
        "categorias.html",
        categorias=listar_categorias(session["usuario_uuid"]),
    )


@usuario_bp.route("/categoria/criar", methods=["POST"])
@usuario_required
def criar_categoria_rota():
    criar_categoria(session["usuario_uuid"], request.form["nome"])
    return redirect(url_for("categorias"))


@usuario_bp.route("/categoria/apagar/<int:categoria_id>")
@usuario_required
def apagar_categoria_rota(categoria_id):
    apagar_categoria(categoria_id, session["usuario_uuid"])
    return redirect(url_for("categorias"))


# ======================================================
# CONTAS FIXAS
# ======================================================
@usuario_bp.route("/conta_fixa/apagar/<int:conta_id>")
@usuario_required
def remover_conta_fixa_rota(conta_id):
    remover_conta_fixa(conta_id, session["usuario_uuid"])
    return redirect(url_for("usuario.usuario_painel"))
