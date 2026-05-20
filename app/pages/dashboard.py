"""
Página do dashboard principal com métricas e navegação.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from app.database import get_db
from app.services import obter_metricas, listar_cargas, cargas_para_dataframe
from app.components import page_header, card_metrica
from app.utils.helpers import formatar_preco, status_cor


def mostrar_dashboard() -> None:
    """Renderiza o dashboard principal."""
    page_header(
        titulo="Dashboard",
        subtitulo=f"Bem-vindo, {st.session_state.get('usuario_nome', 'Usuário')}! Aqui está o resumo operacional.",
        icone="📊"
    )

    db = get_db()
    try:
        metricas = obter_metricas(db)
        cargas = listar_cargas(db)
    finally:
        db.close()

    if not metricas:
        st.warning("Não foi possível carregar as métricas.")
        return

    # === CARDS DE NAVEGAÇÃO RÁPIDA ===
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        border-radius: 16px;
        padding: 1.75rem 2rem;
        margin-bottom: 2rem;
        color: white;
    ">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700; margin-bottom: 0.3rem;">
            🚛 O que deseja fazer hoje?
        </div>
        <div style="font-size: 0.88rem; opacity: 0.8; font-family: 'DM Sans', sans-serif;">
            Gerencie suas cargas de forma rápida e eficiente
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div style="
            background: white;
            border: 2px solid #E2E8F0;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            height: 180px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        ">
            <div style="font-size: 3rem; margin-bottom: 0.75rem;">📦</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">Nova Carga</div>
            <div style="font-size: 0.82rem; color: #64748B; font-family: 'DM Sans', sans-serif;">Registrar novo agendamento</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("➕ Registrar Nova Carga", use_container_width=True, type="primary", key="btn_nova_carga"):
            st.session_state["pagina_ativa"] = "nova_carga"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="
            background: white;
            border: 2px solid #E2E8F0;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            height: 180px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        ">
            <div style="font-size: 3rem; margin-bottom: 0.75rem;">🔍</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">Consultar Cargas</div>
            <div style="font-size: 0.82rem; color: #64748B; font-family: 'DM Sans', sans-serif;">Pesquisar e filtrar registros</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Ver Todas as Cargas", use_container_width=True, key="btn_consultar"):
            st.session_state["pagina_ativa"] = "consultar"
            st.rerun()

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

    # === MÉTRICAS ===
    st.markdown("### 📈 Resumo Operacional")

    cols = st.columns(4, gap="medium")
    metricas_display = [
        ("Total de Cargas", str(metricas.get("total", 0)), "📦", "#1E40AF", "todos os registros"),
        ("Agendadas", str(metricas.get("agendadas", 0)), "📅", "#3B82F6", "aguardando início"),
        ("Em Trânsito", str(metricas.get("em_transito", 0)), "🚛", "#8B5CF6", "em movimento"),
        ("Entregues", str(metricas.get("entregues", 0)), "✅", "#10B981", "concluídas"),
    ]

    for i, (titulo, valor, icone, cor, sub) in enumerate(metricas_display):
        with cols[i]:
            st.markdown(card_metrica(titulo, valor, icone, cor, sub), unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    cols2 = st.columns(3, gap="medium")
    with cols2[0]:
        st.markdown(card_metrica(
            "Em Carregamento",
            str(metricas.get("em_carregamento", 0)),
            "🔄", "#F59E0B",
            "em processamento"
        ), unsafe_allow_html=True)
    with cols2[1]:
        st.markdown(card_metrica(
            "Canceladas",
            str(metricas.get("canceladas", 0)),
            "❌", "#EF4444",
            "não realizadas"
        ), unsafe_allow_html=True)
    with cols2[2]:
        st.markdown(card_metrica(
            "Receita Total",
            formatar_preco(metricas.get("receita_total", 0)),
            "💰", "#059669",
            "cargas entregues"
        ), unsafe_allow_html=True)

    # === GRÁFICO DE STATUS ===
    if cargas:
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("### 📊 Distribuição por Status")

        col_graf1, col_graf2 = st.columns([1, 1], gap="large")

        df = cargas_para_dataframe(cargas)

        with col_graf1:
            contagem_status = df["Status"].value_counts().reset_index()
            contagem_status.columns = ["Status", "Quantidade"]

            cores = [status_cor(s) for s in contagem_status["Status"]]

            fig = go.Figure(data=[go.Pie(
                labels=contagem_status["Status"],
                values=contagem_status["Quantidade"],
                hole=0.5,
                marker_colors=cores,
                textinfo="percent+value",
                textfont_size=12,
            )])
            fig.update_layout(
                title=dict(text="Status das Cargas", font_size=14, x=0.5),
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5),
                margin=dict(t=50, b=20, l=20, r=20),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="DM Sans",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_graf2:
            # Cargas por mês
            df_temp = df.copy()
            df_temp["Data_dt"] = pd.to_datetime(df_temp["Data"], format="%d/%m/%Y", errors="coerce")
            df_temp["Mês"] = df_temp["Data_dt"].dt.strftime("%b/%Y")
            por_mes = df_temp.groupby("Mês").size().reset_index(name="Cargas")

            if len(por_mes) > 0:
                fig2 = go.Figure(data=[go.Bar(
                    x=por_mes["Mês"],
                    y=por_mes["Cargas"],
                    marker_color="#3B82F6",
                    marker_line_color="#1E40AF",
                    marker_line_width=1,
                )])
                fig2.update_layout(
                    title=dict(text="Cargas por Período", font_size=14, x=0.5),
                    xaxis_title="",
                    yaxis_title="Quantidade",
                    margin=dict(t=50, b=20, l=20, r=20),
                    height=300,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_family="DM Sans",
                    yaxis=dict(gridcolor="#F1F5F9"),
                    xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                )
                st.plotly_chart(fig2, use_container_width=True)

        # === ÚLTIMAS CARGAS ===
        st.markdown("### 🕐 Últimas Cargas Registradas")
        ultimas = df.head(5)[["ID", "Data", "Cliente", "Destino", "Motorista", "Status"]]

        st.dataframe(
            ultimas,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Status": st.column_config.TextColumn("Status"),
            }
        )
    else:
        st.info("📭 Nenhuma carga cadastrada ainda. Registre a primeira carga!")
