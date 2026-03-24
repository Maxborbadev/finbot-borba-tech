def parse_valor(texto):
    if not texto:
        raise ValueError("Valor vazio")

    texto = texto.strip().replace(" ", "")

    if "." in texto and "," in texto:
        # Ex: 1.234,56 → 1234.56
        texto = texto.replace(".", "").replace(",", ".")
    elif "." in texto:
        # Ex: 4.000 → 4000
        texto = texto.replace(".", "")
    elif "," in texto:
        # Ex: 4,50 → 4.50
        texto = texto.replace(",", ".")

    return float(texto)

def dinheiro(valor):
    if valor is None:
        return "0,00"
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
