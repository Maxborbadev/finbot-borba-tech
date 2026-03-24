import requests

url = "http://127.0.0.1:5000/mensagem"

telefone = "22219"

while True:
    texto = input("Mensagem: ")

    data = {
        "telefone": telefone,
        "texto": texto
    }

    r = requests.post(url, json=data)

    print("Bot:", r.json()["resposta"])
    print()