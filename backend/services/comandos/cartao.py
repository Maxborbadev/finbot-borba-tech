import re
from utils.formatters import dinheiro
from services.cartao import registrar_gasto_cartao
from db.database import get_connection


def processar_cartao(usuario_uuid, mensagem, buscar_cartao_ativo):
    """
    Processa:
    cartao 120 mercado
    cartao 350 tenis 3x
    """

    texto = mensagem.lower().replace("cartao", "").replace("cartão", "").strip()

    parcelas = 1

    match = re.search(r'(\d+)x$', texto)
    if match:
        parcelas = int(match.group(1))
        texto = texto[:match.start()].strip()

    partes = texto.split()

    if len(partes) < 2:
        return None

    try:
        valor = float(partes[0].replace(",", "."))
    except ValueError:
        return None

    descricao = " ".join(partes[1:])

    cartao_id = buscar_cartao_ativo(usuario_uuid)

    # 🚨 NÃO EXISTE CARTÃO → iniciar cadastro automático
    if not cartao_id:
        conn = get_connection()
        conn.execute(
            """
            UPDATE usuarios
            SET estado = 'aguardando_cartao_nome',
                cartao_temp_valor = ?,
                cartao_temp_descricao = ?,
                cartao_temp_parcelas = ?
            WHERE uuid = ?
            """,
            (valor, descricao, parcelas, usuario_uuid),
        )
        conn.commit()
        conn.close()

        return (
            "💳 *Vamos cadastrar seu cartão primeiro*\n\n"
            "Qual o *nome do cartão*?\n"
            "Ex: Nubank, Itaú, Inter"
        )

    
    # se for parcelado → iniciar fluxo interativo
    if parcelas > 1:
        conn = get_connection()
        conn.execute(
            """
            UPDATE usuarios
            SET estado = 'aguardando_data_compra',
                cartao_temp_valor = ?,
                cartao_temp_descricao = ?,
                cartao_temp_parcelas = ?
            WHERE uuid = ?
            """,
            (valor, descricao, parcelas, usuario_uuid),
        )
        conn.commit()
        conn.close()

        return (
            "💳 Compra parcelada detectada!\n\n"
            "A compra foi feita hoje?\n\n"
            "1️⃣ Sim\n"
            "2️⃣ Não"
        )

    if parcelas == 1:

        gasto = registrar_gasto_cartao(usuario_uuid, valor, descricao)

        categoria = gasto["categoria"] or "Outros"

        return (
            "💳 *Gasto no cartão registrado!*\n\n"
            f"📌 {descricao}\n"
            f"📂 Categoria: {categoria}\n"
            f"💰 R$ {dinheiro(valor)}"
        )