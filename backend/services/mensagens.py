# =======================
# MENSAGEM BOAS VINDAS
# =======================
def msg_boas_vindas():
    return (
        "👋 Olá! Seja bem-vindo(a)!\n\n"
        "🤖 Eu sou o *FinBot*, o assistente financeiro da *Borba Tech* 💻\n\n"
        "Comigo você pode:\n"
        "💸 Registrar gastos\n"
        "💰 Registrar rendas\n"
        "📊 Acompanhar relatórios\n"
        "📈 Ter controle total do seu dinheiro\n\n"
        "Tudo direto pelo *WhatsApp*, de forma simples e rápida.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ *Primeiro acesso?*\n"
        "Recomendamos fortemente que você veja a opção *2️⃣* para entender exatamente como o FinBot funciona.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👉 *Escolha uma opção:*\n\n"
        "1️⃣ Criar meu cadastro\n"
        "2️⃣ Como o FinBot funciona"
    )


# =======================
# COMO FUNCIONA ==2
# =======================
def msg_como_funciona():
    return (
        "📘 *Como o FinBot funciona*\n\n"
        "O *FinBot* é o assistente financeiro da *Borba Tech* 💻🏢, criado para te ajudar a controlar seus gastos e rendas de forma simples, rápida e organizada — tudo direto pelo *WhatsApp*.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✍️ *Como registrar seus gastos e recebimentos?*\n\n"
        "Basta enviar uma *mensagem simples* informando o que aconteceu com seu dinheiro.\n"
        "Não é necessário formulário, botão ou menu complicado 👌\n\n"
        "📌 *Exemplos de gastos:*\n"
        "• gastei 30 mercado 🛒\n"
        "• gastei 120 combustível ⛽\n\n"
        "📌 *Exemplos de recebimentos:*\n"
        "• recebi 500 freelance 💼\n"
        "• recebi 200 salário 💰\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ *Importante sobre os valores*\n"
        "Informe *os valores de forma correta*.\n"
        "utilize ponto, vírgula. *Não utilize (R$)*\n\n"
        "✅ Correto: gastei 60,50 mercado\n"
        "✅ Correto: gastei 1.200,40 mercado\n\n"
        "use o mesmo formato para registrar gastos\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📝 *Descrição do gasto ou renda*\n"
        "A última palavra ou frase da mensagem será considerada a *descrição*.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Relatórios disponíveis quando quiser:*\n"
        "📅 /hoje → resumo do dia\n"
        "🗓️ /semanal → resumo da semana\n"
        "📆 /mensal → resumo do mês\n"
        "📈 /avancado → relatório completo\n\n"
        "Digite *1️⃣* para continuar."
    )


# =======================
# PEDINDO E-AMAIL
# =======================
def msg_pedir_email(nome):
    return (
        f"Prazer, {nome}! 😊\n\n"
        "Agora informe seu *email* 📧\n"
        "Ele será usado para acessar o *painel do FinBot*.\n\n"
        "👉 Exemplo: nome@email.com"
    )


# =======================
# SENHA CADASTRADA
# ======================
def msg_senha_cadastrada():
    return (
        "🔐 *Senha cadastrada com sucesso!*\n\n"
        "✅ O *painel administrativo* já está disponível para uso.\n"
        "Você pode acessá-lo pelo link abaixo:\n"
        "🌐 http://finbotbyborbatech.com/\n\n"
        "Você também pode acessar nosso site no link abaixo:\n"
        "🌐 https://finbotbyborbatech.netlify.app\n\n\n"
        "Agora preciso saber qual é o seu *salário mensal* 💼\n\n"
        "🔒 Fique tranquilo(a): essa informação é usada apenas para gerar seus relatórios e análises pessoais.\n"
        "Ela não é compartilhada com ninguém.\n\n"
        "Digite somente números.\n"
        "👉 Exemplo: 2500 ou 2.500 ou 2.500,50"
    )


# ===================
# PEDIR SALDO INICIAL
# ===================
def msg_pedir_saldo_inicial():
    return (
        "Perfeito.\n\n"
        "Quanto você tem disponível hoje em dinheiro ou na conta para começarmos o controle financeiro?\n\n"
        "🔒 Fique tranquilo(a): essa informação é usada apenas para gerar seus relatórios e análises pessoais.\n"
        "Ela não é compartilhada com ninguém.\n\n"
        "Digite somente números.\n"
        "Exemplo: 1.500 ou 1500 ou 1.500,50"
    )


# =====================
# CADASTRO CONCLUIDO
# ====================
def msg_cadastro_concluido():
    return (
        "🎉 *Cadastro concluído com sucesso!*\n\n"
        "Agora você já pode começar a controlar seu dinheiro 💰\n\n"
        "👉 Envie suas movimentações assim:\n"
        "• gastei 20 lanche\n"
        "• recebi 100 freelance\n\n"
        "⚠️ *Importante:* envie apenas *1 gasto ou 1 renda por mensagem*.\n"
        "Não é possível registrar dois valores na mesma mensagem.\n\n"
        "📋 Digite */menu* para ver todas as opções.\n"
        "❓ Se precisar de ajuda, digite */ajuda*."
    )


# ==================
# COMANDOS
# ===================
def msg_comandos():
    return (
        "📘 *Comandos disponíveis — FinBot*\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Principais*\n"
        "/menu → menu principal\n"
        "/comandos → lista de comandos\n"
        "/ajuda → instruções de uso\n"
        "/saldo → ver saldo atual\n"
        "/plano → ver seu plano atual\n"
        "/upgrade → ativar plano Premium\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💸 *Lançamentos*\n"
        "/gasto → como registrar gastos\n"
        "/renda → como registrar rendas\n"
        "/cofrinho → guardar dinheiro no cofrinho\n"
        "/attcofre → atualizar total do cofrinho\n"
        "/cartao → registrar gasto no cartão\n\n"
        "📌 *Exemplos rápidos*\n"
        "gastei 30 mercado\n"
        "recebi 500 freelance\n"
        "cartão 200 ifood\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Relatórios (Free)*\n"
        "/hoje → resumo do dia\n"
        "/semanal → resumo da semana\n"
        "/mensal → resumo do mês\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💳 *Cartões (Premium)*\n"
        "/novocartao → cadastrar cartão\n"
        "/cartoes → selecionar cartão ativo\n"
        "/fatura → ver fatura do mês atual\n"
        "/cartao → ver informações do cartão\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📆 *Contas Fixas (Premium)*\n"
        "/contafixa → cadastrar conta fixa\n"
        "/fixas → listar contas fixas\n"
        "/removerconta ID → remover conta\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📊 *Relatórios Avançados (Premium)*\n"
        "/avancado → relatório financeiro completo\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ *Ajustes (Premium)*\n"
        "/attsaldo → ajustar saldo\n"
        "/attsalario → ajustar salário\n"
        "/senha → trocar senha do painel\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🌐 *Extras*\n"
        "/painel → acessar painel web\n\n"
        "🤖 *Dica:* você pode digitar valores direto.\n"
        "Exemplo: *gastei 50 mercado*"
    )


# ========================
# MENU PRINCIPAL
# ======================
def msg_menu_principal():
    return (
        "💼 *MENU PRINCIPAL — FINBOT*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 *RELATÓRIOS*\n"
        "━━━━━━━━━━━━━━\n"
        "📅 */dia* ou */hoje* — Resumo do dia\n"
        "🗓️ */semanal* ou */semana* — Resumo semanal\n"
        "📆 */mensal* ou */mes* — Resumo mensal\n"
        "📈 */avancado* — Relatório completo *(Premium)*\n\n"
        "💸 *LANÇAMENTOS*\n"
        "━━━━━━━━━━━━━━\n"
        "➖ */gasto* — Registrar despesas\n"
        "➕ */renda* — Registrar receitas\n"
        "💳 */cartao* — Gastos no cartão *(Premium)*\n"
        "🐷 */cofrinho* — Guardar dinheiro\n\n"
        "📆 *CONTAS FIXAS*\n"
        "━━━━━━━━━━━━━━\n"
        "📌 */contafixa* — Cadastrar conta *(Premium)*\n"
        "📋 */fixas* — Listar contas *(Premium)*\n"
        "🗑️ */removerconta* — Remover conta *(Premium)*\n\n"
        "⚙️ *AJUSTES & STATUS*\n"
        "━━━━━━━━━━━━━━\n"
        "💳 */saldo* — Ver saldo atual\n"
        "⭐ */plano* — Ver plano atual\n"
        "🔄 */attsaldo* — Ajustar saldo *(Premium)*\n"
        "💼 */attsalario* — Ajustar salário *(Premium)*\n\n"
        "🌐 *EXTRAS*\n"
        "━━━━━━━━━━━━━━\n"
        "📊 */painel* — Painel financeiro *(Premium)*\n"
        "💎 */upgrade* — Ativar plano Premium\n\n"
        "🧭 *SUPORTE & AJUDA*\n"
        "━━━━━━━━━━━━━━\n"
        "❓ */ajuda* — Dúvidas e orientações\n"
        "📘 */comandos* — Lista completa de comandos\n\n"
        "🚀 *FinBot* — Seu controle financeiro inteligente"
    )


# ==============================
# Plano Premium / Plano free
# ==============================
from datetime import datetime


def msg_plano_premium(expira):

    if expira:
        try:
            data = datetime.fromisoformat(str(expira))
            data_formatada = data.strftime("%d/%m/%Y")

            dias_restantes = (data - datetime.now()).days

            validade_msg = (
                f"📅 *Plano ativo até:* {data_formatada}\n"
                f"⏳ *Restam:* {dias_restantes} dias"
            )

        except:
            validade_msg = f"📅 *Plano ativo até:* {expira}"
    else:
        validade_msg = "📅 *Plano ativo até:* Não definido"

    return (
        "⭐ *FINBOT PREMIUM*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🎉 Você está utilizando o *FinBot Premium*.\n"
        "Controle completo da sua vida financeira direto no WhatsApp.\n\n"
        "📊 *Painel Financeiro Inteligente*\n"
        "• Acesso ao painel web completo\n"
        "• Gráficos de gastos e rendas\n"
        "• Saldo atualizado em tempo real\n\n"
        "📈 *Relatórios Financeiros*\n"
        "• Relatório diário\n"
        "• Relatório semanal\n"
        "• Relatório mensal completo\n"
        "• Relatório financeiro avançado\n\n"
        "💳 *Gestão Completa*\n"
        "• Registro ilimitado de gastos e rendas\n"
        "• Controle de cartões de crédito\n"
        "• Gerenciamento de contas fixas\n"
        "• Cofrinho para guardar dinheiro\n\n"
        "🌐 *Painel Web*\n"
        "• Visualize gráficos da sua vida financeira\n"
        "• Analise seus hábitos de consumo\n"
        "• Controle tudo em um só lugar\n\n"
        f"{validade_msg}\n\n"
        "Obrigado por usar o *FinBot Premium* 🚀"
    )


def msg_plano_free():
    return (
        "⭐ *FINBOT*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🔓 *Plano atual:* Free\n\n"
        "Com o plano Free você já pode:\n"
        "• Registrar gastos 💸\n"
        "• Registrar rendas 💰\n"
        "• Consultar seu saldo 📊\n"
        "• Ver relatórios básicos 📈\n"
        "• Controlar seu dinheiro direto no WhatsApp 🤖\n\n"
        "💎 *Quer liberar mais recursos?*\n"
        "No plano Premium você desbloqueia:\n"
        "• Painel web completo\n"
        "• Gráficos financeiros\n"
        "• Relatórios avançados\n"
        "• Histórico financeiro completo\n\n"
        "🚀 Para ativar o Premium,\n"
        "fale com o administrador."
    )


def msg_plano_pago():
    return (
        "🔒 *Recurso exclusivo do FinBot Premium*\n\n"
        "Este comando está disponível apenas para usuários Premium.\n\n"
        "📋 Use */plano* para ver todos os benefícios do plano.\n"
        "🚀 Para ativar o plano Premium, digite */upgrade*.\n\n"
        "💬 Se precisar de ajuda, fale com o administrador."
    )


##============================================
# AJUDA
##============================================
def msg_ajuda():
    return (
        "🤖 *Ajuda — FinBot*\n\n"
        "Eu te ajudo a controlar seu dinheiro direto pelo WhatsApp 💰\n\n"
        "👉 Registre gastos e rendas com frases simples:\n"
        "• gastei 30 mercado\n"
        "• recebi 500 freelance\n"
        "• cartão 200 ifood\n\n"
        "⚠️ *Importante:* envie apenas *1 gasto ou 1 renda por mensagem*.\n"
        "Não é possível registrar dois valores na mesma mensagem.\n\n"
        "📋 Para ver todos os comandos disponíveis:\n"
        "Digite */menu*\n\n"
        "Se precisar de ajuda com algo, é só me chamar 😉"
    )


# ============================================
# RENDA REGISTRADA
# ============================================
def msg_renda_registrada(descricao, valor, saldo):
    return (
        "💰 *Entrada registrada com sucesso!*\n\n"
        f"📌 Descrição: {descricao or 'entrada'}\n"
        f"💵 Valor: R$ {valor}\n"
        f"💳 Saldo atual: R$ {saldo}\n\n"
        "Digite /menu para mais opções."
    )


# ============================================
# GASTO REGISTRADO
# ============================================
def msg_gasto_registrado(descricao, categoria, valor, saldo):
    return (
        "💸 *Gasto registrado com sucesso!*\n\n"
        f"📌 Descrição: {descricao or 'gasto'}\n"
        f"🏷️ Categoria: {categoria}\n"
        f"💰 Valor: R$ {valor}\n"
        f"💳 Saldo atual: R$ {saldo}\n\n"
        "Digite /menu para mais opções."
    )


# ============================================
# MENSAGEM NÃO ENTENDI
# ============================================
def msg_nao_entendi_lancamento():
    return (
        "🤔 Não consegui entender o que você quis registrar.\n\n"
        "Tente enviar de forma simples, por exemplo:\n\n"
        "💸 gastei 35 mercado\n"
        "💰 recebi 500 freelance\n"
        "💳 cartão 120 ifood\n\n"
        "⚠️ Envie apenas *1 gasto ou 1 renda por mensagem*.\n"
        "Não é possível registrar dois valores juntos.\n\n"
        "📋 Digite */menu* para ver todas as opções."
    )


# ============================================
# FALLBACK FINA
# ============================================
def msg_nao_entendi():
    return "Não entendi sua mensagem 🤔"


# ============================================
# mensagem planoa tivado
# ============================================
def msg_plano_premium_ativado(expira):

    dias_restantes = (expira - datetime.now()).days

    return (
        "⭐ *FINBOT PREMIUM ATIVADO*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🎉 *Pagamento confirmado!*\n"
        "Seu *FinBot Premium* foi ativado com sucesso.\n\n"
        f"📅 *Plano ativo até:* {expira.strftime('%d/%m/%Y')}\n"
        f"⏳ *Dias restantes:* {dias_restantes}\n\n"
        "Agora você tem acesso a todos os recursos do *FinBot Premium*:\n"
        "✔ Relatórios financeiros completos\n"
        "✔ Controle avançado de cartões\n"
        "✔ Organização automática de gastos\n"
        "✔ Painel financeiro completo\n\n"
        "🚀 Aproveite ao máximo o FinBot!\n"
        "⚠️ Quando seu plano estiver próximo de expirar, avisaremos você automaticamente.\n\n"
        "🚀 Obrigado por apoiar o FinBot"
    )


# ===================================
# mensagem de premium de 7 dias ativado
# ====================================
def msg_premium_gratis_7_dias(expira):

    dias_restantes = (expira - datetime.now()).days

    return (
        "🎁 *FINBOT PREMIUM LIBERADO*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 *Você ganhou 7 dias grátis!*\n"
        "Seu acesso ao *FinBot Premium* foi liberado para teste.\n\n"
        f"📅 *Acesso válido até:* {expira.strftime('%d/%m/%Y')}\n"
        f"⏳ *Dias restantes:* {dias_restantes}\n\n"
        "Agora você pode aproveitar todos os recursos premium:\n"
        "✔ Relatórios financeiros completos\n"
        "✔ Controle avançado de cartões\n"
        "✔ Organização automática de gastos\n"
        "✔ Painel financeiro completo\n\n"
        "💡 Aproveite esse período para organizar sua vida financeira!\n"
        "💎 Depois, você pode ativar o plano completo a qualquer momento.\n\n"
        "🚀 Aproveite o FinBot!"
    )


# ============================================
# AVISO DE CONTA VENCENDO (AUTO)
# ============================================
def msg_aviso_conta_vencendo(descricao, valor, dia_venc):
    return f"""⚠️ Conta próxima do vencimento

📄 {descricao}
💰 Valor: R$ {valor}
📅 Vence dia {dia_venc}
"""


# ============================================
# AVISO DE CARTÃO VENCENDO (AUTO)
# ============================================
def msg_fatura_cartao_vencendo(nome_cartao, valor_fatura, dia_venc):
    return f"""💳 Fatura do cartão próxima do vencimento

💳 Cartão: {nome_cartao}
💰 Fatura atual: R$ {valor_fatura}
📅 Vencimento: dia {dia_venc}

Evite juros pagando até o vencimento 😉
"""


# ===========================================
# mensagem de aviso de limite
# ===========================================
def msg_limite_atingido():
    return (
        "🚫 *Limite atingido!*\n\n"
        "Você usou todos os *10 lançamentos* do plano FREE.\n\n"
        "🚀 *Não fique travado!*\n\n"
        "💎 *Plano BASIC — R$ 6,99*\n"
        "• 100 lançamentos por mês\n"
        "• Cartões + contas fixas\n"
        "• Gráficos completos\n\n"
        "👉 Digite */upgrade* e continue usando agora"
    )


def msg_aviso_limite():
    return (
        "⚠️ *Atenção!*\n\n"
        "Você está quase atingindo o limite do plano FREE.\n"
        "Faltam apenas *3 lançamentos* este mês.\n\n"
        "🚀 *Evite ficar travado!*\n\n"
        "💎 BASIC — R$ 6,99\n"
        "• 100 lançamentos por mês\n\n"
        "👉 Digite */upgrade* e garanta mais lançamentos"
    )


def msg_plano_basic_ativado(expira):

    from datetime import datetime

    dias_restantes = (expira - datetime.now()).days

    return (
        "💎 *FINBOT BASIC ATIVADO*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🎉 *Pagamento confirmado!*\n"
        "Seu *FinBot BASIC* foi ativado com sucesso.\n\n"
        f"📅 *Plano ativo até:* {expira.strftime('%d/%m/%Y')}\n"
        f"⏳ *Dias restantes:* {dias_restantes}\n\n"
        "Agora você tem acesso a:\n"
        "✔ 100 lançamentos por mês\n"
        "✔ Controle de cartões de crédito\n"
        "✔ Contas fixas\n"
        "✔ Gráficos financeiros\n"
        "✔ Painel web\n\n"
        "🚀 Continue organizando sua vida financeira!\n"
        "⚠️ Quando seu plano estiver próximo de expirar, avisaremos você automaticamente.\n\n"
        "💰 Quer ir além?\n"
        "O *Premium* libera tudo sem limites!"
    )
