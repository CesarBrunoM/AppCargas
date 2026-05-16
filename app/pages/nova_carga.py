"""
Página de cadastro de nova carga.
"""
import streamlit as st
from datetime import date
from app.database import get_db
from app.services import criar_carga
from app.components import page_header, divider
from app.utils.helpers import validar_placa, formatar_placa

# Opções de tamanho de carga
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
        # === LINHA 1: Data e Cliente ===
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

        # === LINHA 2: Carregador e Tamanho ===
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

        # === LINHA 3: Motorista e Placa ===
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

        # === LINHA 4: Destino e Preço ===
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
            st.form_submit_button(
                "🔄 Limpar",
                use_container_width=True,
            )

    # === PROCESSAMENTO DO FORMULÁRIO ===
    if submitted:
        erros = _validar_formulario(
            data_carregamento, cliente, carregador, tamanho,
            motorista, placa, destino, preco
        )

        if erros:
            for erro in erros:
                st.error(erro)
        else:
            placa_formatada = formatar_placa(placa)
            dados = {
                "data_carregamento": data_carregamento,
                "cliente": cliente,
                "carregador": carregador,
                "tamanho": tamanho,
                "motorista": motorista,
                "placa": placa_formatada,
                "destino": destino,
                "preco": preco,
            }

            db = get_db()
            try:
                carga = criar_carga(db, dados)
                if carga:
                    st.success(f"✅ Carga registrada com sucesso! **ID: #{carga.id}**")
                    st.balloons()

                    # Mostrar resumo
                    st.markdown("""
                    <div style="
                        background: #F0FDF4;
                        border: 1px solid #86EFAC;
                        border-radius: 12px;
                        padding: 1.25rem;
                        margin-top: 1rem;
                    ">
                        <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #065F46; margin-bottom: 0.5rem;">
                            📋 Carga Registrada
                        </div>
                    """, unsafe_allow_html=True)

                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1:
                        st.metric("ID", f"#{carga.id}")
                        st.metric("Cliente", carga.cliente)
                    with col_r2:
                        st.metric("Motorista", carga.motorista)
                        st.metric("Placa", carga.placa)
                    with col_r3:
                        st.metric("Destino", carga.destino)
                        st.metric("Status", carga.status)

                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("❌ Erro ao registrar a carga. Tente novamente.")
            finally:
                db.close()

    # Dica de campos obrigatórios
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
