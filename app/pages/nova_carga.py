# -*- coding: utf-8 -*-
"""
Página de cadastro de nova carga.
"""
import streamlit as st
from datetime import date
from app.database import get_db
from app.services import criar_carga
from app.components import (
    page_header, divider,
    notificar, exibir_notificacoes, redirecionar_apos_salvar,
)
from app.utils.helpers import validar_placa, formatar_placa, formatar_preco

TAMANHOS_CARGA = [
    "Selecione...",
    "Caminhão Toco",
    "Caminhão Truck",
    "Carreta Simples",
    "Carreta Eixo Extendido",
    "Bitrem",
    "Rodotrem",
    "Van / Utilitário",
    "Outro",
]


def mostrar_nova_carga() -> None:
    """Renderiza o formulário de cadastro de nova carga."""

    # Exibe notificações pendentes vindas de qualquer redirect anterior
    exibir_notificacoes()

    page_header(
        titulo="Nova Carga",
        subtitulo="Preencha os dados para registrar um novo agendamento de carga.",
        icone="📦"
    )

    if st.button("← Voltar ao Dashboard", key="btn_voltar_nova"):
        st.session_state["pagina_ativa"] = "dashboard"
        st.rerun()

    divider("Dados do Agendamento")

    with st.form("form_nova_carga", clear_on_submit=False):
        col1, col2 = st.columns([1, 2])
        with col1:
            data_carregamento = st.date_input(
                "📅 Data de Carregamento *",
                value=date.today(),
                min_value=date(2020, 1, 1),
                format="DD/MM/YYYY",
                help="Data prevista para o carregamento"
            )
        with col2:
            cliente = st.text_input(
                "🏢 Cliente *",
                placeholder="Nome do cliente ou empresa",
                max_chars=150,
            )

        col3, col4 = st.columns(2)
        with col3:
            carregador = st.text_input(
                "👷 Carregador *",
                placeholder="Nome do responsável pelo carregamento",
                max_chars=150,
            )
        with col4:
            tamanho = st.selectbox(
                "🚛 Tamanho do Veículo *",
                options=TAMANHOS_CARGA,
                help="Tipo/tamanho do caminhão"
            )

        divider("Dados do Transporte")

        col5, col6 = st.columns([2, 1])
        with col5:
            motorista = st.text_input(
                "👤 Motorista *",
                placeholder="Nome completo do motorista",
                max_chars=150,
            )
        with col6:
            placa = st.text_input(
                "🔤 Placa *",
                placeholder="Ex: ABC1234 ou ABC1D23",
                max_chars=8,
                help="Placa no formato antigo ou Mercosul"
            )

        col7, col8 = st.columns([2, 1])
        with col7:
            destino = st.text_input(
                "📍 Destino *",
                placeholder="Cidade/Estado de destino",
                max_chars=200,
            )
        with col8:
            preco = st.number_input(
                "💰 Preço (R$) *",
                min_value=0.0,
                max_value=9_999_999.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                help="Valor acordado pelo frete"
            )

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

        col_sub, col_limpar = st.columns([2, 1])
        with col_sub:
            submitted = st.form_submit_button(
                "✅ Registrar Carga",
                use_container_width=True,
                type="primary"
            )
        with col_limpar:
            st.form_submit_button("🔄 Limpar", use_container_width=True)

    # === PROCESSAMENTO ===
    if submitted:
        erros = _validar_formulario(
            data_carregamento, cliente, carregador, tamanho,
            motorista, placa, destino, preco
        )

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            dados = {
                "data_carregamento": data_carregamento,
                "cliente": cliente,
                "carregador": carregador,
                "tamanho": tamanho,
                "motorista": motorista,
                "placa": formatar_placa(placa),
                "destino": destino,
                "preco": preco,
            }

            db = get_db()
            try:
                carga = criar_carga(db, dados)
                if carga:
                    st.balloons()

                    # Notificação persistente — será exibida na tela de consulta
                    notificar(
                        mensagem=(
                            f"Carga <strong>#{carga.id}</strong> registrada com sucesso! "
                            f"Cliente: <strong>{carga.cliente}</strong> &nbsp;·&nbsp; "
                            f"Motorista: <strong>{carga.motorista}</strong> &nbsp;·&nbsp; "
                            f"Destino: <strong>{carga.destino}</strong> &nbsp;·&nbsp; "
                            f"Valor: <strong>{formatar_preco(carga.preco)}</strong>"
                        ),
                        tipo="sucesso",
                        icone="📦",
                    )

                    # Countdown visual + redirect automático para consulta
                    redirecionar_apos_salvar(
                        pagina_destino="consultar",
                        segundos=2,
                    )
                else:
                    st.error("❌ Erro ao registrar a carga. Tente novamente.")
            finally:
                db.close()

    st.markdown("""
    <div style="margin-top: 1.5rem; font-size: 0.78rem; color: #94A3B8; font-family: 'DM Sans', sans-serif;">
        * Campos obrigatórios
    </div>
    """, unsafe_allow_html=True)


def _validar_formulario(
    data_carregamento, cliente, carregador, tamanho,
    motorista, placa, destino, preco
) -> list:
    """Valida o formulário e retorna lista de erros."""
    erros = []
    if not cliente or not cliente.strip():
        erros.append("⚠️ O campo **Cliente** é obrigatório.")
    if not carregador or not carregador.strip():
        erros.append("⚠️ O campo **Carregador** é obrigatório.")
    if tamanho == "Selecione...":
        erros.append("⚠️ Selecione o **Tamanho do Veículo**.")
    if not motorista or not motorista.strip():
        erros.append("⚠️ O campo **Motorista** é obrigatório.")
    if not placa or not placa.strip():
        erros.append("⚠️ O campo **Placa** é obrigatório.")
    elif not validar_placa(placa):
        erros.append("⚠️ **Placa** inválida. Use o formato ABC1234 ou ABC1D23.")
    if not destino or not destino.strip():
        erros.append("⚠️ O campo **Destino** é obrigatório.")
    if preco <= 0:
        erros.append("⚠️ O **Preço** deve ser maior que zero.")
    return erros
