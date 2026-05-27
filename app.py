import streamlit as st

from utils.data_loader import carregar_conexao
from utils.data_transformer import executar_transformacoes

from utils.data_viz import (
    metrica_gasto_total,
    metrica_gasto_per_capita,
    metrica_participacao_publica,
    metrica_desembolso_direto,
    metrica_razao_reativo_preventivo,
    plot_gasto_total_brasil,
    plot_evolucao_pub_x_priv,
    plot_gasto_pct_brasil,
    plot_evolucao_financiamento_brasil,
    plot_evolucao_componentes,
    plot_razao,
    plot_gasto_pc_brics    
)

from utils.constants import COR_RAZAO

# CARREGAR DADOS
con = carregar_conexao()
executar_transformacoes(con)

# CONFIGURAÇÃO DA PÁGINA
# Configurando Aba
st.set_page_config(
    page_title="O Brasil gasta bem em saúde?",
    page_icon="🩺",
    layout="wide"
)

## Alinhando Cards
st.markdown("""
    <style>
        /* Centraliza conteúdo dentro dos cards */
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 150px;
        }

        /* Garante que todos os cards tenham a mesma altura */
        [data-testid="stVerticalBlockBorderWrapper"] {
            height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# HEADER
st.title("O Brasil gasta bem em saúde?")
st.write("""Análise do Global Health Expenditure Database (WHO) — TidyTuesday de 21 Abril de 2026""")
st.markdown("_por João Victor Fernandes_")
st.markdown("_v.1.2_")
st.divider()

# SEÇÃO 1
st.header("Quanto o Brasil gasta em saúde hoje?")

c1, c2, c3, c4, c5 = st.columns(5)

m = metrica_gasto_total(con)
delta_total = (m["valor_atual"] / m["valor_2000"] - 1) * 100
with c1.container(border=True):
    col_val, col_rank = st.columns([2.5, 1], vertical_alignment="center")

    col_val.metric(
        label="Gasto total em saúde",
        value=f"US$ {m['valor_atual']:.0f}bi",
        delta=f"+{delta_total:.0f}% desde 2000",
    )

    col_rank.caption("BRICS")
    col_rank.markdown(f"**{int(m['rank_brics'])}º**")
    col_rank.caption("Sistemas Universais")
    col_rank.markdown(f"**{int(m['rank_universal'])}º**")
    
m2 = metrica_gasto_per_capita(con)
delta_total2 = (m2["valor_atual"] / m2["valor_2000"] - 1) * 100
with c2.container(border=True):
    col_val, col_rank = st.columns([2, 1], vertical_alignment="center")

    col_val.metric(
        label="Gasto per capita", 
        value=f"US$ {m2['valor_atual']:,.0f}".replace(",", "."), 
        delta=f"+{delta_total2:.0f}% desde 2000",
        )
    col_rank.caption("BRICS")
    col_rank.markdown(f"**{int(m2['rank_brics'])}º**")
    col_rank.caption("Sistemas Universais")
    col_rank.markdown(f"**{int(m2['rank_universal'])}º**")

m3 = metrica_participacao_publica(con)
delta_total3 = (m3["valor_atual"] - m3["valor_2000"])
with c3.container(border=True):
    col_val, col_rank = st.columns([2, 1], vertical_alignment="center")

    col_val.metric(
        label="Participação pública", 
        value=f"{m3['valor_atual']:.0f}%" ,
        delta=f"+{delta_total3:.0f} p.p. desde 2000",
        )

    col_rank.caption("BRICS")
    col_rank.markdown(f"**{int(m3['rank_brics'])}º**")
    col_rank.caption("Sistemas Universais")
    col_rank.markdown(f"**{int(m3['rank_universal'])}º**")

m4 = metrica_desembolso_direto(con)
delta_total4 = (m4["valor_atual"] - m4["valor_2000"])
with c4.container(border=True):
    col_val, col_rank = st.columns([2, 1], vertical_alignment="center")
    
    col_val.metric(
        label="Desembolso Direto (OOP)", 
        value=f"{m4['valor_atual']:.0f}%" ,
        delta=f"{delta_total4:.0f} p.p. desde 2000",
        delta_color="inverse",
        )

    col_rank.caption("BRICS")
    col_rank.markdown(f"**{int(m4['rank_oop_brics'])}º**")
    col_rank.caption("Sistemas Universais")
    col_rank.markdown(f"**{int(m4['rank__oop_universal'])}º**")

m5 = metrica_razao_reativo_preventivo(con)
with c5.container(border=True):

    st.markdown(
        """
        <h6 style="margin-bottom:0;">
            Para cada US$ 1 investido em prevenção,
            <br>
            o Brasil gasta
        </h6>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <h1 style="
            color:{COR_RAZAO};
            margin-bottom:0;
        ">
            US$ {m5['razao']:.0f}
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    em cuidados reativos.
    """)
    
st.markdown("_Indicadores referentes ao último ano disponível da série histórica (2000–2023)._")
st.markdown("_Valores em US$ constantes de 2023._")

st.divider()

# SEÇÃO 2
st.header("Como o financiamento da saúde mudou nas últimas décadas?")

c1, c2, c3 = st.columns(3)

# Gráfico 1
fig = plot_gasto_total_brasil(con)
with c1.container(border=True):
    st.plotly_chart(fig, width='stretch')

# Gráfico 2
fig2 = plot_evolucao_pub_x_priv(con)
with c2.container(border=True):
    st.plotly_chart(fig2, width='stretch')

# Gráfico 3
fig3 = plot_gasto_pct_brasil(con)
with c3.container(border=True):
    st.plotly_chart(fig3, width='stretch')

# Gráfico 4
fig4 = plot_evolucao_financiamento_brasil(con)
with st.container(border=True):
    st.plotly_chart(fig4, width='stretch')

st.divider()

# SEÇÃO 3
st.header("Gastamos para tratar ou para prevenir?")

c1, c2 = st.columns(2)

fig5 = plot_evolucao_componentes(con)
with c1.container(border=True):
    st.plotly_chart(fig5, width='stretch')

fig6 = plot_razao(con)
with c2.container(border=True):
    st.plotly_chart(fig6, width='stretch')

st.divider()

# SEÇÃO 4
st.header("O Brasil gasta bem comparado a quem?")

# Gráfico
#fig5 = plot_gasto_pc_brics(con)
#with st.container(border=True):
#    st.plotly_chart(fig5, width='stretch')

# FOOTER
st.subheader("Teste")
teste = con.sql("""
        SELECT *
        
        FROM gold_hc1_hc6_ratio
        
        WHERE country_name = 'Brazil'
                
        ORDER BY year
""").df()
st.dataframe(teste)