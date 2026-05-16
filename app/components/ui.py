"""
Componentes de UI reutilizáveis.
"""
import streamlit as st
from app.utils.helpers import status_cor, status_emoji


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
