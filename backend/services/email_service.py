import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config


def enviar_email_recuperacao(destinatario, link):

    remetente = Config.EMAIL_USER

    assunto = "Recuperação de senha - FinBot"

    html = f"""
    <html>
    <body style="font-family:Arial;background:#f4f6fb;padding:40px;">

        <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:10px;
            padding:30px;
            box-shadow:0 4px 15px rgba(0,0,0,0.1);
        ">

            <h2 style="color:#1f2937;">🔑 Recuperação de senha</h2>

            <p style="color:#374151;font-size:16px;">
                Recebemos um pedido para redefinir sua senha no <b>FinBot</b>.
            </p>

            <p style="color:#374151;font-size:16px;">
                Clique no botão abaixo para criar uma nova senha:
            </p>

            <div style="margin:30px 0;text-align:center;">
                <a href="{link}" 
                style="
                    background:#2563eb;
                    color:white;
                    padding:14px 28px;
                    text-decoration:none;
                    border-radius:6px;
                    font-weight:bold;
                    display:inline-block;
                ">
                    Redefinir senha
                </a>
            </div>

            <p style="color:#6b7280;font-size:14px;">
                Este link expira em <b>30 minutos</b>.
            </p>

            <p style="color:#6b7280;font-size:14px;">
                Se você não solicitou esta recuperação, ignore este email.
            </p>

            <hr style="margin:30px 0;border:none;border-top:1px solid #e5e7eb;">

            <p style="color:#9ca3af;font-size:12px;">
                FinBot • Assistente financeiro<br>
                © BorbaTech
            </p>

        </div>

    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    msg.attach(MIMEText(html, "html"))

    try:

        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()

        servidor.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)

        servidor.sendmail(remetente, destinatario, msg.as_string())

        servidor.quit()

        print(f"[EMAIL] enviado para {destinatario}")

    except Exception as e:
        print(f"[ERRO EMAIL] {e}")
