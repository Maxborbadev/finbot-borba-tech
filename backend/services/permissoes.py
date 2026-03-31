from db.database import get_connection
from models.usuario import buscar_usuario_por_uuid


def obter_plano_dados(usuario_uuid):
    usuario = buscar_usuario_por_uuid(usuario_uuid)
    plano_nome = usuario["plano"].lower()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM planos
        WHERE LOWER(nome) = ?
    """, (plano_nome,))

    plano = cursor.fetchone()
    conn.close()

    return plano


# Mantém compatibilidade com código antigo
def usuario_premium(plano):
    return plano.upper() == "PREMIUM"


# NOVAS PERMISSÕES
def pode_usar_cartao(usuario_uuid):
    plano = obter_plano_dados(usuario_uuid)
    return plano and plano["pode_cartao"] == 1


def pode_usar_conta_fixa(usuario_uuid):
    plano = obter_plano_dados(usuario_uuid)
    return plano and plano["pode_conta_fixa"] == 1


def pode_usar_grafico(usuario_uuid):
    plano = obter_plano_dados(usuario_uuid)
    return plano and plano["pode_grafico"] == 1