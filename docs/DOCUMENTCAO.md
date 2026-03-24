# 📘 Documentação do Projeto

# FinBot — Borba Tech

---

## 1. Visão Geral

O **FinBot — Borba Tech** é um sistema financeiro composto por dois módulos principais:

* **Bot WhatsApp**: responsável pela interação com o usuário.
* **Backend + Painel Administrativo Web**: responsável pela lógica de negócio, persistência de dados e visualização das informações.

O objetivo do sistema é permitir o **controle financeiro completo**, incluindo:

* registro de gastos
* registro de rendas
* controle automático de saldo
* relatórios financeiros detalhados
* painel web para administração

---

## 2. Arquitetura Geral

```
Usuário
   │
   ▼
WhatsApp Bot (Node.js)
   │  requisições HTTP
   ▼
Backend Flask (Python)
   │
   ▼
Banco de Dados SQLite
```

---

## 3. Tecnologias Utilizadas

### Backend

* Python 3.11+
* Flask
* SQLite
* APScheduler

### Bot

* Node.js
* whatsapp-web.js

### Front-end

* HTML
* CSS
* JavaScript

---

## 4. Estrutura de Pastas

```
finbot-borba-tech/
│
├── backend/
│   ├── admin_painel/        # Painel administrativo web
│   │   ├── templates/
│   │   └── static/
│   │
│   ├── db/
│   │   └── database.py      # Conexão com SQLite
│   │
│   ├── models/              # Camada de acesso ao banco
│   │   ├── gasto.py
│   │   ├── renda.py
│   │   ├── usuario.py
│   │   └── cartao.py
│   │
│   ├── services/            # Regras de negócio
│   │   ├── bot_service.py
│   │   └── relatorio_service.py
│   │
│   ├── scheduler.py         # Tarefas automáticas
│   └── app.py               # Aplicação Flask
│
├── whatsapp_bot/             # Bot WhatsApp
│   ├── index.js
│   └── package.json
│
├── docs/                     # Documentação e imagens
│   └── images/
│
├── start_finbot.ps1
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 5. Banco de Dados

### Banco

* Tipo: **SQLite**
* Criação automática na primeira execução
* Arquivo não versionado no Git

### Principais Tabelas

#### usuários

| Campo | Tipo | Descrição                |
| ----- | ---- | ------------------------ |
| uuid  | TEXT | Identificador do usuário |
| nome  | TEXT | Nome                     |
| saldo | REAL | Saldo atual              |

---

#### compras (gastos)

| Campo        | Tipo     | Descrição          |
| ------------ | -------- | ------------------ |
| id           | INTEGER  | PK                 |
| usuario_uuid | TEXT     | FK usuário         |
| descricao    | TEXT     | Descrição do gasto |
| valor        | REAL     | Valor              |
| data         | DATETIME | Data do registro   |

---

#### rendas

| Campo        | Tipo     | Descrição  |
| ------------ | -------- | ---------- |
| id           | INTEGER  | PK         |
| usuario_uuid | TEXT     | FK usuário |
| descricao    | TEXT     | Origem     |
| valor        | REAL     | Valor      |
| data         | DATETIME | Data       |

---

## 6. Fluxo de Funcionamento

### Registro de Gasto

1. Usuário envia comando pelo WhatsApp
2. Bot interpreta a mensagem
3. Backend registra o gasto
4. Saldo é atualizado automaticamente
5. Dados são persistidos no banco

---

### Registro de Renda

1. Usuário envia comando
2. Backend registra renda
3. Saldo é incrementado
4. Banco atualizado

---

## 7. Relatórios Financeiros

### Relatório Diário

* lista todos os gastos do dia
* mostra total gasto
* mostra entradas do dia
* mostra saldo atual

### Relatório Semanal

* lista gastos dos últimos 7 dias
* total consolidado

### Relatório Mensal

* lista gastos do mês
* total mensal

### Relatório Avançado

* resumo mensal
* gastos no cartão
* top gastos
* comparação mensal

---

## 8. Comandos do Bot

| Comando                  | Função               |
| ------------------------ | -------------------- |
| `/saldo`                 | Mostra o saldo atual |
| `/gasto valor descrição` | Registra gasto       |
| `/renda valor descrição` | Registra renda       |
| `/hoje`                  | Relatório diário     |
| `/semana`                | Relatório semanal    |
| `/mês`                   | Relatório mensal     |
| `/relatorio`             | Relatório avançado   |
| `/extrato`               | Últimos gastos       |
| `/comandos`              | Lista de comandos    |

---

## 9. Painel Administrativo

O painel administrativo permite:

* visualização de gastos
* visualização de rendas
* acompanhamento financeiro
* organização dos dados

Acesso local:

```
http://localhost:5000/admin
```

---

## 10. Segurança

* banco SQLite não versionado
* sessões do WhatsApp ignoradas
* tokens protegidos via `.env`
* `.gitignore` configurado corretamente

---

## 11. Execução do Projeto

### Backend

```bash
cd backend
python app.py
```

### Bot WhatsApp

```bash
cd whatsapp_bot
node index.js
```

---

## 12. Possíveis Evoluções

* autenticação no painel
* controle de planos (free/premium)
* gráficos financeiros
* exportação PDF
* API pública
* deploy em nuvem

---

## 13. Desenvolvedor

**Max Borba**
**Borba Tech**

---

## 14. Conclusão

O FinBot foi desenvolvido seguindo boas práticas de arquitetura, separação de responsabilidades e segurança, sendo um sistema totalmente funcional e preparado para evolução, deploy e uso real.
