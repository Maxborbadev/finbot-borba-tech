from services.mercado_pago import criar_pix
from db.database import get_connection


def comando_upgrade(usuario):

    db = get_connection()

    pagamento_pendente = db.execute(
        """
        SELECT id
        FROM pagamentos
        WHERE usuario_uuid = ?
        AND status = 'pendente'
        """,
        (usuario["uuid"],),
    ).fetchone()

    db.close()

    if pagamento_pendente:
        return (
            "⚠️ *Você já tem um pagamento pendente.*\n\n"
            "Use o PIX enviado anteriormente ou aguarde ele expirar."
        )

    nome = usuario["nome"]

    pagamento = criar_pix(usuario["uuid"], usuario["email"])

    pix = pagamento["pix"]
    qr_base64 = pagamento["qr_base64"]

    mensagem = (
        "💎 *FINBOT PREMIUM*\n"
        "━━━━━━━━━━━━━━\n\n"
        "Controle total das suas finanças direto no WhatsApp.\n\n"
        "Com o *Premium* você desbloqueia:\n"
        "✔ Relatórios financeiros completos\n"
        "✔ Controle avançado de cartões\n"
        "✔ Organização automática de gastos\n"
        "✔ Painel financeiro completo\n"
        "✔ Recursos exclusivos do FinBot\n\n"
        "💰 *Apenas R$ 6,99 por mês*\n\n"
        "📲 Escaneie o QR Code abaixo ou copie o PIX da próxima mensagem.\n\n"
        "⚠️ *Este pagamento expira em 30 minutos.*\n\n"
        f"👤 Usuário: *{nome}*\n\n"
        "🚀 Assim que o pagamento for confirmado seu *FinBot Premium* será ativado automaticamente."
    )

    pix_info = "📋 *PIX Copia e Cola*\n" "Toque e segure para copiar:"

    return [mensagem, {"imagem_base64": qr_base64}, pix_info, pix]
