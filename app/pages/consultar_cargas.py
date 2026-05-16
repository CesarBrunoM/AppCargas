"""
Página de consulta e listagem de cargas.
"""
import io
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.services import listar_cargas, cargas_para_dataframe, buscar_carga_por_id
from app.models import StatusCarga
from app.components import page_header, divider, status_badge, info_row
from app.utils.helpers import formatar_preco, formatar_data, status_emoji

# Itens por página
ITENS_POR_PAGINA = 10
STATUS_OPCOES = ["Todos"] + [s.value for s in StatusCarga]


def mostrar_consultar_cargas() -> None:
    """Renderiza a tela de consulta de cargas."""
    page_header(
        titulo="Consultar Cargas",
        subtitulo="Pesquise, filtre e gerencie todos os registros de carga.",
        icone="🔍"
    )

    if st.button("← Voltar ao Dashboard", key="btn_voltar_consultar"):
        st.session_state["pagina_ativa"] = "dashboard"
        st.rerun()

    # === VERIFICAR SE DEVE ABRIR DETALHES/EDIÇÃO ===
    if st.session_state.get("ver_detalhe_id"):
        _mostrar_detalhe(st.session_state["ver_detalhe_id"])
        return

    if st.session_state.get("editar_carga_id"):
        from app.pages.editar_carga import mostrar_editar_carga
        mostrar_editar_carga(st.session_state["editar_carga_id"])
        return

    divider("Filtros de Pesquisa")

    # === FILTROS ===
    col1, col2 = st.columns([2, 1])
    with col1:
        termo_busca = st.text_input(
            "🔎 Busca geral",
            placeholder="Cliente, motorista, placa, destino...",
            key="filtro_busca"
        )
    with col2:
        status_filtro = st.selectbox(
            "📌 Status",
            options=STATUS_OPCOES,
            key="filtro_status"
        )

    col3, col4, col5 = st.columns(3)
    with col3:
        cliente_filtro = st.text_input(
            "🏢 Cliente",
            placeholder="Filtrar por cliente",
            key="filtro_cliente"
        )
    with col4:
        motorista_filtro = st.text_input(
            "👤 Motorista",
            placeholder="Filtrar por motorista",
            key="filtro_motorista"
        )
    with col5:
        periodo = st.selectbox(
            "📅 Período",
            options=["Todos", "Hoje", "Últimos 7 dias", "Últimos 30 dias", "Personalizado"],
            key="filtro_periodo"
        )

    # Datas personalizadas
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

    if periodo == "Hoje":
        data_inicio = data_fim = date.today()
    elif periodo == "Últimos 7 dias":
        data_inicio = date.today() - timedelta(days=7)
        data_fim = date.today()
    elif periodo == "Últimos 30 dias":
        data_inicio = date.today() - timedelta(days=30)
        data_fim = date.today()
    elif periodo == "Personalizado":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_inicio = st.date_input("De:", value=date.today() - timedelta(days=30), format="DD/MM/YYYY")
        with col_d2:
            data_fim = st.date_input("Até:", value=date.today(), format="DD/MM/YYYY")

    # === BUSCAR CARGAS ===
    db = get_db()
    try:
        cargas = listar_cargas(
            db,
            cliente=cliente_filtro,
            motorista=motorista_filtro,
            status=status_filtro if status_filtro != "Todos" else "",
            data_inicio=data_inicio,
            data_fim=data_fim,
            termo_busca=termo_busca,
        )
    finally:
        db.close()

    df = cargas_para_dataframe(cargas)

    # === RESULTADOS ===
    divider(f"Resultados ({len(cargas)} carga{'s' if len(cargas) != 1 else ''})")

    if df.empty:
        st.info("📭 Nenhuma carga encontrada com os filtros aplicados.")
        return

    # Botão de exportação
    col_exp, col_info = st.columns([1, 3])
    with col_exp:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Cargas")
        st.download_button(
            label="📥 Exportar Excel",
            data=buffer.getvalue(),
            file_name=f"cargas_{date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch',
        )

    # === PAGINAÇÃO ===
    total_paginas = max(1, (len(df) + ITENS_POR_PAGINA - 1) // ITENS_POR_PAGINA)

    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = 1

    pagina = st.session_state["pagina_atual"]
    inicio = (pagina - 1) * ITENS_POR_PAGINA
    fim = inicio + ITENS_POR_PAGINA
    df_pagina = df.iloc[inicio:fim]

    # Tabela
    colunas_exibir = ["ID", "Data", "Cliente", "Carregador", "Motorista", "Placa", "Destino", "Preço", "Status"]
    df_exibir = df_pagina[colunas_exibir].copy()

    st.dataframe(
        df_exibir,
        width='stretch',
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small", format="%d"),
            "Preço": st.column_config.NumberColumn("Preço (R$)", format="R$ %.2f"),
            "Status": st.column_config.TextColumn("Status", width="medium"),
        }
    )

    # Controles de paginação
    col_prev, col_pag_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Anterior", disabled=(pagina <= 1), width='stretch'):
            st.session_state["pagina_atual"] -= 1
            st.rerun()
    with col_pag_info:
        st.markdown(
            f"<div style='text-align:center; padding: 0.5rem; color:#64748B; font-size:0.85rem;'>"
            f"Página {pagina} de {total_paginas} &nbsp;·&nbsp; {len(df)} registros</div>",
            unsafe_allow_html=True
        )
    with col_next:
        if st.button("Próxima ➡️", disabled=(pagina >= total_paginas), width='stretch'):
            st.session_state["pagina_atual"] += 1
            st.rerun()

    # === AÇÕES POR LINHA ===
    divider("Ações")
    st.markdown("**Selecione uma carga para visualizar ou editar:**")

    ids_disponiveis = df_pagina["ID"].tolist()
    col_id, col_ver, col_editar = st.columns([1, 1, 1])

    with col_id:
        id_selecionado = st.selectbox(
            "ID da Carga",
            options=ids_disponiveis,
            format_func=lambda x: f"Carga #{x}",
            key="sel_carga_id"
        )
    with col_ver:
        st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("👁️ Ver Detalhes", width='stretch', key="btn_ver"):
            st.session_state["ver_detalhe_id"] = id_selecionado
            st.rerun()
    with col_editar:
        st.markdown("<div style='margin-top: 1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("✏️ Editar Carga", width='stretch', type="primary", key="btn_editar"):
            st.session_state["editar_carga_id"] = id_selecionado
            st.rerun()


def _mostrar_detalhe(carga_id: int) -> None:
    """Exibe o painel de detalhes de uma carga."""
    db = get_db()
    try:
        carga = buscar_carga_por_id(db, carga_id)
    finally:
        db.close()

    if not carga:
        st.error("Carga não encontrada.")
        st.session_state.pop("ver_detalhe_id", None)
        return

    if st.button("← Voltar à lista", key="btn_voltar_detalhe"):
        st.session_state.pop("ver_detalhe_id", None)
        st.rerun()

    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    ">
        <div style="
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: #0F172A;
        ">📋 Detalhes da Carga #{carga.id}</div>
        {status_badge(carga.status)}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">📅 Dados do Agendamento</div>
        """, unsafe_allow_html=True)
        st.markdown(info_row("Data de Carregamento", formatar_data(carga.data_carregamento)), unsafe_allow_html=True)
        st.markdown(info_row("Cliente", carga.cliente), unsafe_allow_html=True)
        st.markdown(info_row("Carregador", carga.carregador), unsafe_allow_html=True)
        st.markdown(info_row("Tamanho do Veículo", carga.tamanho), unsafe_allow_html=True)
        st.markdown(info_row("Preço", formatar_preco(carga.preco)), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">🚛 Dados do Transporte</div>
        """, unsafe_allow_html=True)
        st.markdown(info_row("Motorista", carga.motorista), unsafe_allow_html=True)
        st.markdown(info_row("Placa", carga.placa), unsafe_allow_html=True)
        st.markdown(info_row("Destino", carga.destino), unsafe_allow_html=True)
        st.markdown(info_row("Status", f"{status_emoji(carga.status)} {carga.status}"), unsafe_allow_html=True)
        st.markdown(info_row("Cadastrado em", formatar_data(carga.criado_em.date()) if carga.criado_em else "-"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Dados operacionais
    if carga.quantidade_frutas or carga.peso_caminhao or carga.observacoes:
        st.markdown("""
        <div class="card">
            <div class="card-header">📊 Dados Operacionais</div>
        """, unsafe_allow_html=True)
        if carga.quantidade_frutas:
            st.markdown(info_row("Quantidade de Frutas", f"{carga.quantidade_frutas:,.0f} un"), unsafe_allow_html=True)
        if carga.peso_caminhao:
            st.markdown(info_row("Peso do Caminhão", f"{carga.peso_caminhao:,.0f} kg"), unsafe_allow_html=True)
        if carga.observacoes:
            st.markdown(info_row("Observações", carga.observacoes), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Botão editar
    if st.button("✏️ Editar esta Carga", type="primary", key="btn_editar_do_detalhe"):
        st.session_state.pop("ver_detalhe_id", None)
        st.session_state["editar_carga_id"] = carga_id
        st.rerun()
