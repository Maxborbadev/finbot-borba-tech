from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib import colors
from utils.formatters import dinheiro
import os


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
from utils.formatters import dinheiro


def gerar_pdf_fatura(usuario_uuid, gastos_por_categoria, total, label, nome_cartao):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    projeto_dir = os.path.dirname(os.path.dirname(base_dir))

    pasta = os.path.join(projeto_dir, "whatsapp_bot", "temp")
    os.makedirs(pasta, exist_ok=True)

    caminho = os.path.join(pasta, f"fatura_{usuario_uuid}.pdf")

    c = canvas.Canvas(caminho, pagesize=A4)
    largura, altura = A4

    # =========================
    # CABEÇALHO
    # =========================
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, altura - 40, f"Cartão: {nome_cartao.upper()}")

    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(largura - 40, altura - 40, "FinBot Seu assistente financeiro")

    c.setFont("Helvetica", 8)
    c.drawRightString(largura - 40, altura - 55, f"Fatura: {label}")

    c.line(40, altura - 65, largura - 40, altura - 65)

    # =========================
    # BLOCO RESUMO
    # =========================
    c.setFillColor(colors.lightgrey)
    c.rect(40, altura - 120, largura - 80, 50, fill=1, stroke=0)

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)

    c.drawString(50, altura - 95, "Total da Fatura:")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(180, altura - 95, f"R$ {dinheiro(total)}")

    # =========================
    # CABEÇALHO TABELA
    # =========================
    y = altura - 150

    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y, "DATA")
    c.drawString(90, y, "DESCRIÇÃO")
    c.drawRightString(largura - 40, y, "VALOR")

    c.line(40, y - 5, largura - 40, y - 5)

    # =========================
    # DADOS
    # =========================
    y -= 20
    c.setFont("Helvetica", 9)

    for categoria, itens in gastos_por_categoria.items():

        itens = [dict(g) for g in itens]  # 🔥 CORREÇÃO DEFINITIVA

        # Nome da categoria
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y, categoria.upper())
        y -= 15

        c.setFont("Helvetica", 9)

        for g in itens:

            if y < 60:  # quebra de página
                c.showPage()
                c.setFont("Helvetica", 9)
                y = altura - 40

            if g["parcelado"]:
                desc = f"{g['descricao']} ({g['parcela_numero']}/{g['qtd_parcelas']})"
                valor = dinheiro(g["valor_parcela"])
            else:
                desc = g["descricao"]
                valor = dinheiro(g["valor"])

            data_raw = g.get("data_compra")

            if data_raw:
                data = datetime.fromisoformat(data_raw).strftime("%d/%m")
            else:
                data = "--/--"

            c.drawString(40, y, data)
            c.drawString(90, y, desc[:40])  # limite pra não quebrar layout
            c.drawRightString(largura - 40, y, f"R$ {valor}")

            y -= 15

        y -= 5

    # =========================
    # TOTAL FINAL
    # =========================
    c.line(40, y, largura - 40, y)
    y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(largura - 40, y, f"TOTAL: R$ {dinheiro(total)}")

    c.save()

    return caminho


def criar_grafico(gastos_por_categoria):

    data = []
    categorias = []

    for categoria, itens in gastos_por_categoria.items():
        total_categoria = 0

        for g in itens:
            if g["parcelado"]:
                total_categoria += float(g["valor_parcela"])
            else:
                total_categoria += float(g["valor"])

        data.append(total_categoria)
        categorias.append(categoria[:10])

    if not data:
        return Drawing(0, 0)

    drawing = Drawing(400, 200)

    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 30
    chart.height = 125
    chart.width = 300

    chart.data = [data]
    chart.categoryAxis.categoryNames = categorias

    chart.bars[0].fillColor = colors.green

    chart.valueAxis.labelTextFormat = "R$ %0.0f"
    chart.categoryAxis.labels.angle = 30
    chart.categoryAxis.labels.dy = -10
    chart.barSpacing = 5
    chart.groupSpacing = 10

    chart.valueAxis.visibleGrid = True
    chart.valueAxis.gridStrokeColor = colors.lightgrey

    drawing.add(chart)

    return drawing
