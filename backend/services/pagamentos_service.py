from db.database import get_connection
from services.mensagens import msg_plano_premium_ativado
from services.mercado_pago import verificar_pagamento
from utils.whatsapp import enviar_whatsapp
from datetime import datetime, timedelta


def processar_pagamento(payment_id):

    pagamento = verificar_pagamento(payment_id)

    print("Pagamento verificado:", pagamento)

    if pagamento["status"] != "approved":
        return
    db = get_connection()

    db.execute(
        """
        UPDATE pagamentos
        SET status = 'aprovado'
        WHERE payment_id = ?
        """,
        (payment_id,)
    )

    db.commit()

    usuario_uuid = pagamento.get("external_reference")

    if not usuario_uuid:
        print("Pagamento sem external_reference")
        return

    db = get_connection()

    usuario = db.execute(
        "SELECT plano, whatsapp_id FROM usuarios WHERE uuid = ?",
        (usuario_uuid,),
    ).fetchone()

    if not usuario:
        print("Usuário não encontrado:", usuario_uuid)
        db.close()
        return

    # evitar ativação duplicada
    if usuario["plano"] == "premium":
        print("Usuário já premium:", usuario_uuid)
        db.close()
        return

    expira = datetime.now() + timedelta(days=30)

    db.execute(
        """
        UPDATE usuarios
        SET plano = 'premium',
            plano_expira_em = ?
        WHERE uuid = ?
        """,
        (expira, usuario_uuid),
    )

    db.commit()
    db.close()

    if usuario["whatsapp_id"]:

        mensagem = msg_plano_premium_ativado(expira)

        enviar_whatsapp(usuario["whatsapp_id"], mensagem)

        print("Premium ativado para:", usuario_uuid)
