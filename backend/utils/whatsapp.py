import requests
import os
from dotenv import load_dotenv

load_dotenv()
BOT_URL = os.getenv("BOT_URL")
if not BOT_URL:
    raise Exception("BOT_URL não definido no .env")

def enviar_whatsapp(numero, mensagem):

    try:

        r = requests.post(
            f"{BOT_URL}/enviar",
            json={"numero": numero, "mensagem": mensagem},
            timeout=5,
        )

        print("Resposta do bot:", r.text)

    except Exception as e:

        print("Erro ao enviar mensagem:", e)


def enviar_whatsapp_documento(numero, caminho_pdf):

    try:
        with open(caminho_pdf, "rb") as arquivo:

            r = requests.post(
                f"{BOT_URL}/enviar-documento",
                files={"arquivo": arquivo},
                data={"numero": numero},
                timeout=10,
            )

        print("PDF enviado:", r.text)

        # 🔥 APAGA O PDF DEPOIS DE ENVIAR
        try:
            if os.path.exists(caminho_pdf):
                os.remove(caminho_pdf)
                print("🗑️ PDF removido com sucesso")
        except Exception as e:
            print("Erro ao remover PDF:", e)

    except Exception as e:
        print("Erro ao enviar PDF:", e)
