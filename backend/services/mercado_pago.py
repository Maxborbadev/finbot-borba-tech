import os
import mercadopago
import time
import base64
from db.database import get_connection
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TEMP_DIR = os.path.join(BASE_DIR, "whatsapp_bot", "temp")

ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise Exception("MP_ACCESS_TOKEN não definido no .env")

sdk = mercadopago.SDK(ACCESS_TOKEN)


def salvar_qr(qr_base64, nome_arquivo):

    os.makedirs(TEMP_DIR, exist_ok=True)

    nome_arquivo = f"{nome_arquivo}_{int(time.time())}.png"

    img = base64.b64decode(qr_base64)

    caminho = os.path.join(TEMP_DIR, nome_arquivo)

    with open(caminho, "wb") as f:
        f.write(img)

    return caminho


def apagar_qr(caminho):

    try:
        if os.path.exists(caminho):
            os.remove(caminho)
    except Exception as e:
        print("Erro ao apagar QR:", e)


def criar_pix(usuario_uuid, email, plano):

    limpar_pagamentos_pendentes(usuario_uuid)
    db = get_connection()

    db.execute(
        """
        UPDATE pagamentos
        SET status = 'expirado'
        WHERE status = 'pendente'
        AND criado_em < datetime('now', '-30 minutes')
    """
    )
    db.commit()

    pendente = db.execute(
        """
        SELECT 1 FROM pagamentos
        WHERE usuario_uuid = ? AND status = 'pendente'
        LIMIT 1
        """,
        (usuario_uuid,),
    ).fetchone()

    db.close()

    if pendente:
        return {
            "erro": "Você já tem um pagamento PIX pendente. Aguarde ou finalize ele."
        }

    limpar_qr_expirados()

    expiration = (datetime.utcnow() + timedelta(minutes=30)).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )

    if plano == "BASIC":
        valor = 6.99
    elif plano == "PREMIUM":
        valor = 15.00
    else:
        return {"erro": "Plano inválido"}

    payment_data = {
        "transaction_amount": valor,
        "description": f"FinBot {plano}",
        "payment_method_id": "pix",
        "external_reference": usuario_uuid,
        "date_of_expiration": expiration,
        "payer": {"email": email},
        "notification_url": "https://finbotbyborbatech.com/webhook/mercadopago"
    }

    payment = sdk.payment().create(payment_data)

    resposta = payment.get("response")

    if not resposta:
        raise Exception("Resposta vazia do Mercado Pago")

    if "point_of_interaction" not in resposta:
        raise Exception(f"Erro ao gerar PIX: {resposta}")

    pix = resposta["point_of_interaction"]["transaction_data"]["qr_code"]
    qr_base64 = resposta["point_of_interaction"]["transaction_data"]["qr_code_base64"]

    payment_id = resposta["id"]

    db = get_connection()

    db.execute(
        """
        INSERT INTO pagamentos (usuario_uuid, payment_id, status, criado_em)
        VALUES (?, ?, 'pendente', datetime('now'))
        """,
        (usuario_uuid, payment_id),
    )

    db.commit()
    db.close()

    return {"pix": pix, "qr_base64": qr_base64, "payment_id": payment_id}


def limpar_qr_expirados():

    pasta = TEMP_DIR

    if not os.path.exists(pasta):
        return

    agora = time.time()

    for arquivo in os.listdir(pasta):

        caminho = os.path.join(pasta, arquivo)

        if not os.path.isfile(caminho):
            continue

        idade = agora - os.path.getmtime(caminho)

        # 40 minutos (PIX expira em 30)
        if idade > 2400:
            try:
                os.remove(caminho)
                print("QR expirado removido:", arquivo)
            except:
                pass


def verificar_pagamento(payment_id):

    payment = sdk.payment().get(payment_id)

    return payment["response"]


def limpar_pagamentos_pendentes(usuario_uuid):

    db = get_connection()

    pagamentos = db.execute(
        """
        SELECT payment_id FROM pagamentos
        WHERE usuario_uuid = ? AND status = 'pendente'
        """,
        (usuario_uuid,),
    ).fetchall()

    for p in pagamentos:

        payment_id = p["payment_id"]

        try:
            status_mp = verificar_pagamento(payment_id)["status"]

            # 🔥 Mapeamento correto
            if status_mp == "approved":
                novo_status = "pago"
            elif status_mp == "pending":
                novo_status = "pendente"
            elif status_mp == "expired":
                novo_status = "expirado"
            else:
                novo_status = "cancelado"

            # Atualiza só se mudou
            if novo_status != "pendente":
                db.execute(
                    """
                    UPDATE pagamentos
                    SET status = ?
                    WHERE payment_id = ?
                    """,
                    (novo_status, payment_id),
                )

        except Exception as e:
            print("Erro ao verificar pagamento:", e)

    db.commit()
    db.close()
