from datetime import datetime

from datetime import datetime

def competencia_fatura_pdf(dia_fechamento, dia_vencimento):
    hoje = datetime.now()

    mes = hoje.month
    ano = hoje.year

    meses = [
        "",
        "Janeiro", "Fevereiro", "Março", "Abril",
        "Maio", "Junho", "Julho", "Agosto",
        "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    label = f"{meses[mes]}/{ano}"

    return mes, ano, label