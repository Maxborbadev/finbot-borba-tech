import os
from dotenv import load_dotenv

load_dotenv()
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
ENV = os.getenv("ENV")
print("Ambiente:", ENV)

from flask import Flask, request, jsonify
from services.bot_service import processar_mensagem
from db.database import criar_tabelas, criar_admin_padrao
from utils.formatters import dinheiro 


app = Flask(__name__)

app.jinja_env.filters["dinheiro"] = dinheiro


# ─────────────────────────
# INICIALIZA O BANCO (1x)
# ─────────────────────────
criar_tabelas()
criar_admin_padrao()


# ─────────────────────────
# ENDPOINT DO BOT
# ─────────────────────────
@app.route("/mensagem", methods=["POST"])
def receber_mensagem():
    try:
        data = request.get_json(silent=True) or {}

        whatsapp_id = str(data.get("telefone", "")).strip()
        texto = str(data.get("texto", "")).strip()

        if not whatsapp_id or not texto:
            return jsonify({"resposta": ""})

        resposta = processar_mensagem(whatsapp_id, texto)
        return jsonify({"resposta": resposta})

    except Exception as e:
        print(f"[ERRO] {e}")
        return (
            jsonify(
                {
                    "resposta": "Ocorreu um erro ao processar sua mensagem. Tente novamente."
                }
            ),
            500,
        )


if __name__ == "__main__":

    if ENV == "development":
        app.run(port=5000, debug=True)

    else:
        app.run(port=5000)
