# =========================================
# ERROS GERAIS
# =========================================

def erro_nao_entendi():
    return (
        "❌ Não consegui entender sua mensagem.\n\n"
        "Tente escrever de forma simples.\n"
        "Digite /menu para ver as opções."
    )


def erro_comando_nao_reconhecido():
    return "❌ Comando não reconhecido. Digite /ajuda."


# =========================================
# ERROS DE VALORES
# =========================================

def erro_valor_invalido():
    return (
        "❌ Valor inválido.\n\n"
        "Exemplos corretos:\n"
        "• 25\n"
        "• 25,50\n"
        "• 1.250,75"
    )


def erro_valor_nao_encontrado():
    return (
        "❌ Não encontrei um valor na sua mensagem.\n\n"
        "Exemplos:\n"
        "• gastei 35 mercado\n"
        "• recebi 500 freelance"
    )


def erro_apenas_numero():
    return (
        "Você enviou apenas um valor.\n\n"
        "Diga o que aconteceu com ele.\n\n"
        "Exemplos:\n"
        "• gastei 50 mercado\n"
        "• recebi 120 freelance"
    )


# =========================================
# ERROS DE CADASTRO
# =========================================

def erro_nome_invalido():
    return "❌ Informe um nome válido para continuar."


def erro_email_invalido():
    return "❌ Email inválido. Informe um email válido."


def erro_email_em_uso():
    return "❌ Este email já está em uso. Informe outro."


def erro_senha_curta():
    return "❌ A senha deve ter pelo menos 6 caracteres."


# =========================================
# ERROS DE CARTÃO
# =========================================

def erro_sem_cartao():
    return "❌ Você ainda não possui cartões cadastrados."


def erro_cartao_nao_encontrado():
    return "❌ Nenhum cartão ativo encontrado."
