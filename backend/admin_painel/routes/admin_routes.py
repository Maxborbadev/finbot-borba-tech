from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for
from admin_painel.decorators import admin_required
from admin_painel.extensions import csrf

from db.database import get_connection
from utils.whatsapp import enviar_whatsapp
from services.admin_service import (
    total_gastos_sistema,
    total_premium,
    total_rendas_sistema,
    saldo_geral,
)

from services.mensagens import msg_plano_premium_ativado
from services.mensagens import msg_premium_gratis_7_dias
from services.pagamentos_service import processar_pagamento
from models.usuario import buscar_usuario_por_uuid

admin_bp = Blueprint("admin", __name__)

def get_db():
    return get_connection()



# ======================================================
# PAINEL ADMIN
# ======================================================
@admin_bp.route("/painel")
@admin_required
def painel():

    db = get_db()

    usuarios = db.execute(
        "SELECT * FROM usuarios ORDER BY data_cadastro DESC"
    ).fetchall()

    usuarios = [dict(u) for u in usuarios]

    for u in usuarios:

        if u["plano_expira_em"]:

            data = datetime.fromisoformat(u["plano_expira_em"])

            u["expira_formatado"] = data.strftime("%d/%m/%Y")

            u["dias_restantes"] = (data - datetime.now()).days

        else:

            u["expira_formatado"] = None
            u["dias_restantes"] = None

    # ----------------------------
    # TOTAL PREMIUM
    # ----------------------------

    premium = total_premium()

    # ----------------------------
    # NOVOS USUÁRIOS HOJE
    # ----------------------------

    novos_hoje = db.execute(
        """
        SELECT COUNT(*)
        FROM usuarios
        WHERE DATE(data_cadastro) = DATE('now')
        """
    ).fetchone()[0]

    # ----------------------------
    # PREMIUM EXPIRANDO EM 7 DIAS
    # ----------------------------

    expiram = db.execute(
        """
        SELECT COUNT(*)
        FROM usuarios
        WHERE plano = 'premium'
        AND plano_expira_em <= DATE('now','+7 day')
        """
    ).fetchone()[0]

    # ----------------------------
    # USUÁRIOS ATIVOS HOJE
    # ----------------------------

    ativos_hoje = db.execute(
        """
        SELECT COUNT(DISTINCT usuario_uuid)
        FROM rendas
        WHERE DATE(data) = DATE('now')
        """
    ).fetchone()[0]

    # ----------------------------
    # RECEITA ESTIMADA
    # ----------------------------

    receita = round(premium * 6.99, 2)

    db.close()

    return render_template(
        "admin_painel.html",
        usuarios=usuarios,
        total=len(usuarios),
        free=len([u for u in usuarios if u["plano"] == "free"]),
        premium=premium,
        gastos=total_gastos_sistema(),
        rendas=total_rendas_sistema(),
        saldo=saldo_geral(),
        novos_hoje=novos_hoje,
        ativos_hoje=ativos_hoje,
        expiram=expiram,
        receita=receita,
    )

# ======================================================
# AÇÕES ADMIN
# ======================================================
@admin_bp.route("/admin/aviso")
@admin_required
def admin_aviso():

    return render_template("admin_aviso.html")


@admin_bp.route("/admin/enviar_aviso", methods=["POST"])
@csrf.exempt
@admin_required
def enviar_aviso():

    tipo = request.form["tipo"]
    mensagem = request.form["mensagem"]

    db = get_db()

    if tipo == "todos":

        usuarios = db.execute(
            "SELECT whatsapp_id FROM usuarios WHERE status='ativo' AND estado='ativo'"
        ).fetchall()

    elif tipo == "premium":

        usuarios = db.execute(
            "SELECT whatsapp_id FROM usuarios WHERE plano='premium' AND status='ativo' AND estado='ativo'"
        ).fetchall()

    elif tipo == "free":

        usuarios = db.execute(
            "SELECT whatsapp_id FROM usuarios WHERE plano='free' AND status='ativo' AND estado='ativo'"
        ).fetchall()

    elif tipo == "expirando":

        usuarios = db.execute(
            """
            SELECT whatsapp_id
            FROM usuarios
            WHERE plano='premium'
            AND status='ativo'
            AND estado='ativo'
            AND plano_expira_em <= DATE('now','+7 day')
            """
        ).fetchall()

    db.close()

    for u in usuarios:

        numero = u["whatsapp_id"]

        if not numero:
            continue

        numero = u["whatsapp_id"]

        print("Enviando aviso para:", numero)

        enviar_whatsapp(numero, mensagem)

        import time

        time.sleep(0.3)

    return redirect(url_for("admin.painel"))


@admin_bp.route("/ativar_premium/<uuid>")
@admin_required
def ativar_premium(uuid):

    db = get_db()

    expira = datetime.now() + timedelta(days=30)

    db.execute(
        """
        UPDATE usuarios
        SET plano = 'premium',
            plano_expira_em = ?,
            origem_premium = 'gratis'
        WHERE uuid = ?
        """,
        (expira, uuid),
    )

    usuario = db.execute(
        "SELECT whatsapp_id FROM usuarios WHERE uuid = ?", (uuid,)
    ).fetchone()

    db.commit()
    db.close()

    if usuario:
        whatsapp_id = usuario["whatsapp_id"]

        mensagem = msg_plano_premium_ativado(expira)

        enviar_whatsapp(whatsapp_id, mensagem)

    return redirect(url_for("admin.painel"))

@admin_bp.route("/remover_premium/<uuid>")
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


@admin_bp.route("/bloquear/<uuid>")
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


@admin_bp.route("/desbloquear/<uuid>")
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


@admin_bp.route("/apagar_usuario/<uuid>")
@admin_required
def apagar_usuario(uuid):
    db = get_db()
    db.execute("DELETE FROM usuarios WHERE uuid = ?", (uuid,))
    db.commit()
    db.close()
    return redirect(url_for("admin.painel"))


@admin_bp.route("/admin/usuario/<uuid>")
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


@admin_bp.route("/admin/usuarios")
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


@admin_bp.route("/resetar_cartao/<uuid>")
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


@admin_bp.route("/apagar_gastos/<uuid>")
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


@admin_bp.route("/apagar_rendas/<uuid>")
@admin_required
def apagar_rendas(uuid):

    db = get_db()

    db.execute(
        """
        DELETE FROM rendas
        WHERE usuario_uuid = ?
        """,
        (uuid,),
    )

    db.commit()
    db.close()

    return redirect(url_for("admin.admin_usuarios"))

@admin_bp.route("/admin/premium-hoje", methods=["POST"])
@csrf.exempt
@admin_required
def dar_premium_hoje():

    db = get_db()

    from datetime import datetime, timedelta
    from utils.whatsapp import enviar_whatsapp
    from services.mensagens import msg_premium_gratis_7_dias
    import time

    expira = datetime.now() + timedelta(days=7)

    # 🔍 pega usuários de hoje (evita duplicar)
    usuarios = db.execute(
        """
        SELECT uuid, whatsapp_id
        FROM usuarios
        WHERE DATE(data_cadastro) = DATE('now')
        AND plano != 'premium'
        AND origem_premium IS NULL
        """
    ).fetchall()

    afetados = 0

    for u in usuarios:

        # ativa premium
        db.execute(
            """
            UPDATE usuarios
            SET plano = 'premium',
                plano_expira_em = ?,
                origem_premium = 'gratis'
            WHERE uuid = ?
            """,
            (expira, u["uuid"])
        )

        # envia mensagem correta (7 dias grátis)
        if u["whatsapp_id"]:
            mensagem = msg_premium_gratis_7_dias(expira)
            enviar_whatsapp(u["whatsapp_id"], mensagem)
            time.sleep(0.3)  # evita bloqueio

        afetados += 1

    db.commit()
    db.close()

    return {
        "status": "ok",
        "msg": f"{afetados} usuários receberam 7 dias grátis"
    }