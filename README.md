# 🚛 CargoFlow — Sistema de Gerenciamento de Cargas

Sistema web profissional para gerenciamento e agendamento de cargas, construído com Python, Streamlit e SQLite.

---

## ✨ Funcionalidades

| Módulo | Descrição |
|---|---|
| 🔐 **Login** | Autenticação segura com bcrypt, sessão protegida, logout |
| 📊 **Dashboard** | Métricas em tempo real, gráficos de status e período, últimas cargas |
| 📦 **Nova Carga** | Formulário completo com validações, máscara de placa, calendário |
| 🔍 **Consultar Cargas** | Listagem paginada, filtros avançados, busca global |
| ✏️ **Editar Carga** | Atualização de status, dados operacionais e dados do agendamento |
| 📥 **Exportar** | Download dos resultados filtrados em Excel (.xlsx) |

### Status operacionais:
- 📅 Agendado
- 🔄 Em carregamento
- 🚛 Em trânsito
- ✅ Entregue
- ❌ Cancelado

---

## 🛠️ Tecnologias

- **Python 3.11+**
- **Streamlit** — Interface web
- **SQLAlchemy** — ORM e gerenciamento do banco
- **SQLite** — Banco de dados local
- **Pandas** — Manipulação de dados
- **Plotly** — Gráficos interativos
- **bcrypt** — Criptografia de senhas
- **openpyxl** — Exportação Excel

---

## 🚀 Instalação e Execução

### 1. Pré-requisitos

- Python 3.11 ou superior instalado
- pip atualizado

### 2. Clone ou extraia o projeto

```bash
cd carga_system
```

### 3. Crie e ative o ambiente virtual

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. (Opcional) Inicialize o banco com dados de exemplo

```bash
python init_db.py
```

Este script cria o banco, o usuário admin, um usuário operador e **20 cargas de exemplo** para testes.

### 6. Execute o sistema

```bash
streamlit run main.py
```

O sistema abrirá automaticamente em `http://localhost:8501`.

---

## 🔑 Credenciais Padrão

| Usuário | Senha | Perfil |
|---|---|---|
| `admin` | `admin123` | Administrador |
| `operador` | `op123456` | Operador (após init_db.py) |

> ⚠️ **Altere as senhas em produção!**

---

## 📁 Estrutura do Projeto

```
carga_system/
│
├── main.py                     # Ponto de entrada principal
├── init_db.py                  # Script de inicialização e seed
├── requirements.txt            # Dependências Python
├── README.md                   # Documentação
├── cargas.db                   # Banco de dados SQLite (gerado automaticamente)
│
├── .streamlit/
│   └── config.toml             # Configurações do Streamlit (tema, servidor)
│
└── app/
    ├── __init__.py
    │
    ├── models/                 # Modelos SQLAlchemy
    │   ├── __init__.py
    │   └── models.py           # Usuario, Carga, StatusCarga
    │
    ├── database/               # Configuração do banco de dados
    │   ├── __init__.py
    │   └── database.py         # Engine, sessão, init_db()
    │
    ├── services/               # Regras de negócio
    │   ├── __init__.py
    │   ├── auth_service.py     # Autenticação de usuários
    │   └── carga_service.py    # CRUD de cargas, métricas
    │
    ├── components/             # Componentes UI reutilizáveis
    │   ├── __init__.py
    │   ├── styles.py           # CSS global, sidebar logo
    │   └── ui.py               # Badges, cards, helpers de UI
    │
    ├── pages/                  # Páginas da aplicação
    │   ├── __init__.py
    │   ├── login.py            # Tela de login
    │   ├── dashboard.py        # Dashboard com métricas
    │   ├── nova_carga.py       # Formulário de cadastro
    │   ├── consultar_cargas.py # Listagem e filtros
    │   └── editar_carga.py     # Edição de carga
    │
    └── utils/                  # Utilitários gerais
        ├── __init__.py
        ├── security.py         # Hash e verificação de senhas
        └── helpers.py          # Formatação, validação de placa, etc.
```

---

## 🎨 Interface

- **Tema**: Azul corporativo com tipografia moderna (Space Grotesk + DM Sans)
- **Sidebar**: Navegação escura elegante com ícones
- **Cards**: Métricas coloridas com bordas indicadoras
- **Badges**: Status coloridos por categoria
- **Gráficos**: Pizza (distribuição de status) + Barras (cargas por período)
- **Tabelas**: DataFrames com paginação nativa do Streamlit

---

## 🔒 Segurança

- Senhas armazenadas com **bcrypt** (salt aleatório por senha)
- Proteção de todas as páginas via verificação de sessão
- Validação de inputs no backend (não apenas no frontend)
- Validação de formato de placa (padrão antigo e Mercosul)
- Tratamento de erros com rollback automático nas transações

---

## 📈 Expansão Futura

O sistema foi projetado para ser facilmente expandido:

- **Banco de dados**: Troque SQLite por PostgreSQL apenas mudando `DATABASE_URL`
- **Autenticação**: Adicione JWT ou OAuth2 no `auth_service.py`
- **Relatórios**: Adicione novas exportações no `carga_service.py`
- **Usuários**: Implemente gestão de perfis em uma nova página
- **API REST**: Extraia os services para um backend FastAPI

---

## 📄 Licença

Projeto desenvolvido para uso interno. Adapte conforme suas necessidades.
