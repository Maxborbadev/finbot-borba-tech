from datetime import datetime, timedelta

from utils.formatters import dinheiro

from models.usuario import buscar_usuario_por_uuid

from models.gasto import (
    total_gastos_periodo,
    maiores_gastos_periodo,
    listar_gastos_periodo,
)

from models.renda import total_rendas_periodo

from services.cartao import (
    total_cartao_fatura_atual,
    total_gastos_cartao_periodo,
    maiores_gastos_cartao_periodo,
)


# ─────────────────────────
# UTILIDADES DE DATA
# ─────────────────────────
def dt_sql(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def inicio_mes_atual():
    agora = datetime.now()
    return agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def inicio_mes_anterior():
    inicio_atual = inicio_mes_atual()
    return (inicio_atual - timedelta(days=1)).replace(day=1)


# ─────────────────────────
# RELATÓRIO DIÁRIO
# ─────────────────────────
def relatorio_diario(usuario_uuid):
    agora = datetime.now()

    inicio_dia = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    fim_dia = agora.replace(hour=23, minute=59, second=59, microsecond=999999)

    total_gastos = total_gastos_periodo(usuario_uuid, inicio_dia, fim_dia)
    gastos_lista = listar_gastos_periodo(usuario_uuid, inicio_dia, fim_dia)
    rendas = total_rendas_periodo(usuario_uuid, inicio_dia, fim_dia)

    usuario = buscar_usuario_por_uuid(usuario_uuid)
    saldo = usuario["saldo"]

    texto = (
        "📅 *RESUMO DE HOJE*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Entradas: R$ {dinheiro(rendas)}\n"
        f"💸 Gastos: R$ {dinheiro(total_gastos)}\n"
        f"💳 Saldo atual: R$ {dinheiro(saldo)}\n\n"
    )

    if not gastos_lista:
        texto += "📉 Nenhum gasto registrado hoje."
        return texto

    texto += "🧾 *Gastos registrados hoje*\n"

    limite = 10

    for i, (_, descricao, valor, _, hora) in enumerate(gastos_lista[:limite], start=1):
        texto += f"{i}️⃣ {hora} • {descricao} — R$ {dinheiro(valor)}\n"

    if len(gastos_lista) > limite:
        restante = len(gastos_lista) - limite
        texto += f"\n📄 +{restante} outros gastos registrados\n"

    return texto


# ─────────────────────────
# RELATÓRIO SEMANAL
# ─────────────────────────
def relatorio_semanal(usuario_uuid):
    fim = datetime.now()
    inicio = fim - timedelta(days=7)

    total_gastos = total_gastos_periodo(usuario_uuid, inicio, fim)
    gastos_lista = listar_gastos_periodo(usuario_uuid, inicio, fim)
    rendas = total_rendas_periodo(usuario_uuid, inicio, fim)

    usuario = buscar_usuario_por_uuid(usuario_uuid)
    saldo = usuario["saldo"]

    texto = (
        "📊 *RESUMO SEMANAL*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Entradas: R$ {dinheiro(rendas)}\n"
        f"💸 Gastos: R$ {dinheiro(total_gastos)}\n"
        f"💳 Saldo atual: R$ {dinheiro(saldo)}\n\n"
    )

    if not gastos_lista:
        texto += "📉 Nenhum gasto registrado nesta semana."
        return texto

    texto += "🧾 *Últimos gastos da semana*\n"

    limite = 10

    for i, (_, descricao, valor, _, hora) in enumerate(gastos_lista[:limite], start=1):
        texto += f"{i}️⃣ {hora} • {descricao} — R$ {dinheiro(valor)}\n"

    if len(gastos_lista) > limite:
        restante = len(gastos_lista) - limite
        texto += f"\n📄 +{restante} outros gastos registrados\n"

    texto += f"\n🔻 Total gasto na semana: R$ {dinheiro(total_gastos)}"

    return texto


# ─────────────────────────
# RELATÓRIO MENSAL
# ─────────────────────────
def relatorio_mensal(usuario_uuid):
    inicio = inicio_mes_atual()
    fim = datetime.now()

    total_gastos = total_gastos_periodo(usuario_uuid, inicio, fim)
    gastos_lista = listar_gastos_periodo(usuario_uuid, inicio, fim)
    rendas = total_rendas_periodo(usuario_uuid, inicio, fim)

    usuario = buscar_usuario_por_uuid(usuario_uuid)
    saldo = usuario["saldo"]

    texto = (
        "📆 *RESUMO DO MÊS*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Entradas: R$ {dinheiro(rendas)}\n"
        f"💸 Gastos: R$ {dinheiro(total_gastos)}\n"
        f"💳 Saldo atual: R$ {dinheiro(saldo)}\n\n"
    )

    if not gastos_lista:
        texto += "📉 Nenhum gasto registrado neste mês."
        return texto

    texto += "🧾 *Últimos gastos registrados*\n"

    limite = 10
    for i, (_, descricao, valor, _, hora) in enumerate(gastos_lista[:limite], start=1):
        texto += f"{i}️⃣ {hora} • {descricao} — R$ {dinheiro(valor)}\n"

    if len(gastos_lista) > limite:
        restante = len(gastos_lista) - limite
        texto += f"\n📄 +{restante} outros gastos registrados\n"

    return texto


# ─────────────────────────
# TOP GASTOS DO MÊS
# ─────────────────────────
def top_gastos_mensal(usuario_uuid, limite=5):
    inicio = inicio_mes_atual()
    fim = datetime.now()

    gastos = maiores_gastos_periodo(usuario_uuid, inicio, fim, limite)

    if not gastos:
        return (
            "🔝 *Maiores gastos do mês*\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📉 Nenhum gasto registrado neste mês."
        )

    texto = "🔝 *Maiores gastos do mês*\n" "━━━━━━━━━━━━━━━━━━\n\n"

    total_top = 0

    for i, (descricao, total) in enumerate(gastos, start=1):
        texto += f"{i}️⃣ {descricao} — R$ {dinheiro(total)}\n"
        total_top += total

    texto += f"\n💸 Total desses gastos: R$ {dinheiro(total_top)}"

    return texto


# ─────────────────────────
# COMPARAÇÃO MENSAL
# ─────────────────────────
def comparacao_mensal(usuario_uuid):
    inicio_atual = inicio_mes_atual()
    inicio_anterior = inicio_mes_anterior()
    fim = datetime.now()

    gastos_atual = total_gastos_periodo(usuario_uuid, inicio_atual, fim)
    gastos_anterior = total_gastos_periodo(usuario_uuid, inicio_anterior, inicio_atual)

    diferenca = gastos_atual - gastos_anterior

    # percentual de mudança
    percentual = 0
    if gastos_anterior > 0:
        percentual = (diferenca / gastos_anterior) * 100

    texto = (
        "📊 *RESUMO DE GASTOS DO MÊS*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📆 Mês atual: R$ {dinheiro(gastos_atual)}\n"
        f"📅 Mês anterior: R$ {dinheiro(gastos_anterior)}\n\n"
    )

    if diferenca > 0:
        texto += (
            f"🔺 Seus gastos aumentaram em\n"
            f"R$ {dinheiro(diferenca)} ({abs(percentual):.0f}%)\n"
        )
    elif diferenca < 0:
        texto += (
            f"🔻 Você economizou\n"
            f"R$ {dinheiro(abs(diferenca))} ({abs(percentual):.0f}%)\n"
        )
    else:
        texto += "➖ Seus gastos foram iguais ao mês anterior\n"

    return texto


# ─────────────────────────
# RELATÓRIO AVANÇADO
# ─────────────────────────
def relatorio_avancado(usuario_uuid):
    inicio = inicio_mes_atual()
    fim = datetime.now()

    total_gastos = total_gastos_periodo(usuario_uuid, inicio, fim)
    total_rendas = total_rendas_periodo(usuario_uuid, inicio, fim)
    gastos_cartao = total_cartao_fatura_atual(usuario_uuid)

    usuario = buscar_usuario_por_uuid(usuario_uuid)
    saldo = usuario["saldo"]
    salario = usuario["salario"] or 0

    base_renda = total_rendas if total_rendas > 0 else salario
    fonte = "rendas registradas" if total_rendas > 0 else "salário mensal"

    diferenca = base_renda - total_gastos

    agora = datetime.now()
    dia_atual = agora.day

    # descobrir quantos dias tem o mês
    proximo_mes = (agora.replace(day=28) + timedelta(days=4)).replace(day=1)
    dias_mes = (proximo_mes - timedelta(days=1)).day

    # percentual da renda utilizada
    percentual_renda = 0
    if base_renda > 0:
        percentual_renda = (total_gastos / base_renda) * 100

    # média diária correta
    media_diaria = total_gastos / dia_atual if dia_atual > 0 else 0

    # projeção até o final do mês
    projecao_mes = media_diaria * dias_mes

    # saúde financeira
    if percentual_renda < 50:
        saude = "🟢 Excelente controle financeiro"
    elif percentual_renda < 80:
        saude = "🟡 Atenção aos gastos"
    else:
        saude = "🔴 Gastos muito altos"

    # situação atual
    if diferenca > 0:
        situacao = "🟢 Você está economizando"
    elif diferenca < 0:
        situacao = "🔴 Atenção: seus gastos estão acima da sua renda"
    else:
        situacao = "🟡 Você está no zero a zero"

    texto = (
        "📊 *RELATÓRIO FINANCEIRO AVANÇADO*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📆 *Resumo do mês*\n"
        f"💰 Entradas: R$ {dinheiro(total_rendas)}\n"
        f"💸 Gastos: R$ {dinheiro(total_gastos)}\n"
        f"💳 Saldo atual: R$ {dinheiro(saldo)}\n\n"
    )

    texto += (
        "📊 *Base de cálculo*\n"
        f"• {fonte}\n\n"
        "💰 *Uso da renda*\n"
        f"{percentual_renda:.0f}% do seu orçamento\n\n"
    )

    texto += f"{situacao}\n\n"

    texto += (
        "💳 *Cartão de crédito*\n" f"Total no cartão: R$ {dinheiro(gastos_cartao)}\n\n"
    )

    # maiores gastos
    maiores = maiores_gastos_periodo(usuario_uuid, inicio, fim, 3)

    if maiores:
        texto += "🔝 *Maiores gastos do mês*\n"

        maior_valor = maiores[0][1]

        for desc, total in maiores:
            texto += f"• {desc} — R$ {dinheiro(total)}\n"

        if total_gastos > 0:
            impacto = (maior_valor / total_gastos) * 100
            texto += f"\n🔥 Maior gasto representa {impacto:.0f}% dos gastos do mês\n"

        texto += "\n"

    texto += (
        "📊 *Média de gastos*\n"
        f"Você gastou em média R$ {dinheiro(media_diaria)} por dia\n\n"
    )

    texto += (
        "🔮 *Projeção até o fim do mês*\n"
        "Se seus gastos continuarem nesse ritmo:\n"
        f"💸 Você pode terminar o mês com R$ {dinheiro(projecao_mes)} em gastos\n\n"
    )

    if base_renda > 0:
        diferenca_proj = base_renda - projecao_mes

        texto += "📉 *Situação projetada*\n"

        if diferenca_proj > 0:
            texto += (
                f"💰 Ainda restariam R$ {dinheiro(diferenca_proj)} do seu orçamento\n\n"
            )
        else:
            texto += f"⚠️ Seus gastos podem ultrapassar seu orçamento em R$ {dinheiro(abs(diferenca_proj))}\n\n"

    texto += "🏦 *Saúde financeira*\n" f"{saude}\n\n"

    # comparação mensal
    inicio_anterior = inicio_mes_anterior()
    gastos_mes_anterior = total_gastos_periodo(usuario_uuid, inicio_anterior, inicio)

    diferenca_mes = total_gastos - gastos_mes_anterior

    texto += "📈 *Comparação com mês anterior*\n"
    texto += f"Mês atual: R$ {dinheiro(total_gastos)}\n"
    texto += f"Mês anterior: R$ {dinheiro(gastos_mes_anterior)}\n"

    if diferenca_mes > 0:
        texto += f"🔺 Você gastou R$ {dinheiro(diferenca_mes)} a mais\n"
    elif diferenca_mes < 0:
        texto += f"🔻 Você economizou R$ {dinheiro(abs(diferenca_mes))}\n"
    else:
        texto += "➖ Gastos iguais ao mês anterior\n"

    # insight automático
    if total_gastos > 0 and maiores:
        texto += (
            "\n💡 *Insight do FinBot*\n"
            "Seu maior gasto representa grande parte do seu orçamento mensal.\n"
            "Reduzir esse tipo de gasto pode melhorar bastante seu saldo.\n"
        )

    return texto
