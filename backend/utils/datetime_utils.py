from datetime import datetime, timedelta


def agora_brasil():
    """
    Retorna a data e hora atual no fuso do Brasil (UTC-3)
    """
    return datetime.utcnow() - timedelta(hours=3)


def agora_brasil_str():
    """
    Retorna string pronta para salvar no banco
    """
    return agora_brasil().strftime("%Y-%m-%d %H:%M:%S")
