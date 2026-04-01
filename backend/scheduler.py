from db.database import get_connection
from datetime import datetime, time, timedelta
from utils.whatsapp import enviar_whatsapp
from utils.formatters import dinheiro
from services.mensagens import msg_aviso_conta_vencendo
from services.mensagens import msg_fatura_cartao_vencendo
from services.cartao import total_cartao_fatura_atual
from services.relatorio_service import (
    relatorio_diario,
    relatorio_semanal,
    relatorio_mensal,
    relatorio_avancado,
)
import schedule
import time


# ===============================
# VERIFICAR EXPIRAÇÃO
# ===============================
def verificar_planos_expirados():
    try:
        conn = get_connection()

        agora = datetime.now()

        conn.execute(
            """
            UPDATE usuarios
            SET plano = 'free',
                plano_expira_em = NULL
            WHERE plano = 'PREMIUM'
              AND plano_expira_em IS NOT NULL
              AND plano_expira_em < ?
            """,
            (agora,),
        )

        conn.commit()
        conn.close()

        print(f"[OK] Verificação executada em {agora}")

    except Exception as e:
        print(f"[ERRO] Scheduler: {e}")


# ===============================
# LIMPAR TOKENS EXPIRADOS
# ===============================
def limpar_tokens_expirados():
    try:
        conn = get_connection()

        conn.execute(
            """
            DELETE FROM recuperacao_senha
            WHERE expira_em < datetime('now')
            """
        )

        conn.commit()
        conn.close()

        print("[OK] Tokens expirados removidos ")

    except Exception as e:
        print(f"[ERRO] Limpeza tokens: {e}")


# ===============================
# ATIVAR PREMIUM
# ===============================
def ativar_premium(usuario_id):
    try:
        conn = get_connection()

        expira = datetime.now() + timedelta(days=30)

        conn.execute(
            """
            UPDATE usuarios
            SET plano = 'PREMIUM',
                plano_expira_em = ?
            WHERE id = ?
            """,
            (expira, usuario_id),
        )

        conn.commit()
        conn.close()

        print(f"[OK] Premium ativado para usuário {usuario_id}")

    except Exception as e:
        print(f"[ERRO] Ativar premium: {e}")


# ===============================
# VERIFICAR VENCIMENTO DE CONTAS
# ===============================
def verificar_contas_vencendo():
    try:
        conn = get_connection()

        hoje = datetime.now().day

        contas = conn.execute(
            """
            SELECT 
                contas_fixas.usuario_uuid,
                contas_fixas.descricao,
                contas_fixas.valor,
                contas_fixas.dia_vencimento,
                usuarios.whatsapp_id
            FROM contas_fixas
            JOIN usuarios 
            ON usuarios.uuid = contas_fixas.usuario_uuid
            WHERE contas_fixas.ativa = 1
            AND usuarios.plano = 'PREMIUM'
            """
        ).fetchall()

        for conta in contas:
            dia_venc = conta["dia_vencimento"]

            dias_para_vencer = dia_venc - hoje

            if dias_para_vencer == 4 or dias_para_vencer == 0:

                mensagem = msg_aviso_conta_vencendo(
                    conta["descricao"], dinheiro(conta["valor"]), dia_venc
                )

                enviar_whatsapp(conta["whatsapp_id"], mensagem)

        conn.close()

    except Exception as e:
        print(f"[ERRO] Verificar contas: {e}")


# ===============================
# VERIFICAR VENCIMENTO DE CARTÕES
# ===============================
def verificar_cartoes_vencendo():
    try:
        conn = get_connection()

        hoje = datetime.now().day

        cartoes = conn.execute(
            """
            SELECT 
                cartoes.usuario_uuid,
                cartoes.nome,
                cartoes.dia_vencimento,
                usuarios.whatsapp_id
            FROM cartoes
            JOIN usuarios
            ON usuarios.uuid = cartoes.usuario_uuid
            WHERE cartoes.ativo = 1
            AND usuarios.plano = 'PREMIUM'
            """
        ).fetchall()

        for cartao in cartoes:

            dia_venc = cartao["dia_vencimento"]
            usuario_uuid = cartao["usuario_uuid"]
            valor_fatura = total_cartao_fatura_atual(usuario_uuid)

            dias_para_vencer = dia_venc - hoje

            if dias_para_vencer == 4 or dias_para_vencer == 0:

                mensagem = msg_fatura_cartao_vencendo(
                    cartao["nome"], dinheiro(valor_fatura), dia_venc
                )

                enviar_whatsapp(cartao["whatsapp_id"], mensagem)

        conn.close()

    except Exception as e:
        print(f"[ERRO] Verificar cartões: {e}")


# ===============================
# ENVIAR RELATÓRIO DIÁRIO
# ===============================
def enviar_relatorio_diario():
    try:
        conn = get_connection()

        usuarios = conn.execute(
        """
        SELECT uuid, whatsapp_id
        FROM usuarios
        WHERE status='ativo'
        AND estado='ativo'
        AND plano = 'PREMIUM'
        """
    ).fetchall()

        for usuario in usuarios:

            usuario_uuid = usuario["uuid"]

            mensagem = relatorio_diario(usuario_uuid)
            numero = usuario["whatsapp_id"]

            if not numero:
                continue

            enviar_whatsapp(usuario["whatsapp_id"], mensagem)

            time.sleep(0.3)

        conn.close()

        print("[OK] Relatório diário enviado")

    except Exception as e:
        print(f"[ERRO] Relatório diário: {e}")


# ===============================
# ENVIAR RELATÓRIO SEMANAL
# ===============================
def enviar_relatorio_semanal():
    try:
        conn = get_connection()

        usuarios = conn.execute(
        """
        SELECT uuid, whatsapp_id
        FROM usuarios
        WHERE status='ativo'
        AND estado='ativo'
        AND plano = 'PREMIUM'
        """
    ).fetchall()

        for usuario in usuarios:

            usuario_uuid = usuario["uuid"]

            mensagem = relatorio_semanal(usuario_uuid)
            numero = usuario["whatsapp_id"]

            if not numero:
                continue

            enviar_whatsapp(usuario["whatsapp_id"], mensagem)

            time.sleep(0.3)

        conn.close()

        print("[OK] Relatório semanal enviado")

    except Exception as e:
        print(f"[ERRO] Relatório semanal: {e}")


# ===============================
# AGENDAMENTO
# ===============================

schedule.every(90).minutes.do(verificar_planos_expirados)
schedule.every(120).minutes.do(limpar_tokens_expirados)
schedule.every().day.at("15:30").do(verificar_contas_vencendo)
schedule.every().day.at("15:25").do(verificar_cartoes_vencendo)
schedule.every().sunday.at("20:00").do(enviar_relatorio_semanal)
schedule.every().day.at("20:30").do(enviar_relatorio_diario)
# roda ao iniciar
verificar_planos_expirados()
limpar_tokens_expirados()
verificar_contas_vencendo()
verificar_cartoes_vencendo()

print("Scheduler FinBot iniciado...")
print("Verificando planos premium automaticamente.")
# ===============================
# LOOP PRINCIPAL
# ===============================
while True:
    schedule.run_pending()
    time.sleep(1)
