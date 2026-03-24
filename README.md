# 🤖 FinBot — Agente Financeiro



**FinBot — Agente Financeiro** é um bot desenvolvido para **uso pessoal**, com o objetivo de auxiliar no **controle financeiro diário**.

Ele permite registrar **gastos, rendas, contas fixas e gastos no cartão diretamente pelo WhatsApp**, além de oferecer um **painel administrativo web** com gráficos e visualizações detalhadas.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-LTS-339933?style=for-the-badge&logo=node.js&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

🔗 **Repositório oficial**  
https://github.com/Maxborbadev/finbot-borba-tech

---

## 🎯 Objetivo do Projeto

- Facilitar o controle financeiro pessoal  
- Centralizar registros financeiros via WhatsApp  
- Oferecer visualização clara e organizada dos dados  
- Servir como projeto de portfólio e base para evolução futura  

---

## 👤 Público-alvo

- Uso pessoal  
- Usuários que desejam controlar finanças de forma simples e prática  

---

## 🧠 Visão Geral de Funcionamento

1. O usuário interage com o FinBot via **WhatsApp**  
2. Registra gastos, rendas e contas fixas por mensagens ou comandos  
3. Os dados são processados por um **back-end em Python**  
4. Um **painel web administrativo** permite visualizar gráficos e informações detalhadas  
5. O sistema roda localmente, com acesso externo via **Ngrok**  

---

## 💬 Comandos do Bot

### 📘 Principais
- `/menu` → Menu principal  
- `/comandos` → Lista de comandos  
- `/ajuda` → Instruções de uso  
- `/saldo` → Ver saldo atual  
- `/plano` → Ver plano atual  

### 💸 Lançamentos
- `/gasto` → Registrar gasto  
- `/renda` → Registrar renda  
- `/cartao` → Registrar gastos no cartão  

### 📆 Contas Fixas
- `/contafixa` → Cadastrar conta fixa  
- `/fixas` → Listar contas fixas  
- `/removerconta` → Remover conta fixa  

### 📊 Relatórios
- `/hoje` ou `/dia` → Resumo diário  
- `/semanal` → Resumo semanal  
- `/mensal` → Resumo mensal  
- `/avancado` → Relatório completo  

### ⚙️ Ajustes
- `/attsaldo` → Ajustar saldo  
- `/attsalario` → Ajustar salário  

---

## ⚙️ Funcionalidades

- Registro de gastos e rendas via WhatsApp  
- Cadastro de contas fixas (valor, periodicidade e vencimento)  
- Controle de gastos no cartão com parcelamento  
- Visualização dos últimos lançamentos diretamente no bot  
- Painel administrativo com:
  - Gráficos de entradas e saídas  
  - Gráficos de linha  
  - Gráficos em pizza  
- Autenticação por login e senha  
- Categorização automática de gastos por palavras-chave  

---

## 🧩 Arquitetura Geral

- **Node.js** → Integração com WhatsApp  
- **Python** → Lógica de negócio e processamento  
- **Flask** → Painel administrativo web  
- **SQLite** → Persistência de dados  
- **PowerShell (.ps1)** → Inicialização automatizada do sistema  

> Todos os serviços são iniciados automaticamente por meio de um script PowerShell.

---

## 🛠️ Tecnologias Utilizadas

### 🔹 Back-end
- Python  
- Flask 3.1.2  
- Flask-WTF 1.2.2  
- Werkzeug 3.1.5  
- python-dotenv 1.2.1  
- schedule 1.2.2  

### 🔹 Front-end
- HTML5  
- CSS3  
- JavaScript  

### 🔹 Infraestrutura
- Node.js  
- npm  
- Ngrok  
- PowerShell  

---

## 📁 Estrutura do Projeto

```text
finbot-borba-tech/
├── backend/
│   ├── admin_painel/
│   ├── db/
│   ├── models/
│   ├── services/
│   ├── utils/
│   ├── app.py
│   ├── scheduler.py
│   └── requirements.txt
├── whatsapp_bot/
├── docs/
├── venv/
├── requirements.txt
├── start_finbot.ps1
└── README.md
```

---

## ▶️ Como Executar o Projeto

### ✅ Pré-requisitos
- Python 3.x  
- Node.js + npm  
- PowerShell (Windows)  

### 🔽 Clonar o repositório

```bash
git clone https://github.com/Maxborbadev/finbot-borba-tech
cd finbot-borba-tech
```

---

### 2️⃣ Ambiente virtual

```bash
python -m venv venv
```

**Ativação**

```bash
# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

---

### 3️⃣ Dependências Python

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Dependências do bot

```bash
cd whatsapp_bot
npm install
```

---

## ▶️ Executando o Sistema

### ✔ Windows (automático)

```bash
start_finbot.ps1
```

---

### ✔ Manual

**Backend**

```bash
cd backend
python app.py
```

Servidor:

```
http://localhost:5000
```

---

**Bot WhatsApp**

```bash
cd whatsapp_bot
node index.js
```

Na primeira execução será exibido um **QR Code** para autenticação.

---

## 🖥️ Painel Administrativo

Acesse pelo navegador:

```
http://localhost:5000/admin
```

---

## ⚠️ Limitações Atuais

- Não utiliza API oficial do WhatsApp
- Não envia mensagens automáticas
- Execução apenas local
- Scheduler sem envio automático de mensagens

---
## 👨‍💻 Desenvolvedor

**Max Borba**  
**Borba Tech**

---

### ⭐ Se este projeto te ajudou, deixe uma estrela no GitHub


