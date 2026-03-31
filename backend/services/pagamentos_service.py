from db.database import get_connection
from services.mercado_pago import verificar_pagamento
from utils.whatsapp import enviar_whatsapp
from datetime import datetime, timedelta
from services.mensagens import msg_plano_basic_ativado, msg_plano_premium_ativado


def processar_pagamento(payment_id):

    pagamento = verificar_pagamento(payment_id)

    print("Pagamento verificado:", pagamento)

    if pagamento["status"] != "approved":
        return

    valor = float(pagamento.get("transaction_amount", 0))

    if valor == 6.99:
        novo_plano = "BASIC"
    elif valor == 15.00:
        novo_plano = "PREMIUM"
    else:
        print("Valor desconhecido:", valor)
        return
    db = get_connection()

    db.execute(
        """
        UPDATE pagamentos
        SET status = 'aprovado'
        WHERE payment_id = ?
        """,
        (payment_id,),
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
    if usuario["plano"].upper() == novo_plano:
        print("Usuário já premium:", usuario_uuid)
        db.close()
        return

    expira = datetime.now() + timedelta(days=30)

    db.execute(
        """
        UPDATE usuarios
        SET plano = ?,
            plano_expira_em = ?,
            origem_premium = 'pago'
        WHERE uuid = ?
        """,
        (novo_plano, expira, usuario_uuid),
    )

    db.commit()
    db.close()

    db = get_connection()

    usuario = db.execute(
        "SELECT plano, whatsapp_id FROM usuarios WHERE uuid = ?",
        (usuario_uuid,),
    ).fetchone()

    db.close()

    if usuario["whatsapp_id"]:

        

        if novo_plano == "BASIC":
            mensagem = msg_plano_basic_ativado(expira)
        else:
            mensagem = msg_plano_premium_ativado(expira)

        enviar_whatsapp(usuario["whatsapp_id"], mensagem)

        print(f"Plano {novo_plano} ativado para:", usuario_uuid)
