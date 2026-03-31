import os
import sqlite3
from utils.datetime_utils import agora_brasil_str
from werkzeug.security import generate_password_hash

# ======================================================
# CAMINHO DO BANCO
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "financas.db")


# ======================================================
# CONEXÃO PADRÃO (ÚNICA NO PROJETO)
# ======================================================
def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn

def garantir_coluna(conn, tabela, coluna, definicao):
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [c[1] for c in cursor.fetchall()]

    if coluna not in colunas:
        print(f"🔧 Criando coluna {coluna} em {tabela}")
        cursor.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"
        )
        conn.commit()


# ======================================================
# CRIA TODAS AS TABELAS
# ======================================================
def criar_tabelas():
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- USUARIOS ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    whatsapp_id TEXT UNIQUE,
    nome TEXT,
    email TEXT UNIQUE,
    senha TEXT,
    tipo_usuario TEXT DEFAULT 'usuario',
    salario REAL DEFAULT 0,
    saldo REAL DEFAULT 0,
    plano TEXT DEFAULT 'Free',
    plano_expira_em DATETIME,
    origem_premium TEXT,
    status TEXT DEFAULT 'ativo',
    estado TEXT DEFAULT 'novo',
    conta_ativa INTEGER DEFAULT 1,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- temporários cartão
    cartao_temp_nome TEXT,
    cartao_temp_valor REAL,
    cartao_temp_descricao TEXT,
    cartao_temp_fechamento INTEGER,

    -- NOVOS (parcelamento)
    cartao_temp_parcelas INTEGER,
    cartao_temp_parcelas_pagas INTEGER
    );
    """
    )

    # ---------------- RENDAS ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS rendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_uuid TEXT NOT NULL,
        valor REAL NOT NULL,
        descricao TEXT,
        data DATETIME NOT NULL,
        FOREIGN KEY (usuario_uuid)
            REFERENCES usuarios(uuid)
            ON DELETE CASCADE
    );
    """
    )

    # ---------------- COMPRAS ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_uuid TEXT NOT NULL,
        valor REAL NOT NULL,
        descricao TEXT,
        categoria TEXT,
        data DATETIME NOT NULL,
        FOREIGN KEY (usuario_uuid)
            REFERENCES usuarios(uuid)
            ON DELETE CASCADE
    );
    """
    )

    # ---------------- GASTOS CARTÃO ----------------
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS gastos_cartao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_uuid TEXT NOT NULL,
    cartao_id INTEGER NOT NULL,

    valor REAL NOT NULL,
    descricao TEXT,
    categoria TEXT,
    data_compra DATE NOT NULL,

    mes_fatura INTEGER NOT NULL,
    ano_fatura INTEGER NOT NULL,

    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,

    parcelado INTEGER DEFAULT 0,
    qtd_parcelas INTEGER,
    valor_parcela REAL,

    parcelas_pagas INTEGER DEFAULT 0,
    quitado INTEGER DEFAULT 0,
                   
    ultima_atualizacao DATE,
                   
    compra_id INTEGER,
    parcela_numero INTEGER,

    FOREIGN KEY (usuario_uuid)
        REFERENCES usuarios(uuid)
        ON DELETE CASCADE,
    FOREIGN KEY (cartao_id)
        REFERENCES cartoes(id)
        ON DELETE CASCADE
);
"""
    )
    # 🔹 impede parcelas duplicadas da mesma compra
    cursor.execute(
        """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_compra_parcela
    ON gastos_cartao (compra_id, parcela_numero)
    """
    )

    # 🔹 acelera buscas por usuário + fatura
    cursor.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_gastos_usuario_fatura
    ON gastos_cartao (usuario_uuid, mes_fatura, ano_fatura)
    """
    )

    # 🔹 acelera listagem de compras por usuário
    cursor.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_gastos_usuario
    ON gastos_cartao (usuario_uuid)
    """
    )

    # 🔹 acelera busca de parcelas da mesma compra
    cursor.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_gastos_compra
    ON gastos_cartao (compra_id)
    """
    )

    # ---------------- CARTÕES ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS cartoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_uuid TEXT NOT NULL,
        nome TEXT NOT NULL,
        bandeira TEXT,
        dia_fechamento INTEGER NOT NULL,
        dia_vencimento INTEGER NOT NULL,
        limite REAL DEFAULT 0,
        ativo INTEGER DEFAULT 1,
        data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (usuario_uuid)
            REFERENCES usuarios(uuid)
            ON DELETE CASCADE
    );
    """
    )

    # ---------------- CONTAS FIXAS ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS contas_fixas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_uuid TEXT NOT NULL,
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        categoria TEXT NOT NULL,
        periodicidade TEXT NOT NULL,
        dia_vencimento INTEGER NOT NULL,
        ativa INTEGER DEFAULT 1,
        ultima_execucao DATETIME,
        data_criacao DATETIME NOT NULL,
        FOREIGN KEY (usuario_uuid)
            REFERENCES usuarios(uuid)
            ON DELETE CASCADE
    );
    """
    )

    # ---------------- CATEGORIAS ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_uuid TEXT NOT NULL,
        nome TEXT NOT NULL,
        FOREIGN KEY (usuario_uuid)
            REFERENCES usuarios(uuid)
            ON DELETE CASCADE
    );
    """
    )
    # ---------------- COFRINHO ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS cofrinho (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_uuid TEXT NOT NULL,
        valor REAL NOT NULL,
        data DATETIME NOT NULL,
        FOREIGN KEY (usuario_uuid)
            REFERENCES usuarios(uuid)
            ON DELETE CASCADE
    );
    """
    )

    # ---------------- PAGAMENTOS ----------------
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pagamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_uuid TEXT NOT NULL,
        payment_id TEXT UNIQUE,
        valor REAL,
        status TEXT DEFAULT 'pendente',
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (usuario_uuid)
            REFERENCES usuarios(uuid)
            ON DELETE CASCADE
    );
    """
    )

    # ---------------- PLANOS ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE,
        limite_mensal INTEGER,
        pode_cartao INTEGER DEFAULT 0,
        pode_conta_fixa INTEGER DEFAULT 0,
        pode_grafico INTEGER DEFAULT 0,
        preco REAL DEFAULT 0
    );
    """
    )

    # ---------------- RECUPERAÇÃO SENHA ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS recuperacao_senha (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expira_em DATETIME NOT NULL,
        usado INTEGER DEFAULT 0,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    )
    # ---------------- TENTATIVAS DE LOGIN BLOQUEIO ----------------
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS tentativas_login (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        ip TEXT,
        data DATETIME DEFAULT CURRENT_TIMESTAMP
    )
"""
    )
    # ======================================================
    # MIGRAÇÕES AUTOMÁTICAS
    # ======================================================

    garantir_coluna(conn, "gastos_cartao", "categoria", "TEXT")
    garantir_coluna(conn, "usuarios", "origem_premium", "TEXT")
    garantir_coluna(conn, "usuarios", "origem_premium", "TEXT")
    garantir_coluna(conn, "pagamentos", "valor", "REAL")


    # ---------------- PLANOS PADRÃO ----------------
    cursor.execute("""
    INSERT OR IGNORE INTO planos (nome, limite_mensal, pode_cartao, pode_conta_fixa, pode_grafico, preco)
    VALUES ('FREE', 10, 0, 0, 0, 0)
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO planos (nome, limite_mensal, pode_cartao, pode_conta_fixa, pode_grafico, preco)
    VALUES ('BASIC', 100, 1, 1, 1, 6.99)
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO planos (nome, limite_mensal, pode_cartao, pode_conta_fixa, pode_grafico, preco)
    VALUES ('PREMIUM', 999999, 1, 1, 1, 15.00)
    """)

    # Atualiza preços caso já existam
    cursor.execute("UPDATE planos SET preco = 6.99 WHERE nome = 'BASIC'")
    cursor.execute("UPDATE planos SET preco = 15.00 WHERE nome = 'PREMIUM'")

    # ---------------- CORRIGIR PLANOS DOS USUÁRIOS ----------------

    # Padroniza nomes
    cursor.execute("UPDATE usuarios SET plano = 'FREE' WHERE plano = 'Free'")
    cursor.execute("UPDATE usuarios SET plano = 'BASIC' WHERE plano = 'Basic'")
    cursor.execute("UPDATE usuarios SET plano = 'PREMIUM' WHERE plano = 'Premium'")

    # Garante que ninguém fique sem plano válido
    cursor.execute("""
    UPDATE usuarios
    SET plano = 'FREE'
    WHERE plano IS NULL OR plano NOT IN ('FREE', 'BASIC', 'PREMIUM')
    """)
    conn.commit()
    conn.close()

# ======================================================
# CRIA ADMIN PADRÃO (SE NÃO EXISTIR)
# ======================================================
def criar_admin_padrao():
    conn = get_connection()
    cursor = conn.cursor()

    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        raise Exception("ADMIN_PASSWORD não definida no .env")

    cursor.execute(
        """
        SELECT id
        FROM usuarios
        WHERE tipo_usuario = 'admin'
        LIMIT 1
    """
    )
 
    existe_admin = cursor.fetchone()

    if not existe_admin:
        cursor.execute(
            """
            INSERT INTO usuarios (
                uuid,
                nome,
                email,
                senha,
                tipo_usuario,
                plano,
                data_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "admin-001",
                "Administrador",
                "admin@finbot.com",
                generate_password_hash(admin_password),
                "admin",
                "PREMIUM",
                agora_brasil_str(),
            ),
        )

        conn.commit()

    conn.close()


# ======================================================
# EXECUÇÃO DIRETA
# ======================================================
if __name__ == "__main__":
    criar_tabelas()
    criar_admin_padrao()
    print("✅ Banco de dados verificado/criado com sucesso!")
