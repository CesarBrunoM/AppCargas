"""
Página de gerenciamento de usuários.
Acesso restrito a perfil Administrador.
"""
import streamlit as st
from app.database import get_db
from app.services import (
    listar_usuarios,
    criar_usuario,
    atualizar_usuario,
    redefinir_senha,
    alterar_senha_propria,
    toggle_ativo,
    buscar_usuario_por_id,
    is_admin,
    PERFIS,
)
from app.components import page_header, divider
from app.utils.helpers import formatar_data

# Mínimo de caracteres para senha
SENHA_MIN = 6


def mostrar_usuarios() -> None:
    """
    Ponto de entrada da página.
    Verifica permissão antes de renderizar.
    """
    perfil_sessao = st.session_state.get("usuario_perfil", "")
    usuario_id = st.session_state.get("usuario_id")

    # Não-admins só veem o painel de alterar a própria senha
    if not is_admin(perfil_sessao):
        _painel_minha_conta(usuario_id)
        return

    page_header(
        titulo="Gerenciar Usuários",
        subtitulo="Cadastre, edite, ative/desative e redefina senhas dos usuários do sistema.",
        icone="👥"
    )

    if st.button("← Voltar ao Dashboard", key="btn_voltar_usuarios"):
        st.session_state["pagina_ativa"] = "dashboard"
        st.rerun()

    # Sub-navegação via abas
    aba_lista, aba_novo, aba_minha_conta = st.tabs([
        "📋  Todos os Usuários",
        "➕  Novo Usuário",
        "🔑  Minha Conta",
    ])

    with aba_lista:
        _aba_lista(usuario_id)

    with aba_novo:
        _aba_novo_usuario()

    with aba_minha_conta:
        _painel_minha_conta(usuario_id, dentro_de_aba=True)


# ─────────────────────────────────────────────
#  ABA: LISTA DE USUÁRIOS
# ─────────────────────────────────────────────

def _aba_lista(admin_id: int) -> None:
    divider("Usuários cadastrados")

    db = get_db()
    try:
        usuarios = listar_usuarios(db)
    finally:
        db.close()

    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return

    # Cabeçalho da tabela
    st.markdown("""
    <div style="
        display: grid;
        grid-template-columns: 2fr 2fr 1.5fr 1fr 1fr 1fr;
        gap: 0.5rem;
        padding: 0.6rem 1rem;
        background: #F1F5F9;
        border-radius: 8px 8px 0 0;
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 1px solid #E2E8F0;
        border-bottom: none;
        font-family: 'DM Sans', sans-serif;
    ">
        <span>Nome</span>
        <span>Usuário / E-mail</span>
        <span>Perfil</span>
        <span>Status</span>
        <span>Criado em</span>
        <span>Ações</span>
    </div>
    """, unsafe_allow_html=True)

    for u in usuarios:
        _linha_usuario(u, admin_id)

    st.markdown(f"""
    <div style="text-align:right; font-size:0.78rem; color:#94A3B8; margin-top:0.75rem; font-family:'DM Sans',sans-serif;">
        {len(usuarios)} usuário(s) cadastrado(s)
    </div>
    """, unsafe_allow_html=True)


def _linha_usuario(u, admin_id: int) -> None:
    """Renderiza uma linha de usuário com ações inline."""
    ativo = u.ativo == 1
    badge_ativo = (
        '<span style="background:#D1FAE5;color:#065F46;padding:2px 8px;border-radius:99px;font-size:0.72rem;font-weight:700;">● Ativo</span>'
        if ativo else
        '<span style="background:#FEE2E2;color:#991B1B;padding:2px 8px;border-radius:99px;font-size:0.72rem;font-weight:700;">● Inativo</span>'
    )

    cor_perfil = "#1E40AF" if u.perfil == "Administrador" else "#5B21B6"
    bg_perfil = "#DBEAFE" if u.perfil == "Administrador" else "#EDE9FE"
    icone_perfil = "🛡️" if u.perfil == "Administrador" else "👤"

    st.markdown(f"""
    <div style="
        display: grid;
        grid-template-columns: 2fr 2fr 1.5fr 1fr 1fr 1fr;
        gap: 0.5rem;
        align-items: center;
        padding: 0.75rem 1rem;
        border: 1px solid #E2E8F0;
        border-top: none;
        background: {'#FAFAFA' if not ativo else 'white'};
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        color: {'#94A3B8' if not ativo else '#0F172A'};
    ">
        <span style="font-weight:600;">{u.nome}</span>
        <div>
            <div style="font-weight:500;">@{u.username}</div>
            <div style="font-size:0.75rem;color:#94A3B8;">{u.email or '—'}</div>
        </div>
        <span style="background:{bg_perfil};color:{cor_perfil};padding:3px 8px;border-radius:99px;font-size:0.72rem;font-weight:700;">
            {icone_perfil} {u.perfil}
        </span>
        <span>{badge_ativo}</span>
        <span style="font-size:0.78rem;color:#94A3B8;">{formatar_data(u.criado_em.date()) if u.criado_em else '—'}</span>
        <span></span>
    </div>
    """, unsafe_allow_html=True)

    # Ações — fora do HTML para usar botões Streamlit
    col_ed, col_senha, col_toggle = st.columns([1, 1, 1])

    with col_ed:
        if st.button("✏️ Editar", key=f"editar_{u.id}", width='stretch'):
            st.session_state["editar_usuario_id"] = u.id
            st.rerun()

    with col_senha:
        if st.button("🔑 Senha", key=f"senha_{u.id}", width='stretch'):
            st.session_state["redefinir_senha_id"] = u.id
            st.rerun()

    with col_toggle:
        label = "🔴 Desativar" if ativo else "🟢 Ativar"
        if st.button(label, key=f"toggle_{u.id}", width='stretch'):
            db = get_db()
            try:
                ok, msg = toggle_ativo(db, u.id, admin_id)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
                st.rerun()
            finally:
                db.close()

    # Painel de edição inline
    if st.session_state.get("editar_usuario_id") == u.id:
        _painel_editar_usuario(u)

    # Painel de redefinição de senha inline
    if st.session_state.get("redefinir_senha_id") == u.id:
        _painel_redefinir_senha(u)

    st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)


def _painel_editar_usuario(u) -> None:
    """Expander inline para editar dados do usuário."""
    with st.container():
        st.markdown(f"""
        <div style="
            background:#EFF6FF;
            border:1px solid #BFDBFE;
            border-radius:10px;
            padding:1.25rem 1.5rem;
            margin:0.25rem 0 0.5rem;
        ">
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;color:#1E40AF;margin-bottom:0.75rem;">
                ✏️ Editando: @{u.username}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form(f"form_editar_{u.id}"):
            col1, col2 = st.columns(2)
            with col1:
                novo_nome = st.text_input("Nome completo", value=u.nome, max_chars=100)
                novo_email = st.text_input("E-mail", value=u.email or "", max_chars=150, placeholder="email@exemplo.com")
            with col2:
                idx_perfil = PERFIS.index(u.perfil) if u.perfil in PERFIS else 0
                novo_perfil = st.selectbox("Perfil de acesso", options=PERFIS, index=idx_perfil)
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.info(f"Username **@{u.username}** não pode ser alterado.")

            col_salvar, col_cancelar = st.columns(2)
            with col_salvar:
                salvar = st.form_submit_button("💾 Salvar", width='stretch', type="primary")
            with col_cancelar:
                cancelar = st.form_submit_button("✖ Cancelar", width='stretch')

        if salvar:
            if not novo_nome.strip():
                st.error("O nome não pode estar vazio.")
            else:
                db = get_db()
                try:
                    resultado = atualizar_usuario(
                        db, u.id,
                        nome=novo_nome,
                        email=novo_email,
                        perfil=novo_perfil,
                    )
                    if resultado:
                        st.success(f"✅ Usuário @{u.username} atualizado!")
                        st.session_state.pop("editar_usuario_id", None)
                        st.rerun()
                    else:
                        st.error("Erro ao atualizar.")
                finally:
                    db.close()

        if cancelar:
            st.session_state.pop("editar_usuario_id", None)
            st.rerun()


def _painel_redefinir_senha(u) -> None:
    """Painel inline para redefinição de senha pelo admin."""
    with st.container():
        st.markdown(f"""
        <div style="
            background:#FFF7ED;
            border:1px solid #FED7AA;
            border-radius:10px;
            padding:1.25rem 1.5rem;
            margin:0.25rem 0 0.5rem;
        ">
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;color:#92400E;margin-bottom:0.75rem;">
                🔑 Redefinir senha de @{u.username}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form(f"form_senha_{u.id}"):
            nova = st.text_input("Nova senha", type="password", placeholder="Mínimo 6 caracteres")
            confirmar = st.text_input("Confirmar nova senha", type="password", placeholder="Repita a senha")

            col_s, col_c = st.columns(2)
            with col_s:
                salvar = st.form_submit_button("🔐 Redefinir senha", width='stretch', type="primary")
            with col_c:
                cancelar = st.form_submit_button("✖ Cancelar", width='stretch')

        if salvar:
            if len(nova) < SENHA_MIN:
                st.error(f"A senha deve ter ao menos {SENHA_MIN} caracteres.")
            elif nova != confirmar:
                st.error("As senhas não coincidem.")
            else:
                db = get_db()
                try:
                    ok = redefinir_senha(db, u.id, nova)
                    if ok:
                        st.success(f"✅ Senha de @{u.username} redefinida com sucesso!")
                        st.session_state.pop("redefinir_senha_id", None)
                        st.rerun()
                    else:
                        st.error("Erro ao redefinir senha.")
                finally:
                    db.close()

        if cancelar:
            st.session_state.pop("redefinir_senha_id", None)
            st.rerun()


# ─────────────────────────────────────────────
#  ABA: NOVO USUÁRIO
# ─────────────────────────────────────────────

def _aba_novo_usuario() -> None:
    divider("Cadastrar novo usuário")

    with st.form("form_novo_usuario", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            novo_nome = st.text_input("👤 Nome completo *", placeholder="Ex: Maria Souza", max_chars=100)
            novo_username = st.text_input(
                "🔖 Username *",
                placeholder="Ex: maria.souza (sem espaços)",
                max_chars=50,
                help="Usado para login. Letras minúsculas, números, ponto ou underline."
            )
            novo_email = st.text_input("📧 E-mail", placeholder="maria@empresa.com", max_chars=150)

        with col2:
            novo_perfil = st.selectbox(
                "🛡️ Perfil de acesso *",
                options=PERFIS,
                index=1,  # Operador como padrão
                help="Administrador tem acesso total, incluindo gerenciar usuários."
            )
            nova_senha = st.text_input(
                "🔒 Senha *",
                type="password",
                placeholder=f"Mínimo {SENHA_MIN} caracteres"
            )
            confirmar_senha = st.text_input(
                "🔒 Confirmar senha *",
                type="password",
                placeholder="Repita a senha"
            )

        # Descrição dos perfis
        st.markdown("""
        <div style="
            background:#F8FAFC;
            border:1px solid #E2E8F0;
            border-radius:8px;
            padding:0.85rem 1rem;
            font-size:0.82rem;
            color:#64748B;
            font-family:'DM Sans',sans-serif;
            margin-top:0.25rem;
        ">
            🛡️ <strong style="color:#1E40AF">Administrador</strong> — acesso completo: cargas + gerenciar usuários<br>
            👤 <strong style="color:#5B21B6">Operador</strong> — acesso às cargas (dashboard, nova carga, consultar)
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("➕ Cadastrar Usuário", width='stretch', type="primary")

    if submitted:
        erros = _validar_novo_usuario(novo_nome, novo_username, nova_senha, confirmar_senha)
        if erros:
            for e in erros:
                st.error(e)
        else:
            db = get_db()
            try:
                criado = criar_usuario(
                    db,
                    username=novo_username,
                    nome=novo_nome,
                    senha=nova_senha,
                    perfil=novo_perfil,
                    email=novo_email,
                )
                if criado:
                    st.success(f"✅ Usuário **@{criado.username}** ({criado.nome}) cadastrado com sucesso!")
                    st.balloons()
                else:
                    st.error(f"❌ Username **@{novo_username}** já está em uso. Escolha outro.")
            finally:
                db.close()


def _validar_novo_usuario(nome, username, senha, confirmar) -> list:
    """Valida os campos do formulário de novo usuário."""
    import re
    erros = []
    if not nome.strip():
        erros.append("⚠️ O campo **Nome** é obrigatório.")
    if not username.strip():
        erros.append("⚠️ O campo **Username** é obrigatório.")
    elif not re.match(r'^[a-zA-Z0-9._]+$', username):
        erros.append("⚠️ **Username** inválido. Use apenas letras, números, ponto ou underline.")
    if not senha:
        erros.append("⚠️ A **senha** é obrigatória.")
    elif len(senha) < SENHA_MIN:
        erros.append(f"⚠️ A senha deve ter ao menos **{SENHA_MIN} caracteres**.")
    if senha != confirmar:
        erros.append("⚠️ As **senhas não coincidem**.")
    return erros


# ─────────────────────────────────────────────
#  PAINEL: MINHA CONTA (qualquer perfil)
# ─────────────────────────────────────────────

def _painel_minha_conta(usuario_id: int, dentro_de_aba: bool = False) -> None:
    """Painel para o usuário logado ver seus dados e alterar a própria senha."""
    if not dentro_de_aba:
        page_header(
            titulo="Minha Conta",
            subtitulo="Visualize seus dados e altere sua senha.",
            icone="👤"
        )
        if st.button("← Voltar ao Dashboard", key="btn_voltar_conta"):
            st.session_state["pagina_ativa"] = "dashboard"
            st.rerun()

    db = get_db()
    try:
        u = buscar_usuario_por_id(db, usuario_id)
    finally:
        db.close()

    if not u:
        st.error("Usuário não encontrado.")
        return

    # Dados atuais
    divider("Seus dados")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background:white;border:1px solid #E2E8F0;border-radius:10px;padding:1rem;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.25rem;">👤</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1rem;color:#0F172A;">{u.nome}</div>
            <div style="font-size:0.78rem;color:#64748B;">@{u.username}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        cor_p = "#1E40AF" if u.perfil == "Administrador" else "#5B21B6"
        bg_p = "#DBEAFE" if u.perfil == "Administrador" else "#EDE9FE"
        st.markdown(f"""
        <div style="background:white;border:1px solid #E2E8F0;border-radius:10px;padding:1rem;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.25rem;">🛡️</div>
            <div style="background:{bg_p};color:{cor_p};display:inline-block;padding:3px 12px;border-radius:99px;font-size:0.82rem;font-weight:700;">{u.perfil}</div>
            <div style="font-size:0.75rem;color:#94A3B8;margin-top:4px;">perfil de acesso</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background:white;border:1px solid #E2E8F0;border-radius:10px;padding:1rem;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.25rem;">📅</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;color:#0F172A;">{formatar_data(u.criado_em.date()) if u.criado_em else '—'}</div>
            <div style="font-size:0.75rem;color:#94A3B8;">conta criada em</div>
        </div>
        """, unsafe_allow_html=True)

    divider("Alterar minha senha")

    with st.form("form_alterar_senha_propria"):
        col_a, col_b = st.columns(2)
        with col_a:
            senha_atual = st.text_input("🔒 Senha atual", type="password", placeholder="Digite sua senha atual")
        with col_b:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            st.caption("Confirme a senha atual para continuar.")

        col_c, col_d = st.columns(2)
        with col_c:
            nova_senha = st.text_input("🔑 Nova senha", type="password", placeholder=f"Mínimo {SENHA_MIN} caracteres")
        with col_d:
            confirmar_nova = st.text_input("🔑 Confirmar nova senha", type="password", placeholder="Repita a nova senha")

        alterar = st.form_submit_button("🔐 Alterar Senha", width='stretch', type="primary")

    if alterar:
        if not senha_atual:
            st.error("⚠️ Informe a senha atual.")
        elif len(nova_senha) < SENHA_MIN:
            st.error(f"⚠️ A nova senha deve ter ao menos {SENHA_MIN} caracteres.")
        elif nova_senha != confirmar_nova:
            st.error("⚠️ As senhas não coincidem.")
        else:
            db = get_db()
            try:
                ok, msg = alterar_senha_propria(db, usuario_id, senha_atual, nova_senha)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
            finally:
                db.close()
