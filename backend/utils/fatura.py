from datetime import datetime


def competencia_fatura_pdf(dia_fechamento, dia_vencimento):
    hoje = datetime.now()

    mes, ano = calcular_competencia_fatura(
        hoje,
        dia_fechamento
    )

    meses = [
        "",
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    ]

    label = f"{meses[mes]}/{ano}"

    return mes, ano, label

def calcular_competencia_fatura(data_compra, dia_fechamento):
    """
    Retorna o mês/ano da fatura baseado no ciclo do cartão.
    """

    mes = data_compra.month
    ano = data_compra.year

    # 🔥 passou do fechamento → próxima fatura
    if data_compra.day > dia_fechamento:
        mes += 1

        if mes > 12:
            mes = 1
            ano += 1

    return mes, ano


def adicionar_meses(mes, ano, quantidade):
    """
    Soma meses corretamente (tratando virada de ano)
    """

    mes += quantidade

    while mes > 12:
        mes -= 12
        ano += 1

    return mes, ano


def gerar_label_fatura(mes, ano):
    meses = [
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    ]

    return f"{meses[mes-1]}/{str(ano)[-2:]}"
