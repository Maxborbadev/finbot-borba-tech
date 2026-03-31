from models.usuario import buscar_usuario_por_uuid
from services import mensagens


def comando_plano(usuario_uuid):

    usuario = buscar_usuario_por_uuid(usuario_uuid)

    plano = usuario["plano"].upper()
    expira = usuario["plano_expira_em"]

    if plano == "PREMIUM":
        return mensagens.msg_plano_premium(expira)

    if plano == "BASIC":

        if expira:
            try:
                from datetime import datetime

                data = datetime.fromisoformat(str(expira))
                data_formatada = data.strftime("%d/%m/%Y")

                dias_restantes = (data - datetime.now()).days

                validade_msg = (
                    f"📅 *Plano ativo até:* {data_formatada}\n"
                    f"⏳ *Dias restantes:* {dias_restantes}"
                )
            except:
                validade_msg = f"📅 *Plano ativo até:* {expira}"
        else:
            validade_msg = "📅 *Plano ativo até:* Não definido"

        return (
            "💎 *PLANO BASIC*\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Você está no plano BASIC.\n\n"
            "✔ 100 lançamentos por mês\n"
            "✔ Cartões e contas fixas\n"
            "✔ Gráficos e painel web\n\n"
            f"{validade_msg}\n\n"
            "🚀 Continue organizando sua vida financeira!"
        )

    return mensagens.msg_plano_free()