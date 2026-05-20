"""
Componentes de UI reutilizáveis.
"""
import time
import streamlit as st
from app.utils.helpers import status_cor, status_emoji

# ─────────────────────────────────────────────────────────────
#  SISTEMA DE NOTIFICAÇÕES / FOLLOW-UP
# ─────────────────────────────────────────────────────────────

def notificar(mensagem: str, tipo: str = "sucesso", icone: str = "") -> None:
    """
    Armazena uma notificação na sessão para ser exibida na próxima renderização.
    tipo: "sucesso" | "erro" | "aviso" | "info"
    """
    if "notificacoes" not in st.session_state:
        st.session_state["notificacoes"] = []
    st.session_state["notificacoes"].append({
        "mensagem": mensagem,
        "tipo": tipo,
        "icone": icone,
    })


def exibir_notificacoes() -> None:
    """
    Exibe e limpa todas as notificações pendentes da sessão.
    Chame no topo de cada página para garantir que o toast apareça após redirect.
    """
    notificacoes = st.session_state.pop("notificacoes", [])
    for n in notificacoes:
        _renderizar_toast(n["mensagem"], n["tipo"], n["icone"])


def _renderizar_toast(mensagem: str, tipo: str, icone: str) -> None:
    """Renderiza um toast/banner visual de notificação."""
    estilos = {
        "sucesso": {
            "bg": "#F0FDF4", "border": "#4ADE80", "texto": "#14532D",
            "icone_pad": "✅", "titulo": "Operação realizada com sucesso",
        },
        "erro": {
            "bg": "#FEF2F2", "border": "#F87171", "texto": "#7F1D1D",
            "icone_pad": "❌", "titulo": "Ocorreu um erro",
        },
        "aviso": {
            "bg": "#FFFBEB", "border": "#FCD34D", "texto": "#78350F",
            "icone_pad": "⚠️", "titulo": "Atenção",
        },
        "info": {
            "bg": "#EFF6FF", "border": "#60A5FA", "texto": "#1E3A8A",
            "icone_pad": "ℹ️", "titulo": "Informação",
        },
    }
    s = estilos.get(tipo, estilos["info"])
    icone_final = icone or s["icone_pad"]

    st.markdown(f"""
    <div style="
        display: flex;
        align-items: flex-start;
        gap: 0.875rem;
        background: {s['bg']};
        border: 1.5px solid {s['border']};
        border-left: 5px solid {s['border']};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
        animation: slideIn 0.3s ease;
        font-family: 'DM Sans', sans-serif;
    ">
        <div style="font-size: 1.4rem; line-height: 1; flex-shrink: 0;">{icone_final}</div>
        <div>
            <div style="font-weight: 700; color: {s['texto']}; font-size: 0.88rem; margin-bottom: 2px;">
                {s['titulo']}
            </div>
            <div style="color: {s['texto']}; font-size: 0.85rem; opacity: 0.9;">{mensagem}</div>
        </div>
    </div>
    <style>
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(-8px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
    """, unsafe_allow_html=True)


def redirecionar_apos_salvar(
    pagina_destino: str,
    segundos: int = 2,
    limpar_keys: list = None,
) -> None:
    """
    Exibe um banner de sucesso com countdown e redireciona automaticamente.
    Deve ser chamado APÓS notificar().
    """
    limpar_keys = limpar_keys or []

    placeholder = st.empty()

    for i in range(segundos, 0, -1):
        with placeholder.container():
            st.markdown(f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 0.875rem;
                background: #EFF6FF;
                border: 1.5px solid #60A5FA;
                border-left: 5px solid #3B82F6;
                border-radius: 10px;
                padding: 0.875rem 1.25rem;
                font-family: 'DM Sans', sans-serif;
            ">
                <div style="font-size: 1.25rem; flex-shrink: 0;">🔄</div>
                <div>
                    <div style="font-weight: 700; color: #1E3A8A; font-size: 0.85rem;">
                        Redirecionando em {i} segundo{'s' if i > 1 else ''}...
                    </div>
                    <div style="color: #3B82F6; font-size: 0.78rem; margin-top: 2px;">
                        Você será levado automaticamente para a tela de consulta.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        time.sleep(1)

    placeholder.empty()

    # Limpar estados antes de redirecionar
    for key in limpar_keys:
        st.session_state.pop(key, None)

    st.session_state["pagina_ativa"] = pagina_destino
    st.rerun()


def page_header(titulo: str, subtitulo: str = "", icone: str = "") -> None:
    """Renderiza o cabeçalho padronizado de uma página."""
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <div class="page-title">{icone} {titulo}</div>
        {'<div class="page-subtitle">' + subtitulo + '</div>' if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """Retorna HTML de badge colorido para o status."""
    mapa_classe = {
        "Agendado": "badge-agendado",
        "Em carregamento": "badge-carregamento",
        "Em trânsito": "badge-transito",
        "Entregue": "badge-entregue",
        "Cancelado": "badge-cancelado",
    }
    classe = mapa_classe.get(status, "badge-agendado")
    emoji = status_emoji(status)
    return f'<span class="badge {classe}">{emoji} {status}</span>'


def card_metrica(
    titulo: str,
    valor: str,
    icone: str = "",
    cor: str = "#1E40AF",
    subtitulo: str = ""
) -> str:
    """Retorna HTML de card de métrica customizado."""
    return f"""
    <div style="
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border-left: 4px solid {cor};
        height: 100%;
    ">
        <div style="
            font-family: 'DM Sans', sans-serif;
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.75rem;
        ">{icone} {titulo}</div>
        <div style="
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1;
            margin-bottom: 0.25rem;
        ">{valor}</div>
        {'<div style="font-size: 0.78rem; color: #94A3B8; margin-top: 4px;">' + subtitulo + '</div>' if subtitulo else ''}
    </div>
    """


def divider(label: str = "") -> None:
    """Renderiza um divisor com label opcional."""
    if label:
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 1.5rem 0;
        ">
            <div style="flex: 1; height: 1px; background: #E2E8F0;"></div>
            <div style="
                font-size: 0.75rem;
                font-weight: 600;
                color: #94A3B8;
                text-transform: uppercase;
                letter-spacing: 1px;
                white-space: nowrap;
            ">{label}</div>
            <div style="flex: 1; height: 1px; background: #E2E8F0;"></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<hr style="border-color: #E2E8F0; margin: 1.5rem 0;">', unsafe_allow_html=True)


def info_row(label: str, valor: str) -> str:
    """Retorna HTML de linha de informação label: valor."""
    return f"""
    <div style="
        display: flex;
        justify-content: space-between;
        padding: 0.6rem 0;
        border-bottom: 1px solid #F1F5F9;
        font-family: 'DM Sans', sans-serif;
    ">
        <span style="color: #64748B; font-size: 0.88rem; font-weight: 500;">{label}</span>
        <span style="color: #0F172A; font-size: 0.88rem; font-weight: 600;">{valor}</span>
    </div>
    """
