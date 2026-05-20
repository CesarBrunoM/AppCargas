"""
CargoFlow - Sistema de Gerenciamento e Agendamento de Cargas
============================================================
Ponto de entrada principal da aplicação Streamlit.

Execução:
    streamlit run main.py
"""
import logging
import streamlit as st

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Configuração da página - DEVE ser o primeiro comando Streamlit
st.set_page_config(
    page_title="CargoFlow | Sistema de Cargas",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "CargoFlow v1.0 - Sistema de Gerenciamento de Cargas",
    }
)

# Importações após set_page_config
from app.database import init_db
from app.components import aplicar_estilos, sidebar_logo
from app.pages.login import mostrar_login, logout


def inicializar_sessao() -> None:
    """Inicializa variáveis de sessão padrão."""
    defaults = {
        "autenticado": False,
        "usuario_id": None,
        "usuario_nome": None,
        "usuario_username": None,
        "pagina_ativa": "dashboard",
        "pagina_atual": 1,
        "ver_detalhe_id": None,
        "editar_carga_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def renderizar_sidebar() -> None:
    """Renderiza a sidebar de navegação."""
    with st.sidebar:
        st.markdown(sidebar_logo(), unsafe_allow_html=True)

        # Info do usuário
        st.markdown(f"""
        <div style="
            padding: 0.75rem 1rem;
            margin: 0 0 1rem;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.08);
        ">
            <div style="font-size: 0.72rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">Usuário logado</div>
            <div style="font-size: 0.9rem; font-weight: 600; color: #E2E8F0;">
                👤 {st.session_state.get('usuario_nome', 'Usuário')}
            </div>
            <div style="font-size: 0.75rem; color: #64748B;">
                @{st.session_state.get('usuario_username', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navegação principal
        st.markdown("""
        <div style="font-size: 0.7rem; color: #475569; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; padding: 0 0 0.5rem; margin-bottom: 0.25rem;">
            Navegação
        </div>
        """, unsafe_allow_html=True)

        pagina = st.session_state.get("pagina_ativa", "dashboard")

        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("nova_carga", "📦", "Nova Carga"),
            ("consultar", "🔍", "Consultar Cargas"),
        ]

        for key, icone, label in nav_items:
            ativo = pagina == key
            estilo_extra = "background: rgba(59,130,246,0.15); border: 1px solid rgba(59,130,246,0.3);" if ativo else ""
            cor_texto = "#93C5FD" if ativo else "#CBD5E1"

            if st.button(
                f"{icone}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
            ):
                # Limpar estados de edição ao navegar
                st.session_state["ver_detalhe_id"] = None
                st.session_state["editar_carga_id"] = None
                st.session_state["pagina_atual"] = 1
                st.session_state["pagina_ativa"] = key
                st.rerun()

        st.markdown("<div style='height: 1px; background: rgba(255,255,255,0.06); margin: 1rem 0;'></div>", unsafe_allow_html=True)

        # Botão de logout
        if st.button("🚪  Sair do Sistema", use_container_width=True, key="btn_logout"):
            logout()

        # Rodapé da sidebar
        st.markdown("""
        <div style="
            position: absolute;
            bottom: 1.5rem;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.68rem;
            color: #334155;
            padding: 0 1rem;
        ">
            CargoFlow v1.0 &nbsp;·&nbsp; 2024
        </div>
        """, unsafe_allow_html=True)


def main() -> None:
    """Função principal da aplicação."""
    # Inicializar banco de dados
    init_db()

    # Inicializar sessão
    inicializar_sessao()

    # Aplicar estilos globais
    st.markdown(aplicar_estilos(), unsafe_allow_html=True)

    # Verificar autenticação
    if not st.session_state.get("autenticado"):
        mostrar_login()
        return

    # Renderizar sidebar
    renderizar_sidebar()

    # Roteador de páginas
    pagina = st.session_state.get("pagina_ativa", "dashboard")

    if pagina == "dashboard":
        from app.pages.dashboard import mostrar_dashboard
        mostrar_dashboard()

    elif pagina == "nova_carga":
        from app.pages.nova_carga import mostrar_nova_carga
        mostrar_nova_carga()

    elif pagina == "consultar":
        from app.pages.consultar_cargas import mostrar_consultar_cargas
        mostrar_consultar_cargas()

    else:
        from app.pages.dashboard import mostrar_dashboard
        mostrar_dashboard()


if __name__ == "__main__":
    main()
