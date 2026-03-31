from services.mercado_pago import criar_pix
from db.database import get_connection


def comando_upgrade(usuario):

    db = get_connection()
    db.execute(
        "UPDATE usuarios SET estado = 'escolhendo_plano' WHERE uuid = ?",
        (usuario["uuid"],),
    )
    db.commit()
    db.close()

    return (
        "💎 *PLANOS FINBOT*\n"
        "━━━━━━━━━━━━━━\n\n"
        "Escolha seu plano:\n\n"
        "1️⃣ BASIC\n"
        "• 100 lançamentos/mês\n"
        "• Cartões + contas fixas + gráficos\n"
        "💰 R$ 6,99/mês\n\n"
        "2️⃣ PREMIUM\n"
        "• Lançamentos ilimitados\n"
        "• Todos os recursos liberados\n"
        "💰 R$ 15,00/mês\n\n"
        "👉 Responda com *1* ou *2*\n\n"
        "Digite *0* ou *sair* para cancelar."
    )


def comando_upgrade_escolha(usuario, escolha):

    plano = None

    if escolha == "1":
        plano = "BASIC"
    elif escolha == "2":
        plano = "PREMIUM"
    else:
        return "❌ Opção inválida. Digite 1 ou 2."

    db = get_connection()

    pagamento_pendente = db.execute(
        """
        SELECT id
        FROM pagamentos
        WHERE usuario_uuid = ?
        AND status = 'pendente'
        AND criado_em > datetime('now', '-30 minutes')
        """,
        (usuario["uuid"],),
    ).fetchone()

    db.close()

    if pagamento_pendente:
        return "⚠️ Você já tem um pagamento pendente.\nFinalize ou aguarde expirar."

    # 🔥 AGORA SIM volta para ativo
    db = get_connection()
    db.execute(
        "UPDATE usuarios SET estado = 'ativo' WHERE uuid = ?",
        (usuario["uuid"],),
    )
    db.commit()
    db.close()

    pagamento = criar_pix(usuario["uuid"], usuario["email"], plano)

    if "erro" in pagamento:
        return pagamento["erro"]

    pix = pagamento["pix"]
    qr_base64 = pagamento["qr_base64"]

    nome = usuario["nome"]

    preco = "R$ 6,99" if plano == "BASIC" else "R$ 15,00"

    mensagem = (
        f"💎 *PLANO {plano}*\n"
        "━━━━━━━━━━━━━━\n\n"
        f"💰 Valor: {preco}\n\n"
        "📲 Escaneie o QR Code abaixo ou copie o PIX.\n\n"
        "⚠️ Expira em 30 minutos\n\n"
        f"👤 Usuário: *{nome}*"
    )

    pix_info = "📋 *PIX Copia e Cola*"

    return [mensagem, {"imagem_base64": qr_base64}, pix_info, pix]
