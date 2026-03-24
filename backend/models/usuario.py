import uuid
from db.database import get_connection


# ======================================================
# GET OU CRIA USUÁRIO (WHATSAPP)
# ======================================================
def get_or_create_user(whatsapp_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT uuid, plano FROM usuarios WHERE whatsapp_id = ?",
        (whatsapp_id,),
    )

    user = cursor.fetchone()

    if user:
        conn.close()
        return user["uuid"], user["plano"]

    novo_uuid = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO usuarios (
            uuid, whatsapp_id, estado, plano
        ) VALUES (?, ?, 'novo', 'free')
    """,
        (novo_uuid, whatsapp_id),
    )

    conn.commit()
    conn.close()

    return novo_uuid, "free"


# ======================================================
# BUSCAR USUÁRIO
# ======================================================
def buscar_usuario_por_uuid(usuario_uuid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE uuid = ?",
        (usuario_uuid,),
    )

    usuario = cursor.fetchone()
    conn.close()
    return usuario


# ======================================================
# ATUALIZAÇÕES DE PERFIL
# ======================================================
def atualizar_nome(usuario_uuid, nome):
    conn = get_connection()
    conn.execute(
        "UPDATE usuarios SET nome = ? WHERE uuid = ?",
        (nome, usuario_uuid),
    )
    conn.commit()
    conn.close()


def atualizar_salario(usuario_uuid, salario):
    conn = get_connection()
    conn.execute(
        "UPDATE usuarios SET salario = ? WHERE uuid = ?",
        (salario, usuario_uuid),
    )
    conn.commit()
    conn.close()


def atualizar_saldo(usuario_uuid, saldo):
    conn = get_connection()
    conn.execute(
        "UPDATE usuarios SET saldo = ? WHERE uuid = ?",
        (saldo, usuario_uuid),
    )
    conn.commit()
    conn.close()


# ======================================================
# LISTAR USUÁRIOS ATIVOS
# ======================================================
def listar_usuarios_ativos():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM usuarios
        WHERE status = 'ativo'
          AND conta_ativa = 1
    """
    )

    usuarios = cursor.fetchall()
    conn.close()
    return usuarios
