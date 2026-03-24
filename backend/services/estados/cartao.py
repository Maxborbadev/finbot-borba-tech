from db.database import get_connection
from models import categoria
from services.categoria_auto import detectar_categoria
from utils.formatters import dinheiro

from services.cartao import registrar_gasto_cartao

def estado_cartao_nome(usuario_uuid, mensagem_original):

    nome_cartao = mensagem_original.strip()

    if not nome_cartao or len(nome_cartao) < 2:
        return (
            "❌ Nome inválido.\n\n"
            "Informe um nome simples para o cartão.\n"
            "Ex: Nubank, Itaú, Inter"
        )

    conn = get_connection()

    conn.execute(
        """
        UPDATE usuarios
        SET cartao_temp_nome = ?,
            estado = 'aguardando_cartao_fechamento'
        WHERE uuid = ?
        """,
        (nome_cartao, usuario_uuid),
    )

    conn.commit()
    conn.close()

    return (
        f"💳 Cartão *{nome_cartao}* anotado 👍\n\n"
        "Agora informe o *dia de fechamento da fatura* 📅\n"
        "👉 Digite um número de *1 a 28*"
    )


def estado_cartao_fechamento(usuario_uuid, mensagem_original):

    try:
        dia_fechamento = int(mensagem_original.strip())
    except ValueError:
        return "❌ Informe apenas um número entre 1 e 28."

    if not (1 <= dia_fechamento <= 28):
        return "❌ O dia de fechamento deve ser entre 1 e 28."

    conn = get_connection()

    conn.execute(
        """
        UPDATE usuarios
        SET cartao_temp_fechamento = ?,
            estado = 'aguardando_cartao_vencimento'
        WHERE uuid = ?
        """,
        (dia_fechamento, usuario_uuid),
    )

    conn.commit()
    conn.close()

    return (
        "📅 Fechamento anotado com sucesso!\n\n"
        "Agora informe o *dia de vencimento da fatura* 📆\n"
        "👉 Digite um número de *1 a 28*"
    )


def estado_cartao_vencimento(usuario_uuid, mensagem_original):

    try:
        dia_vencimento = int(mensagem_original.strip())
    except ValueError:
        return "❌ Informe apenas um número entre 1 e 28."

    if not (1 <= dia_vencimento <= 28):
        return "❌ O dia de vencimento deve ser entre 1 e 28."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cartao_temp_nome,
            cartao_temp_fechamento,
            cartao_temp_valor,
            cartao_temp_descricao,
            cartao_temp_parcelas,
            cartao_temp_parcelas_pagas
        FROM usuarios
        WHERE uuid = ?
        """,
        (usuario_uuid,),
    )

    temp = cursor.fetchone()

    if not temp:
        conn.close()
        return "❌ Erro ao finalizar cadastro do cartão."

    nome_cartao = temp["cartao_temp_nome"]
    dia_fechamento = temp["cartao_temp_fechamento"]
    valor = temp["cartao_temp_valor"]
    descricao = temp["cartao_temp_descricao"] or "Sem descrição"
    parcelas = temp["cartao_temp_parcelas"] or 1
    parcelas_pagas = temp["cartao_temp_parcelas_pagas"] or 0

    cursor.execute(
        """
        INSERT INTO cartoes (
            usuario_uuid,
            nome,
            dia_fechamento,
            dia_vencimento,
            ativo
        ) VALUES (?, ?, ?, ?, 1)
        """,
        (usuario_uuid, nome_cartao, dia_fechamento, dia_vencimento),
    )

    cursor.execute(
        """
        UPDATE usuarios
        SET
            cartao_temp_nome = NULL,
            cartao_temp_fechamento = NULL,
            cartao_temp_valor = NULL,
            cartao_temp_descricao = NULL,
            cartao_temp_parcelas = NULL,
            cartao_temp_parcelas_pagas = NULL,
            estado = 'ativo'
        WHERE uuid = ?
        """,
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    if valor is not None and descricao is not None:
        registrar_gasto_cartao(
            usuario_uuid, valor, descricao, parcelas, parcelas_pagas
        )

    return (
        "💳 *Cartão cadastrado com sucesso!*\n\n"
        f"📌 Cartão: {nome_cartao}\n"
        f"📅 Fechamento: dia {dia_fechamento}\n"
        f"💳 Vencimento: dia {dia_vencimento}\n\n"
        "💸 O gasto foi registrado automaticamente.\n"
        "Digite /menu para continuar."
    )



def estado_cartao_selecao(usuario_uuid, mensagem_original, listar_cartoes, ativar_cartao):

    cartoes = listar_cartoes(usuario_uuid)

    if not cartoes:
        return "❌ Você não possui cartões cadastrados."

    try:
        escolha = int(mensagem_original.strip())
    except ValueError:

        resposta = "❌ Digite apenas o número do cartão.\n\n"

        for i, c in enumerate(cartoes, start=1):
            status = " (ativo)" if c["ativo"] == 1 else ""
            resposta += f"{i}️⃣ {c['nome']}{status}\n"

        return resposta

    if escolha < 1 or escolha > len(cartoes):

        resposta = "❌ Número inválido. Escolha uma opção válida:\n\n"

        for i, c in enumerate(cartoes, start=1):
            status = " (ativo)" if c["ativo"] == 1 else ""
            resposta += f"{i}️⃣ {c['nome']}{status}\n"

        return resposta

    cartao_escolhido = cartoes[escolha - 1]

    ativar_cartao(usuario_uuid, cartao_escolhido["id"])

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'ativo' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return (
        f"✅ Cartão *{cartao_escolhido['nome']}* agora é o ativo.\n\n"
        "Todos os próximos gastos no cartão serão registrados nele."
    )


def estado_data_compra(usuario_uuid, mensagem, processar_mensagem, whatsapp_id):

    if mensagem == "1":

        conn = get_connection()

        conn.execute(
            """
            UPDATE usuarios
            SET estado = 'salvar_compra_cartao',
                cartao_temp_parcelas_pagas = 0
            WHERE uuid = ?
            """,
            (usuario_uuid,),
        )

        conn.commit()
        conn.close()

        return processar_mensagem(whatsapp_id, "__continuar__")

    elif mensagem == "2":

        conn = get_connection()

        conn.execute(
            """
            UPDATE usuarios
            SET estado = 'aguardando_parcelas_pagas'
            WHERE uuid = ?
            """,
            (usuario_uuid,),
        )

        conn.commit()
        conn.close()

        return "Quantas parcelas já foram pagas?"

    else:
        return "Responda com 1 para SIM ou 2 para NÃO."
    
def estado_parcelas_pagas(usuario_uuid, mensagem_original, processar_mensagem, whatsapp_id):

    try:
        parcelas_pagas = int(mensagem_original.strip())
    except ValueError:
        return "Digite apenas o número de parcelas já pagas."

    conn = get_connection()

    conn.execute(
        """
        UPDATE usuarios
        SET
            cartao_temp_parcelas_pagas = ?,
            estado = 'salvar_compra_cartao'
        WHERE uuid = ?
        """,
        (parcelas_pagas, usuario_uuid),
    )

    conn.commit()
    conn.close()

    return processar_mensagem(whatsapp_id, "__continuar__")

def estado_salvar_compra(usuario_uuid):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            cartao_temp_valor,
            cartao_temp_descricao,
            cartao_temp_parcelas,
            cartao_temp_parcelas_pagas
        FROM usuarios
        WHERE uuid = ?
        """,
        (usuario_uuid,),
    )

    temp = cursor.fetchone()

    valor = temp["cartao_temp_valor"]
    descricao = temp["cartao_temp_descricao"]
    parcelas = temp["cartao_temp_parcelas"] or 1
    parcelas_pagas = temp["cartao_temp_parcelas_pagas"] or 0

    gasto = registrar_gasto_cartao(usuario_uuid, valor, descricao, parcelas, parcelas_pagas)

    cursor.execute(
        """
        UPDATE usuarios
        SET
            cartao_temp_valor = NULL,
            cartao_temp_descricao = NULL,
            cartao_temp_parcelas = NULL,
            cartao_temp_parcelas_pagas = NULL,
            estado = 'ativo'
        WHERE uuid = ?
        """,
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    valor_parcela = valor / parcelas
    restantes = parcelas - parcelas_pagas
    categoria = gasto["categoria"] or "Outros"

    if parcelas > 1:

        return (
        "💳 *Compra parcelada registrada!*\n\n"
        f"📌 {descricao}\n"
        f"📂 Categoria: {categoria}\n"
        f"💰 R$ {dinheiro(valor)}\n"
        f"💳 {parcelas}x de R$ {dinheiro(valor_parcela)}\n"
        f"✅ Pagas: {parcelas_pagas}\n"
        f"📌 Restam: {restantes}"
        )

    else:

        return (
        "💳 *Gasto no cartão registrado!*\n\n"
        f"📌 {descricao}\n"
        f"📂 Categoria: {categoria}\n"
        f"💰 R$ {dinheiro(valor)}"
        )
    
    

    