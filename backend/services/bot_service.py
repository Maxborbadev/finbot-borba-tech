# =========================================================
# BIBLIOTECAS PADRÃO
# =========================================================
import unicodedata

# =========================================================
# BANCO
# =========================================================
from db.database import get_connection

# =========================================================
# MODELS
# =========================================================
from models.usuario import (
    get_or_create_user,
    buscar_usuario_por_uuid,
)

# =========================================================
# SERVICES
# =========================================================
from services import mensagens
from services.permissoes import (
    usuario_premium,
    pode_usar_cartao,
    pode_usar_conta_fixa,
    pode_usar_grafico,
)
from services.mensagens_erro import erro_comando_nao_reconhecido
from services.lancamentos import processar_lancamento
from services.detector_intencao import eh_registro_gasto, eh_registro_renda
from services.categoria_auto import detectar_categoria
from services.estados.upgrade import estado_escolhendo_plano
from services.estados.cadastro import estado_novo
from services.estados.recuperacao import estado_aguardando_recuperacao_email
from services.estados.cadastro import (
    estado_aguardando_nome,
    estado_aguardando_email,
    estado_aguardando_senha,
    estado_aguardando_salario,
    estado_aguardando_saldo,
)
from services.estados.ajustes import (
    estado_ajustar_salario,
    estado_ajustar_saldo,
)
from services.estados.cartao import (
    estado_cartao_nome,
    estado_cartao_fechamento,
    estado_cartao_vencimento,
    estado_cartao_selecao,
    estado_data_compra,
    estado_parcelas_pagas,
    estado_salvar_compra,
)

# =========================================================
# COMANDOS
# =========================================================
from services.comandos.upgrade import comando_upgrade, comando_upgrade_escolha
from utils.whatsapp import enviar_whatsapp_documento
from services.comandos.painel import comando_painel
from services.comandos.cofrinho import comando_cofrinho
from services.comandos.menu import comando_menu
from services.comandos.saldo import comando_saldo
from services.comandos.plano import comando_plano
from services.comandos.comando_fatura import comando_fatura
from services.comandos.comandos import comando_comandos
from services.comandos.instrucoes import comando_gasto, comando_renda
from services.comandos.recuperar_senha import comando_recuperar_senha
from services.comandos.ajustes import comando_ajustar_saldo, comando_ajustar_salario
from services.comandos.cartoes import comando_novo_cartao, comando_listar_cartoes
from services.comandos.info_cartao import comando_info_cartao
from services.comandos.contas_fixas import (
    comando_conta_fixa,
    comando_listar_contas,
    comando_remover_conta,
)
from services.comandos.relatorios import (
    comando_relatorio_diario,
    comando_relatorio_semanal,
    comando_relatorio_mensal,
    comando_relatorio_avancado,
)


# ==================================================================================
def buscar_cartao_ativo(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM cartoes
        WHERE usuario_uuid = ?
          AND ativo = 1
        ORDER BY id DESC
        LIMIT 1
    """,
        (usuario_uuid,),
    )

    cartao = cursor.fetchone()
    conn.close()

    return cartao["id"] if cartao else None


def listar_cartoes(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, nome, ativo
        FROM cartoes
        WHERE usuario_uuid = ?
        ORDER BY id
    """,
        (usuario_uuid,),
    )

    cartoes = cursor.fetchall()
    conn.close()
    return cartoes


def ativar_cartao(usuario_uuid, cartao_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE cartoes
        SET ativo = 0
        WHERE usuario_uuid = ?
    """,
        (usuario_uuid,),
    )

    cursor.execute(
        """
        UPDATE cartoes
        SET ativo = 1
        WHERE id = ? AND usuario_uuid = ?
    """,
        (cartao_id, usuario_uuid),
    )

    conn.commit()
    conn.close()


def processar_mensagem(whatsapp_id, mensagem):

    mensagem_original = mensagem.strip()

    mensagem = unicodedata.normalize("NFKD", mensagem_original)
    mensagem = mensagem.encode("ASCII", "ignore").decode("ASCII").lower()

    usuario_uuid, _ = get_or_create_user(whatsapp_id)

    from services.permissoes import sincronizar_plano
    sincronizar_plano(usuario_uuid)

    usuario = buscar_usuario_por_uuid(usuario_uuid)

    # 🔹 BUSCAR DADOS DO PLANO REAL
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT *
    FROM planos
    WHERE nome = ?
    """,
        (usuario["plano"],),
    )

    plano_dados = cursor.fetchone()
    conn.close()

    estado = usuario["estado"]

    # ========================
    #   ESTADOS DO USUARIO
    # =========================
    if estado == "novo":
        return estado_novo(usuario_uuid, mensagem)

    if estado == "aguardando_nome":
        return estado_aguardando_nome(usuario_uuid, mensagem_original)

    if estado == "aguardando_email":
        return estado_aguardando_email(usuario_uuid, mensagem_original)

    if estado == "aguardando_senha":
        return estado_aguardando_senha(usuario_uuid, mensagem_original)

    if estado == "aguardando_salario":
        return estado_aguardando_salario(usuario_uuid, mensagem_original)

    if estado == "aguardando_saldo_inicial":
        return estado_aguardando_saldo(usuario_uuid, mensagem_original)

    if estado == "aguardando_ajuste_salario":
        return estado_ajustar_salario(usuario_uuid, mensagem_original)

    if estado == "aguardando_ajuste_saldo":
        return estado_ajustar_saldo(usuario_uuid, mensagem_original)

    if estado == "aguardando_cartao_nome":
        return estado_cartao_nome(usuario_uuid, mensagem_original)

    if estado == "aguardando_cartao_fechamento":
        return estado_cartao_fechamento(usuario_uuid, mensagem_original)

    if estado == "aguardando_cartao_vencimento":
        return estado_cartao_vencimento(usuario_uuid, mensagem_original)

    if estado == "aguardando_cartao_selecao":
        return estado_cartao_selecao(
            usuario_uuid,
            mensagem_original,
            listar_cartoes,
            ativar_cartao,
        )

    if estado == "aguardando_data_compra":
        return estado_data_compra(
            usuario_uuid, mensagem, processar_mensagem, whatsapp_id
        )

    if estado == "aguardando_parcelas_pagas":
        return estado_parcelas_pagas(
            usuario_uuid, mensagem_original, processar_mensagem, whatsapp_id
        )

    if estado == "salvar_compra_cartao":
        return estado_salvar_compra(usuario_uuid)

    if estado == "aguardando_recuperacao_email":
        return estado_aguardando_recuperacao_email(usuario_uuid, mensagem_original)
    if estado == "escolhendo_plano":
        from services.estados.upgrade import estado_escolhendo_plano

        return estado_escolhendo_plano(usuario_uuid, mensagem, usuario)

    # ─────────────────────────
    # ATIVO
    # ─────────────────────────
    if estado == "ativo":

        respostas_sociais = [
            "ok",
            "blz",
            "beleza",
            "valeu",
            "obrigado",
            "obrigada",
            "show",
            "top",
            "kk",
            "kkk",
            "rs",
            "rsrs",
            "👍",
            "🙏",
            "👌",
        ]

        if mensagem.strip() in respostas_sociais:
            return "😊"
        # ========================================================================================
        #                                       COMANDOS DO FINBOT
        # ========================================================================================
        if mensagem.startswith("/"):
            mensagem = "/" + mensagem[1:].strip()

            # ===============================
            #       COMANDOS FREE
            # ===============================
            if mensagem == "/menu":
                return comando_menu()

            if mensagem == "/ajuda":
                return mensagens.msg_ajuda()

            if mensagem == "/comandos":
                return comando_comandos()

            if mensagem == "/saldo":
                return comando_saldo(usuario_uuid)

            resposta = comando_cofrinho(usuario_uuid, mensagem_original)
            if resposta:
                return resposta

            if mensagem == "/plano":
                usuario = buscar_usuario_por_uuid(usuario_uuid)
                return comando_plano(usuario_uuid)

            if mensagem == "/upgrade":
                return comando_upgrade(usuario)

            if mensagem == "/gasto":
                return comando_gasto()

            if mensagem == "/renda":
                return comando_renda()

            if mensagem in ["/hoje", "/dia", "/diario", "/diário"]:
                return comando_relatorio_diario(usuario_uuid)

            if mensagem in ["/semanal", "/semana"]:
                return comando_relatorio_semanal(usuario_uuid)

            if mensagem in ["/mensal", "/mes", "/mês"]:
                return comando_relatorio_mensal(usuario_uuid)

            # ===============================
            # COMANDOS PREMIUM
            # ===============================

            if mensagem.startswith("/painel"):
                if not pode_usar_grafico(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_painel()
            # =================================================
            if mensagem in ["/senha", "/recuperar", "/recuperarsenha"]:
                if not pode_usar_grafico(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_recuperar_senha(usuario_uuid)
            # =================================================
            if mensagem in ["/avancado", "/avançado"]:
                if not pode_usar_grafico(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_relatorio_avancado(usuario_uuid)
            # =================================================
            if mensagem.startswith("/contafixa"):
                if not pode_usar_conta_fixa(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_conta_fixa(usuario_uuid, mensagem_original)
            # =================================================
            if mensagem == "/fixas":
                if not pode_usar_conta_fixa(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_listar_contas(usuario_uuid)
            # =================================================
            if mensagem.startswith("/removerconta"):
                if not pode_usar_conta_fixa(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_remover_conta(usuario_uuid, mensagem)
            # =================================================
            if mensagem in ["/att saldo", "/attsaldo", "/ajustarsaldo"]:
                if not pode_usar_grafico(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_ajustar_saldo(usuario_uuid)
            # =================================================
            if mensagem in ["/att salario", "/attsalario", "/ajustarsalario"]:
                if not pode_usar_grafico(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_ajustar_salario(usuario_uuid)
            # =================================================
            if mensagem == "/novocartao":
                if not pode_usar_cartao(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_novo_cartao(usuario_uuid)
            # =================================================
            if mensagem == "/cartoes":
                if not pode_usar_cartao(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_listar_cartoes(usuario_uuid, listar_cartoes)
            # =================================================
            if mensagem == "/cartao":
                if not pode_usar_cartao(usuario_uuid):
                    return mensagens.msg_plano_pago()
                return comando_info_cartao()
            # =================================================
            if mensagem == "/fatura":
                if not pode_usar_grafico(usuario_uuid):
                    return mensagens.msg_plano_pago()

                msg, pdf = comando_fatura(usuario_uuid)

                if msg:
                    return msg

                if pdf:
                    enviar_whatsapp_documento(usuario["whatsapp_id"], pdf)

                return None
            # =================================================

            return erro_comando_nao_reconhecido()
        # ===============================================  FIM DOS COMANDOS ==========================================================

        return processar_lancamento(
            usuario_uuid, mensagem, mensagem_original, buscar_cartao_ativo
        )

    return mensagens.msg_nao_entendi()
