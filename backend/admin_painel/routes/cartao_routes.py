from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    url_for,
    jsonify,
)

# ========================================================
from admin_painel.decorators import usuario_required
from admin_painel.extensions import csrf

# ========================================================
from db.database import get_connection
from services.cartao import calcular_faturas_cartao
from services.cartao import atualizar_parcelas
from services.cartao import total_cartao_fatura_atual
from utils.fatura import calcular_competencia_fatura, gerar_label_fatura
from datetime import datetime

# ========================================================
cartao_bp = Blueprint("cartao", __name__)


# ========================================================
def get_db():
    return get_connection()


# ========================================================


@cartao_bp.route("/cartoes")
@usuario_required
def cartoes_painel():
    db = get_db()

    # 🔹 Usuário logado
    usuario = db.execute(
        "SELECT * FROM usuarios WHERE uuid = ?",
        (session["usuario_uuid"],),
    ).fetchone()

    # 🔹 Lista cartões
    cartoes = db.execute(
        """
        SELECT id, nome
        FROM cartoes
        WHERE usuario_uuid = ?
        ORDER BY data_criacao DESC
        """,
        (session["usuario_uuid"],),
    ).fetchall()

    # 🔹 Atualizar parcelas automaticamente
    todos = db.execute(
        """
        SELECT *
        FROM gastos_cartao
        WHERE usuario_uuid = ?
        """,
        (session["usuario_uuid"],),
    ).fetchall()

    cursor = db.cursor()
    cursor.execute(
        """
    SELECT dia_vencimento
    FROM cartoes
    WHERE usuario_uuid = ?
    AND ativo = 1
    LIMIT 1
    """,
        (session["usuario_uuid"],),
    )

    cartao = cursor.fetchone()
    dia_vencimento = cartao["dia_vencimento"] if cartao else None

    for g in todos:
        if dia_vencimento:
            atualizar_parcelas(g, cursor, dia_vencimento)

    db.commit()

    # 🔹 Recarrega gastos após atualização
    gastos = db.execute(
        """
        SELECT
            gc.*,
            c.nome AS nome_cartao,
            (gc.qtd_parcelas - gc.parcelas_pagas) AS parcelas_restantes
        FROM gastos_cartao gc
        JOIN cartoes c ON c.id = gc.cartao_id
        WHERE gc.usuario_uuid = ?
          AND gc.parcela_numero = (
            SELECT MIN(parcela_numero)
            FROM gastos_cartao
            WHERE compra_id = gc.compra_id
        )
        ORDER BY gc.data_compra DESC
        """,
        (session["usuario_uuid"],),
    ).fetchall()

    # ======================================================
    # 🔹 CALCULAR FATURAS DO CARTÃO (service)
    # ======================================================

    faturas = calcular_faturas_cartao(session["usuario_uuid"])
    # 🔹 pegar dia de vencimento
    cartao_info = db.execute(
        """
        SELECT dia_vencimento
        FROM cartoes
        WHERE usuario_uuid = ?
        AND ativo = 1
        LIMIT 1
        """,
        (session["usuario_uuid"],),
    ).fetchone()

    dia_vencimento = cartao_info["dia_vencimento"] if cartao_info else ""

    # 🔥 calcular fatura correta pro topo (ignora vencimento)
    agora = datetime.now()

    cartao_info = db.execute(
        """
        SELECT dia_fechamento
        FROM cartoes
        WHERE usuario_uuid = ?
        AND ativo = 1
        LIMIT 1
        """,
        (session["usuario_uuid"],),
    ).fetchone()

    mes, ano = calcular_competencia_fatura(agora, cartao_info["dia_fechamento"])

    fatura_label_topo = gerar_label_fatura(mes, ano)
    total_topo = total_cartao_fatura_atual(session["usuario_uuid"])

    # ======================================================
    # 🔹 RENDERIZA
    # ======================================================

    return render_template(
        "usuario_cartao.html",
        usuario=usuario,
        cartoes=cartoes,
        gastos_cartao=gastos,
        total_cartao_atual=total_topo,
        fatura_label_atual=fatura_label_topo,
        total_cartao_proximo=faturas["total_proximo"],
        fatura_label_proximo=faturas["faturas"][1]["label"],
        dia_vencimento=dia_vencimento,
    )


# =====================================================
# CARTÕES
# =====================================================
@cartao_bp.route("/api/cartoes")
@usuario_required
def listar_cartoes():
    db = get_db()
    cartoes = db.execute(
        """
        SELECT *
        FROM cartoes
        WHERE usuario_uuid = ?
          AND ativo = 1
        ORDER BY data_criacao DESC
    """,
        (session["usuario_uuid"],),
    ).fetchall()

    return dict(cartoes=[dict(c) for c in cartoes])


# ====================================================
# GASTOS-CARTÃO
# ======================================================
@cartao_bp.route("/api/gastos-cartao")
@usuario_required
def listar_gastos_cartao():
    db = get_db()
    gastos = db.execute(
        """
    SELECT gc.*, c.nome AS nome_cartao
    FROM gastos_cartao gc
    JOIN cartoes c ON c.id = gc.cartao_id
    WHERE gc.usuario_uuid = ?
      AND gc.parcela_numero = 1
    ORDER BY gc.data_compra DESC
""",
        (session["usuario_uuid"],),
    ).fetchall()

    return dict(gastos=[dict(g) for g in gastos])


# ======================================================
# APAGAR GASTO NO CARTÃO
# ======================================================
@cartao_bp.route("/gasto-cartao/apagar/<int:gasto_id>", methods=["POST"])
@usuario_required
@csrf.exempt
def apagar_gasto_cartao(gasto_id):
    db = get_db()

    # 🔎 descobre a compra
    compra = db.execute(
        """
        SELECT compra_id
        FROM gastos_cartao
        WHERE id = ?
          AND usuario_uuid = ?
    """,
        (gasto_id, session["usuario_uuid"]),
    ).fetchone()

    if compra:
        # 🧹 remove TODAS as parcelas da compra
        db.execute(
            """
            DELETE FROM gastos_cartao
            WHERE compra_id = ?
              AND usuario_uuid = ?
        """,
            (compra["compra_id"], session["usuario_uuid"]),
        )

    db.commit()
    db.close()

    return jsonify({"sucesso": True})


# ====================================================
# EDITAR-GASTOS-CARTÃO
# =====================================================
@cartao_bp.route("/gasto-cartao/editar/<int:gasto_id>", methods=["POST"])
@usuario_required
@csrf.exempt
def editar_gasto_cartao(gasto_id):

    db = get_db()

    db.execute(
        """
        UPDATE gastos_cartao
        SET cartao_id = ?,
            descricao = ?
        WHERE id = ?
        AND usuario_uuid = ?
        """,
        (
            request.form["cartao_id"],
            request.form.get("descricao"),
            gasto_id,
            session["usuario_uuid"],
        ),
    )

    db.commit()
    db.close()

    return jsonify({"sucesso": True})


# =======================================================
# +1PARCELA PAGA
# =======================================================
@cartao_bp.route("/gasto-cartao/parcela-paga/<int:gasto_id>", methods=["POST"])
@usuario_required
def parcela_paga_cartao(gasto_id):
    db = get_db()

    db.execute(
        """
        UPDATE gastos_cartao
        SET parcelas_pagas = 
            CASE
                WHEN parcelas_pagas < qtd_parcelas THEN parcelas_pagas + 1
                ELSE parcelas_pagas
            END
        WHERE id = ?
          AND usuario_uuid = ?
          AND quitado = 0
    """,
        (gasto_id, session["usuario_uuid"]),
    )

    db.commit()
    db.close()

    return redirect(url_for("cartao.cartoes_painel"))


# =======================================================
# COMPRA QUITADA
# =======================================================
@cartao_bp.route("/gasto-cartao/quitar/<int:gasto_id>", methods=["POST"])
@usuario_required
def quitar_gasto_cartao(gasto_id):
    db = get_db()

    db.execute(
        """
        UPDATE gastos_cartao
        SET quitado = 1,
            parcelas_pagas = qtd_parcelas
        WHERE id = ?
          AND usuario_uuid = ?
    """,
        (gasto_id, session["usuario_uuid"]),
    )

    db.commit()
    db.close()

    return redirect(url_for("cartao.cartoes_painel"))
