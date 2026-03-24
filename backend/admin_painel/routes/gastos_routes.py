from flask import Blueprint, redirect, url_for, session, request
from admin_painel.decorators import usuario_required, login_required
from admin_painel.extensions import csrf

from models.gasto import apagar_gasto, editar_gasto
from models.renda import apagar_renda, editar_renda

gastos_bp = Blueprint("gastos", __name__)



# ======================================================
# GASTOS / RENDAS
# ======================================================
@gastos_bp.route("/gasto/apagar/<int:gasto_id>")
@usuario_required
def apagar_gasto_rota(gasto_id):
    apagar_gasto(gasto_id, session["usuario_uuid"])
    return redirect(url_for("usuario.usuario_painel"))


@gastos_bp.route("/renda/apagar/<int:renda_id>")
@usuario_required
def apagar_renda_rota(renda_id):
    apagar_renda(renda_id, session["usuario_uuid"])
    return redirect(url_for("usuario.usuario_painel"))


@gastos_bp.route("/gasto/editar/<int:gasto_id>", methods=["POST"])
@usuario_required
@csrf.exempt
def editar_gasto_rota(gasto_id):
    editar_gasto(
        gasto_id,
        session["usuario_uuid"],
        float(request.form.get("valor", 0)),
        request.form.get("descricao", ""),
        request.form.get("categoria"),
    )

    return redirect(url_for("usuario.usuario_painel"))


@gastos_bp.route("/renda/editar/<int:renda_id>", methods=["POST"])
@usuario_required
def editar_renda_rota(renda_id):
    editar_renda(
        renda_id,
        session["usuario_uuid"],
        float(request.form["valor"]),
        request.form["descricao"],
    )
    return redirect(url_for("usuario.usuario_painel"))
# ======================================================
# SALVAR TODOS OS GASTOS
# ======================================================
@gastos_bp.route("/gastos/salvar_todos", methods=["POST"])
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

    return redirect(request.referrer or url_for("usuario.usuario_painel"))
