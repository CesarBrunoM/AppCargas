# -*- coding: utf-8 -*-
"""
Página de edição de carga existente.
"""
import streamlit as st
from datetime import date
from app.database import get_db
from app.services import buscar_carga_por_id, atualizar_carga
from app.models import StatusCarga
from app.components import (
    page_header, divider, status_badge,
    notificar, exibir_notificacoes, redirecionar_apos_salvar,
)
from app.utils.helpers import (
    formatar_preco, formatar_data, validar_placa, formatar_placa, status_cor,
)

STATUS_OPCOES = [s.value for s in StatusCarga]

TAMANHOS_CARGA = [
    "Caminhão Toco",
    "Caminhão Truck",
    "Carreta Simples",
    "Carreta Eixo Extendido",
    "Bitrem",
    "Rodotrem",
    "Van / Utilitário",
    "Outro",
]


def mostrar_editar_carga(carga_id: int) -> None:
    """Renderiza o formulário de edição de carga."""

    # Exibe notificações pendentes
    exibir_notificacoes()

    db = get_db()
    try:
        carga = buscar_carga_por_id(db, carga_id)
    finally:
        db.close()

    if not carga:
        st.error(f"❌ Carga #{carga_id} não encontrada.")
        if st.button("← Voltar"):
            st.session_state.pop("editar_carga_id", None)
            st.rerun()
        return

    # Header com status atual
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        page_header(
            titulo=f"Editar Carga #{carga.id}",
            subtitulo="Atualize os dados operacionais e o status da carga.",
            icone="✏️"
        )
    with col_badge:
        st.markdown(
            f"<div style='margin-top: 1.5rem;'>{status_badge(carga.status)}</div>",
            unsafe_allow_html=True
        )

    if st.button("← Voltar à lista", key="btn_voltar_editar"):
        st.session_state.pop("editar_carga_id", None)
        st.rerun()

    aba_operacional, aba_agendamento = st.tabs(["📊 Dados Operacionais", "📋 Dados do Agendamento"])

    # ─── ABA 1: DADOS OPERACIONAIS ───────────────────────────────────────────
    with aba_operacional:
        divider("Atualizar Status e Dados Operacionais")

        with st.form("form_operacional"):
            col1, col2 = st.columns(2)

            with col1:
                idx_status = STATUS_OPCOES.index(carga.status) if carga.status in STATUS_OPCOES else 0
                novo_status = st.selectbox(
                    "📌 Status *",
                    options=STATUS_OPCOES,
                    index=idx_status,
                    help="Atualize o status operacional da carga"
                )
                cor = status_cor(novo_status)
                st.markdown(f"""
                <div style="
                    display: inline-flex; align-items: center; gap: 6px;
                    padding: 6px 12px; background: {cor}20;
                    border: 1px solid {cor}60; border-radius: 8px;
                    font-size: 0.82rem; font-weight: 600; color: {cor}; margin-top: 4px;
                ">Novo status: {novo_status}</div>
                """, unsafe_allow_html=True)

            with col2:
                quantidade_frutas = st.number_input(
                    "🍎 Quantidade de Frutas (unidades)",
                    min_value=0.0,
                    value=float(carga.quantidade_frutas) if carga.quantidade_frutas else 0.0,
                    step=100.0,
                    format="%.0f",
                    help="Quantidade total de frutas carregadas"
                )

            peso_caminhao = st.number_input(
                "⚖️ Peso do Caminhão (kg)",
                min_value=0.0,
                value=float(carga.peso_caminhao) if carga.peso_caminhao else 0.0,
                step=100.0,
                format="%.0f",
                help="Peso total do caminhão carregado"
            )

            observacoes = st.text_area(
                "📝 Observações",
                value=carga.observacoes or "",
                placeholder="Adicione observações relevantes sobre a carga...",
                max_chars=1000,
                height=100,
            )

            submitted_op = st.form_submit_button(
                "💾 Salvar Alterações Operacionais",
                width='stretch',
                type="primary"
            )

        if submitted_op:
            dados = {
                "status": novo_status,
                "quantidade_frutas": quantidade_frutas if quantidade_frutas > 0 else None,
                "peso_caminhao": peso_caminhao if peso_caminhao > 0 else None,
                "observacoes": observacoes.strip() if observacoes else None,
            }
            db = get_db()
            try:
                atualizado = atualizar_carga(db, carga_id, dados)
                if atualizado:
                    notificar(
                        mensagem=(
                            f"Dados operacionais da Carga <strong>#{carga_id}</strong> atualizados com sucesso! "
                            f"Novo status: <strong>{novo_status}</strong>."
                        ),
                        tipo="sucesso",
                        icone="📊",
                    )
                    redirecionar_apos_salvar(
                        pagina_destino="consultar",
                        segundos=2,
                        limpar_keys=["editar_carga_id"],
                    )
                else:
                    st.error("❌ Erro ao atualizar. Tente novamente.")
            finally:
                db.close()

    # ─── ABA 2: DADOS DO AGENDAMENTO ─────────────────────────────────────────
    with aba_agendamento:
        divider("Editar Dados do Agendamento")

        idx_tamanho = TAMANHOS_CARGA.index(carga.tamanho) if carga.tamanho in TAMANHOS_CARGA else 0

        with st.form("form_agendamento"):
            col1, col2 = st.columns([1, 2])
            with col1:
                nova_data = st.date_input(
                    "📅 Data de Carregamento",
                    value=carga.data_carregamento or date.today(),
                    format="DD/MM/YYYY",
                )
            with col2:
                novo_cliente = st.text_input("🏢 Cliente", value=carga.cliente, max_chars=150)

            col3, col4 = st.columns(2)
            with col3:
                novo_carregador = st.text_input("👷 Carregador", value=carga.carregador, max_chars=150)
            with col4:
                novo_tamanho = st.selectbox("🚛 Tamanho", options=TAMANHOS_CARGA, index=idx_tamanho)

            col5, col6 = st.columns([2, 1])
            with col5:
                novo_motorista = st.text_input("👤 Motorista", value=carga.motorista, max_chars=150)
            with col6:
                nova_placa = st.text_input("🔤 Placa", value=carga.placa, max_chars=8)

            col7, col8 = st.columns([2, 1])
            with col7:
                novo_destino = st.text_input("📍 Destino", value=carga.destino, max_chars=200)
            with col8:
                novo_preco = st.number_input(
                    "💰 Preço (R$)",
                    value=float(carga.preco),
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                )

            submitted_ag = st.form_submit_button(
                "💾 Salvar Dados do Agendamento",
                width='stretch',
                type="primary"
            )

        if submitted_ag:
            erros = []
            if not novo_cliente.strip():
                erros.append("⚠️ **Cliente** é obrigatório.")
            if not novo_motorista.strip():
                erros.append("⚠️ **Motorista** é obrigatório.")
            if not nova_placa.strip():
                erros.append("⚠️ **Placa** é obrigatória.")
            elif not validar_placa(nova_placa):
                erros.append("⚠️ **Placa** inválida.")
            if not novo_destino.strip():
                erros.append("⚠️ **Destino** é obrigatório.")
            if novo_preco <= 0:
                erros.append("⚠️ **Preço** deve ser maior que zero.")

            if erros:
                for e in erros:
                    st.error(e)
            else:
                dados_ag = {
                    "data_carregamento": nova_data,
                    "cliente": novo_cliente.strip(),
                    "carregador": novo_carregador.strip(),
                    "tamanho": novo_tamanho,
                    "motorista": novo_motorista.strip(),
                    "placa": formatar_placa(nova_placa),
                    "destino": novo_destino.strip(),
                    "preco": novo_preco,
                }
                db = get_db()
                try:
                    atualizado = atualizar_carga(db, carga_id, dados_ag)
                    if atualizado:
                        notificar(
                            mensagem=(
                                f"Agendamento da Carga <strong>#{carga_id}</strong> atualizado com sucesso! "
                                f"Cliente: <strong>{novo_cliente.strip()}</strong> &nbsp;·&nbsp; "
                                f"Destino: <strong>{novo_destino.strip()}</strong> &nbsp;·&nbsp; "
                                f"Valor: <strong>{formatar_preco(novo_preco)}</strong>."
                            ),
                            tipo="sucesso",
                            icone="📋",
                        )
                        redirecionar_apos_salvar(
                            pagina_destino="consultar",
                            segundos=2,
                            limpar_keys=["editar_carga_id"],
                        )
                    else:
                        st.error("❌ Erro ao atualizar. Tente novamente.")
                finally:
                    db.close()

    # Resumo atual colapsável
    with st.expander("📄 Ver dados atuais da carga", expanded=False):
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric("Cliente", carga.cliente)
            st.metric("Data", formatar_data(carga.data_carregamento))
        with col_r2:
            st.metric("Motorista", carga.motorista)
            st.metric("Placa", carga.placa)
        with col_r3:
            st.metric("Destino", carga.destino)
            st.metric("Preço", formatar_preco(carga.preco))
