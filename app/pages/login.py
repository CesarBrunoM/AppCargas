"""
Página de login do sistema.
"""
import streamlit as st
from app.database import get_db
from app.services import autenticar_usuario
from app.components import aplicar_estilos


def mostrar_login() -> bool:
    """
    Exibe a tela de login e processa a autenticação.
    Retorna True se o usuário estiver autenticado.
    """
    st.markdown(aplicar_estilos(), unsafe_allow_html=True)

    # Verificar se já está autenticado
    if st.session_state.get("autenticado"):
        return True

    # Layout centralizado
    col_left, col_center, col_right = st.columns([1, 1.4, 1])

    with col_center:
        # Logo e título
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1.5rem;">
            <div style="font-size: 4rem; margin-bottom: 0.5rem;">🚛</div>
            <div style="
                font-family: 'Space Grotesk', sans-serif;
                font-size: 2rem;
                font-weight: 700;
                color: #0F172A;
                letter-spacing: -1px;
            ">CargoFlow</div>
            <div style="
                font-family: 'DM Sans', sans-serif;
                font-size: 0.9rem;
                color: #64748B;
                margin-top: 4px;
            ">Sistema de Gerenciamento de Cargas</div>
        </div>
        """, unsafe_allow_html=True)

        # Card de login
        st.markdown("""
        <div style="
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            margin-top: 1rem;
        ">
            <div style="
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.1rem;
                font-weight: 600;
                color: #0F172A;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #F1F5F9;
            ">🔐 Entrar no sistema</div>
        """, unsafe_allow_html=True)

        with st.form("form_login", clear_on_submit=False):
            username = st.text_input(
                "Usuário",
                placeholder="Digite seu usuário",
                help="Username de acesso ao sistema"
            )
            senha = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha",
                help="Senha de acesso ao sistema"
            )

            col_btn, col_info = st.columns([1, 1])
            with col_btn:
                submitted = st.form_submit_button(
                    "Entrar →",
                    use_container_width=True,
                    type="primary"
                )

            if submitted:
                if not username or not senha:
                    st.error("⚠️ Preencha usuário e senha.")
                else:
                    db = get_db()
                    try:
                        usuario = autenticar_usuario(db, username.strip(), senha)
                        if usuario:
                            st.session_state["autenticado"] = True
                            st.session_state["usuario_id"] = usuario.id
                            st.session_state["usuario_nome"] = usuario.nome
                            st.session_state["usuario_username"] = usuario.username
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha incorretos.")
                    finally:
                        db.close()

        st.markdown("</div>", unsafe_allow_html=True)

        # Dica de acesso
        st.markdown("""
        <div style="
            text-align: center;
            margin-top: 1.5rem;
            padding: 0.75rem;
            background: #F8FAFC;
            border-radius: 8px;
            border: 1px solid #E2E8F0;
        ">
            <div style="font-size: 0.78rem; color: #94A3B8; font-family: 'DM Sans', sans-serif;">
                💡 Acesso padrão: <strong style="color:#64748B">admin</strong> / <strong style="color:#64748B">admin123</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return False


def logout() -> None:
    """Encerra a sessão do usuário."""
    for key in ["autenticado", "usuario_id", "usuario_nome", "usuario_username"]:
        st.session_state.pop(key, None)
    st.rerun()
