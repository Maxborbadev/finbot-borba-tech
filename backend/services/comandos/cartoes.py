from db.database import get_connection


def comando_novo_cartao(usuario_uuid):

    conn = get_connection()

    conn.execute(
        """
        UPDATE usuarios
        SET estado = 'aguardando_cartao_nome',
            cartao_temp_valor = NULL,
            cartao_temp_descricao = NULL
        WHERE uuid = ?
        """,
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return (
        "💳 *Cadastro de novo cartão*\n\n"
        "Qual o *nome do cartão*?\n"
        "Ex: Nubank, Itaú, Inter"
    )


def comando_listar_cartoes(usuario_uuid, listar_cartoes):

    cartoes = listar_cartoes(usuario_uuid)

    if not cartoes:
        return "❌ Você ainda não possui cartões cadastrados."

    resposta = "💳 *Seus cartões:*\n\n"

    for i, c in enumerate(cartoes, start=1):
        status = " (ativo)" if c["ativo"] == 1 else ""
        resposta += f"{i}️⃣ {c['nome']}{status}\n"

    resposta += "\nDigite o *número do cartão* que deseja usar."

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'aguardando_cartao_selecao' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return resposta