require("dotenv").config();
const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
} = require("@whiskeysockets/baileys");

const Pino = require("pino");
const qrcode = require("qrcode-terminal");
const axios = require("axios");
const express = require("express");
const path = require("path");
const multer = require("multer");
const upload = multer({ dest: "uploads/" });
const filaMensagens = [];
const BASE_URL = process.env.BASE_URL;
console.log("🌐 Backend URL:", BASE_URL);
let enviando = false;
let iniciando = false;

const app = express();
app.use(express.json());

let sock;

async function startBot() {
  if (iniciando) return;
  iniciando = true;

  try {
    const { state, saveCreds } = await useMultiFileAuthState("auth");

    sock = makeWASocket({
      logger: Pino({ level: "silent" }),
      auth: state,

      browser: ["Windows", "Chrome", "121.0.0"],

      markOnlineOnConnect: true,
      syncFullHistory: false,
      generateHighQualityLinkPreview: false,

      connectTimeoutMs: 60000,
      defaultQueryTimeoutMs: 60000,

      keepAliveIntervalMs: 10000, // 🔥 mantém conexão viva (ESSENCIAL no GCP)

      retryRequestDelayMs: 250,
    });

    sock.ev.on("creds.update", saveCreds);

    let reconnectTentativas = 0;

    sock.ev.on("connection.update", (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        qrcode.generate(qr, { small: true });
        console.log("📱 Escaneie o QR Code acima");
      }

      if (connection === "open") {
        console.log("🤖 Conectado com sucesso");
        reconnectTentativas = 0;
      }

      if (connection === "close") {
        const statusCode = lastDisconnect?.error?.output?.statusCode;

        console.log("⚠️ Conexão fechada:", statusCode);

        // 🔥 TRATAMENTO DO 405
        if (statusCode === 405) {
          reconnectTentativas++;

          const delay = Math.min(15000 * reconnectTentativas, 120000);

          console.log(`🚫 405 detectado. Aguardando ${delay / 1000}s...`);

          setTimeout(() => startBot(), delay);
          return;
        }

        if (statusCode === DisconnectReason.loggedOut) {
          console.log("❌ Sessão inválida. Apague a pasta auth.");
          return;
        }

        console.log("🔄 Reconectando normal...");
        setTimeout(() => startBot(), 5000);
      }
    });
    // ─────────────────────────
    // RECEBER MENSAGENS
    // ─────────────────────────
    sock.ev.on("messages.upsert", async ({ messages, type }) => {
      if (type !== "notify") return;

      const msg = messages[0];
      if (!msg.message || msg.key.fromMe) return;

      const texto =
        msg.message.conversation || msg.message.extendedTextMessage?.text;

      if (!texto) return;

      const chatId = msg.key.remoteJid;
      const telefone = chatId.replace("@s.whatsapp.net", "");

      console.log("📩 Mensagem recebida:", texto);

      try {
        const response = await axios.post(`${BASE_URL}/mensagem`, {
          telefone,
          texto,
        });

        const resposta = response.data?.resposta;

        if (Array.isArray(resposta)) {
          for (const msg of resposta) {
            if (typeof msg === "string") {
              await sock.sendMessage(chatId, { text: msg });
            } else if (msg.imagem) {
              await sock.sendMessage(chatId, {
                image: { url: msg.imagem },
                caption: "📷 Escaneie o QR Code para pagar",
              });
            }

            await new Promise((r) => setTimeout(r, 800));
          }
        } else if (resposta) {
          await sock.sendMessage(chatId, { text: resposta });
        }
      } catch (err) {
        console.error("❌ Erro ao comunicar com Flask:", err.message);

        await sock.sendMessage(chatId, {
          text: "⚠️ Ocorreu um erro ao processar sua mensagem. Tente novamente.",
        });
      }
    });
  } catch (err) {
    console.error("Erro ao iniciar:", err);
  } finally {
    iniciando = false;
  }
}

startBot();

// ─────────────────────────
// API PARA ENVIAR MENSAGEM
// ─────────────────────────

app.post("/enviar", async (req, res) => {
  const { numero, mensagem } = req.body;

  console.log("📨 Mensagem recebida para envio:", numero);

  filaMensagens.push({
    numero,
    mensagem,
  });

  processarFila();

  res.json({ status: "na_fila" });
});

app.post("/enviar-documento", upload.single("arquivo"), async (req, res) => {
  const numero = req.body.numero;
  const arquivo = req.file;

  console.log("📄 PDF recebido para envio:", numero);

  try {
    const fs = require("fs");

    const buffer = fs.readFileSync(arquivo.path);

    await sock.sendMessage(numero, {
      document: buffer,
      mimetype: "application/pdf",
      fileName: "fatura.pdf",
      caption:
        "📄 *Fatura do mês disponível!*\n\n💰 Confira todos os seus gastos organizados no PDF.\n\n🤖 FinBot - Borba Tech",
    });

    console.log("✅ PDF enviado:", numero);

    // remove arquivo depois
    fs.unlinkSync(arquivo.path);

    res.json({ status: "enviado" });
  } catch (err) {
    console.error("❌ Erro ao enviar PDF:", err);

    res.status(500).json({ erro: "erro ao enviar pdf" });
  }
});

app.listen(3000, () => {
  console.log("🚀 API do bot rodando na porta 3000");
});

async function processarFila() {
  if (enviando) return;
  enviando = true;

  while (filaMensagens.length > 0) {
    const { numero, mensagem } = filaMensagens.shift();

    try {
      await sock.sendMessage(numero, { text: mensagem });

      console.log("✅ Mensagem enviada:", numero);
    } catch (err) {
      console.error("❌ Erro ao enviar:", numero, err);
    }

    // espera 2 segundos entre cada envio
    await new Promise((r) => setTimeout(r, 2000));
  }

  enviando = false;
}
