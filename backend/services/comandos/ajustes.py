from db.database import get_connection


def comando_ajustar_saldo(usuario_uuid):

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'aguardando_ajuste_saldo' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return (
        "🔄 *Ajuste de saldo*\n\n"
        "Informe o valor que você possui em mãos no momento.\n\n"
        "Informe somente números.\n"
        "Exemplo: 1250 ou 1.250"
    )


def comando_ajustar_salario(usuario_uuid):

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'aguardando_ajuste_salario' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return (
        "💼 *Ajuste de salário*\n\n"
        "Qual é o seu salário mensal atual?\n\n"
        "Informe somente números.\n"
        "Exemplo: 3500 ou 3.500"
    )