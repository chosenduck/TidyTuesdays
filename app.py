import streamlit as st

from utils.data_loader import carregar_conexao
from utils.data_transformer import executar_transformacoes

from utils.data_viz import gasto_total_brasil, plot_gasto_publico_brasil, plot_evolucao_pub_x_priv, plot_perfil_financiamento_brasil, plot_gasto_pc_brics

# CARREGAR DADOS
con = carregar_conexao()
executar_transformacoes(con)

# st.subheader("Silver")
#silver = con.sql("""
#    SELECT *
#    FROM silver_financing_schemes
#    LIMIT 20
#""").df()
#st.dataframe(silver)

#st.subheader("Gold")
#gold = con.sql("""
#    SELECT *
#    FROM silver_health_spending
#    WHERE country_name == 'Brazil'
#""").df()
#st.dataframe(gold)

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="O Brasil gasta bem em saúde?",
    page_icon="🩺",
    layout="wide"
)

# HEADER
st.title("🌍 O Brasil gasta bem em saúde?")
st.markdown("_v.1.0_")
st.write("""Análise do Global Health Expenditure Database (WHO) — TidyTuesday de 21 Abril 2026""")
st.divider()

# SEÇÃO 1
st.header("Quanto gastamos?")

# Cards
m1, m2, m3 = st.columns(3)
m1.metric(label="Gasto total (2023)", value="—", delta="—")
m2.metric(label="Gasto per capita",   value="—", delta="—")
m3.metric(label="% do PIB",           value="—", delta="—")
st.divider()

# Gráfico 1
fig = gasto_total_brasil(con)
with st.container(border=True):
    st.plotly_chart(fig, width='stretch')

# Gráfico 2
fig2 = plot_gasto_publico_brasil(con)
with st.container(border=True):
    st.plotly_chart(fig2, width='stretch')

# Gráfico 3
fig3 = plot_evolucao_pub_x_priv(con)
with st.container(border=True):
    st.plotly_chart(fig3, width='stretch')

st.divider()

# SEÇÃO 2
st.header("Como financiamos?")

fig4 = plot_perfil_financiamento_brasil(con)
with st.container(border=True):
    st.plotly_chart(fig4, width='stretch')

fig5 = plot_gasto_pc_brics(con)
with st.container(border=True):
    st.plotly_chart(fig5, width='stretch')

# SEÇÃO 3
st.header("Em que gastamos?")

# FOOTER