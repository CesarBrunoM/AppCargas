"""
Componente de estilos CSS globais da aplicação.
"""


def aplicar_estilos() -> str:
    """Retorna o CSS global da aplicação."""
    return """
    <style>
        /* === IMPORTAÇÃO DE FONTES === */
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        /* === VARIÁVEIS GLOBAIS === */
        :root {
            --primary: #1E40AF;
            --primary-light: #3B82F6;
            --primary-dark: #1E3A8A;
            --accent: #F59E0B;
            --accent-light: #FCD34D;
            --success: #10B981;
            --danger: #EF4444;
            --warning: #F59E0B;
            --info: #8B5CF6;
            --bg-main: #F8FAFC;
            --bg-card: #FFFFFF;
            --text-primary: #0F172A;
            --text-secondary: #64748B;
            --border: #E2E8F0;
            --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.10), 0 8px 32px rgba(0,0,0,0.06);
            --radius: 12px;
            --radius-sm: 8px;
        }

        /* === RESET & BASE === */
        * { box-sizing: border-box; }

        .stApp {
            background: var(--bg-main) !important;
            font-family: 'DM Sans', sans-serif !important;
        }

        h1, h2, h3, h4 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }

        /* === SIDEBAR === */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.06) !important;
        }

        [data-testid="stSidebar"] * {
            color: #CBD5E1 !important;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #F8FAFC !important;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 0 !important;
        }

        /* === BOTÕES === */
        .stButton > button {
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
            border-radius: var(--radius-sm) !important;
            border: none !important;
            transition: all 0.2s ease !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
            color: white !important;
            box-shadow: 0 2px 8px rgba(59,130,246,0.35) !important;
        }

        .stButton > button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 16px rgba(59,130,246,0.45) !important;
        }

        /* === INPUTS === */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: var(--radius-sm) !important;
            border: 1.5px solid var(--border) !important;
            font-family: 'DM Sans', sans-serif !important;
            transition: border-color 0.2s !important;
        }

        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-light) !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
        }

        /* === MÉTRICAS === */
        [data-testid="stMetric"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius) !important;
            padding: 1.2rem 1.5rem !important;
            box-shadow: var(--shadow) !important;
        }

        [data-testid="stMetricValue"] {
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 700 !important;
            font-size: 2rem !important;
            color: var(--text-primary) !important;
        }

        [data-testid="stMetricLabel"] {
            font-family: 'DM Sans', sans-serif !important;
            color: var(--text-secondary) !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
        }

        /* === DATAFRAME === */
        [data-testid="stDataFrame"] {
            border-radius: var(--radius) !important;
            overflow: hidden !important;
            box-shadow: var(--shadow) !important;
        }

        /* === ALERTS === */
        .stAlert {
            border-radius: var(--radius-sm) !important;
        }

        /* === SEPARADORES === */
        hr {
            border-color: var(--border) !important;
            margin: 1.5rem 0 !important;
        }

        /* === CARDS CUSTOMIZADOS === */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 1.5rem;
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }

        .card-header {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border);
        }

        /* === STATUS BADGES === */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            font-family: 'DM Sans', sans-serif;
        }

        .badge-agendado { background: #DBEAFE; color: #1E40AF; }
        .badge-carregamento { background: #FEF3C7; color: #92400E; }
        .badge-transito { background: #EDE9FE; color: #5B21B6; }
        .badge-entregue { background: #D1FAE5; color: #065F46; }
        .badge-cancelado { background: #FEE2E2; color: #991B1B; }

        /* === PAGE TITLE === */
        .page-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }

        .page-subtitle {
            font-family: 'DM Sans', sans-serif;
            font-size: 0.95rem;
            color: var(--text-secondary);
            margin-bottom: 1.5rem;
        }

        /* === LOGIN PAGE === */
        .login-container {
            max-width: 420px;
            margin: 0 auto;
            padding: 2.5rem;
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        }

        /* === EXPANDER === */
        .streamlit-expanderHeader {
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
        }

        /* Ocultar menu do Streamlit */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            background: transparent !important;
        }
    </style>
    """


def sidebar_logo() -> str:
    """HTML do logo/cabeçalho da sidebar."""
    return """
    <div style="
        padding: 1.5rem 1rem 1rem;
        text-align: center;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1rem;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🚛</div>
        <div style="
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.2rem;
            font-weight: 700;
            color: #F8FAFC;
            letter-spacing: -0.5px;
        ">CargoFlow</div>
        <div style="
            font-size: 0.72rem;
            color: #64748B;
            font-weight: 400;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 2px;
        ">Sistema de Cargas</div>
    </div>
    """
