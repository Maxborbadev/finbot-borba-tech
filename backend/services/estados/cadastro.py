from db.database import get_connection
from services import mensagens
from utils.formatters import parse_valor
from werkzeug.security import generate_password_hash

from models.usuario import (
    atualizar_nome,
    atualizar_salario,
    atualizar_saldo,
)

def estado_novo(usuario_uuid, mensagem):

    if mensagem == "1":

        conn = get_connection()

        conn.execute(
            "UPDATE usuarios SET estado = 'aguardando_nome' WHERE uuid = ?",
            (usuario_uuid,),
        )

        conn.commit()
        conn.close()

        return (
            "Perfeito, vamos começar 😊\n"
            "Para que eu possa te atender melhor, qual é o seu nome?"
        )

    if mensagem == "2":
        return mensagens.msg_como_funciona()

    return mensagens.msg_boas_vindas()
#===========================================================================
def estado_aguardando_nome(usuario_uuid, mensagem_original):

    nome = mensagem_original.strip().title()

    if not nome or any(char.isdigit() for char in nome):
        return "Por favor, informe um nome válido para continuar seu cadastro."

    atualizar_nome(usuario_uuid, nome)

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'aguardando_email' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return mensagens.msg_pedir_email(nome)
#===========================================================================
def estado_aguardando_email(usuario_uuid, mensagem_original):

    email = mensagem_original.strip().lower()

    if "@" not in email or "." not in email:
        return "❌ Email inválido. Informe um email válido."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM usuarios WHERE email = ?",
        (email,),
    )

    if cursor.fetchone():
        conn.close()
        return "❌ Este email já está em uso. Informe outro."

    cursor.execute(
        "UPDATE usuarios SET email = ?, estado = 'aguardando_senha' WHERE uuid = ?",
        (email, usuario_uuid),
    )

    conn.commit()
    conn.close()

    return (
        "Perfeito 👍\n\n"
        "Agora crie uma *senha* 🔐\n"
        "➡️ Use no mínimo *6 caracteres*."
    )
#===========================================================================
def estado_aguardando_senha(usuario_uuid, mensagem_original):

    senha = mensagem_original.strip()

    if len(senha) < 6:
        return "❌ A senha deve ter pelo menos 6 caracteres."

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET senha = ? WHERE uuid = ?",
        (generate_password_hash(senha), usuario_uuid),
    )

    conn.execute(
        "UPDATE usuarios SET estado = 'aguardando_salario' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return mensagens.msg_senha_cadastrada()
#===========================================================================
def estado_aguardando_salario(usuario_uuid, mensagem_original):

    try:
        salario = parse_valor(mensagem_original)
    except Exception:
        return "❌ Valor inválido. Exemplo: 2500 ou 2.500,50"

    atualizar_salario(usuario_uuid, salario)

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'aguardando_saldo_inicial' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return mensagens.msg_pedir_saldo_inicial()
#===========================================================================
def estado_aguardando_saldo(usuario_uuid, mensagem_original):

    try:
        saldo = parse_valor(mensagem_original)
    except Exception:
        return "❌ Valor inválido. Exemplo: 1500 ou 1.500,50"

    atualizar_saldo(usuario_uuid, saldo)

    conn = get_connection()

    conn.execute(
        "UPDATE usuarios SET estado = 'ativo' WHERE uuid = ?",
        (usuario_uuid,),
    )

    conn.commit()
    conn.close()

    return mensagens.msg_cadastro_concluido()
#===========================================================================

#===========================================================================