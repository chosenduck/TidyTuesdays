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
    plot_gasto_pc_comparativo,
    plot_perfil_financiamento,
    plot_prevencao_vs_reacao
)

from utils.constants import COR_RAZAO

# CARREGAR DADOS
con = carregar_conexao()
executar_transformacoes(con)

# CONFIGURAÇÃO DA PÁGINA
# Carregando style.css
def carregar_estilos():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

carregar_estilos()

# Configurando Aba
st.set_page_config(
    page_title="O Brasil gasta bem em saúde?",
    page_icon="🩺",
    layout="wide"
)

# HEADER
st.title("O Brasil gasta bem em saúde?")
st.markdown( """ Análise do Global Health Expenditure Database (WHO) — TidyTuesday de 21 Abril de 2026 """ )
st.caption("por João Victor Fernandes") 
st.caption("v1.3")

st.markdown("""
[GitHub](...) • [LinkedIn](...)
""")

st.divider()

# SEÇÃO 1
st.header("Quanto o Brasil gasta em saúde hoje*?")

c1, c2, c3, c4 = st.columns(4)

# Card 1
m = metrica_gasto_total(con)
delta_total = (m["valor_atual"] / m["valor_2000"] - 1) * 100

with c1.container(border=True):
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    col_val, col_rank = st.columns([3, 1])

    with col_val: 
        st.metric( 
            label="Gasto total em saúde", 
            value=f"US$ {m['valor_atual']:.0f} bi", 
            delta=f"+{delta_total:.0f}% desde 2000"
        )

    with col_rank: 
        st.markdown( 
            f""" 
            <div class="rank-box"> 
                <div class="rank-title">BRICS</div> 
                <div class="rank-value">{int(m['rank_brics'])}º</div>
                <div class="rank-title secondary">Sistemas Universais</div> 
                <div class="rank-value">{int(m['rank_universal'])}º</div> 
            </div> 
            """, 
            unsafe_allow_html=True 
        ) 
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

# Card 2   
m2 = metrica_gasto_per_capita(con)
delta_total2 = (m2["valor_atual"] / m2["valor_2000"] - 1) * 100

with c2.container(border=True): 
    st.markdown('<div class="metric-card">', unsafe_allow_html=True) 
    
    col_val, col_rank = st.columns([3, 1]) 
    
    with col_val: 
        st.metric( 
            label="Gasto per capita", 
            value=f"US$ {m2['valor_atual']:,.0f}".replace(",", "."), 
            delta=f"+{delta_total2:.0f}% desde 2000", 
        ) 
    
    with col_rank: 
        st.markdown( 
            f""" 
            <div class="rank-box"> 
                <div class="rank-title">BRICS</div> 
                <div class="rank-value">{int(m2['rank_brics'])}º</div>
                <div class="rank-title secondary">Sistemas Universais</div> 
                <div class="rank-value">{int(m2['rank_universal'])}º</div> 
            </div> 
            """, 
            unsafe_allow_html=True 
        ) 
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

# Card 3
m3 = metrica_participacao_publica(con)
delta_total3 = (m3["valor_atual"] - m3["valor_2000"])

with c3.container(border=True): 
    st.markdown('<div class="metric-card">', unsafe_allow_html=True) 
    
    col_val, col_rank = st.columns([3, 1]) 
    
    with col_val: 
        st.metric( 
            label="Participação pública", 
            value=f"{m3['valor_atual']:.0f}%", 
            delta=f"+{delta_total3:.0f} p.p. desde 2000", 
        ) 
    
    with col_rank: 
        st.markdown( 
            f""" 
            <div class="rank-box"> 
                <div class="rank-title">BRICS</div> 
                <div class="rank-value">{int(m3['rank_brics'])}º</div>
                <div class="rank-title secondary">Sistemas Universais</div> 
                <div class="rank-value">{int(m3['rank_universal'])}º</div> 
            </div> 
            """, 
            unsafe_allow_html=True 
        ) 
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

# Card 4
m4 = metrica_desembolso_direto(con) 
delta_total4 = (m4["valor_atual"] - m4["valor_2000"]) 

with c4.container(border=True): 
    st.markdown('<div class="metric-card">', unsafe_allow_html=True) 
    col_val, col_rank = st.columns([3, 1]) 
    with col_val: 
        st.metric( 
            label="Desembolso Direto (OOP)", 
            value=f"{m4['valor_atual']:.0f}%", 
            delta=f"{delta_total4:.0f} p.p. desde 2000", 
            delta_color="inverse", 
        ) 
    with col_rank: 
        st.markdown( 
            f""" 
            <div class="rank-box"> 
                <div class="rank-title">BRICS</div> 
                <div class="rank-value"> {int(m4['rank_oop_brics'])}º </div> 
                <div class="rank-title secondary"> Sistemas Universais </div> 
                <div class="rank-value"> {int(m4['rank__oop_universal'])}º </div> 
            </div> 
            """, 
            unsafe_allow_html=True 
        ) 
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

# Card Narrativo
m5 = metrica_razao_reativo_preventivo(con) 

with st.container(border=True):

    st.markdown(
        f"""
        <div class="highlight-inline">
            <span class="highlight-text">Para cada US$ 1 investido em prevenção, o Brasil gasta:</span>
            <span class="highlight-value" style="color:{COR_RAZAO};">US$ {m5['razao']:.0f}</span>
            <span class="highlight-text">em cuidados reativos.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")

st.caption( 
    "*Indicadores referentes ao último ano disponível " 
    "da série histórica (2000–2023)." 
    ) 

st.caption(
    "Valores em US$ constantes de 2023."
    ) 

st.divider()

# SEÇÃO 2
st.header("Como o financiamento da saúde mudou nas últimas décadas?")

c1, c2 = st.columns(2)

fig = plot_gasto_total_brasil(con) 
with c1.container(border=True): 
    st.plotly_chart(fig, width='stretch') 
    
fig2 = plot_evolucao_pub_x_priv(con) 
with c2.container(border=True): 
    st.plotly_chart(fig2, width='stretch')

fig3 = plot_gasto_pct_brasil(con) 
with st.container(border=True): 
    st.plotly_chart(fig3, width='stretch')

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

grupo_gasto = st.radio(
    "Grupo de comparação — gasto per capita",
    ["BRICS", "Sistemas Universais"],
    horizontal=True,
    key="grupo_gasto_pc"
)

grupo_fin = st.radio(
    "Grupo de comparação — perfil de financiamento",
    ["BRICS", "Sistemas Universais"],
    horizontal=True,
    key="grupo_financiamento"
)


c1, c2 = st.columns(2)

fig_gasto  = plot_gasto_pc_comparativo(
    con,
    grupo="BRICS" if grupo_gasto == "BRICS" else "Sistemas Universais"
)

with c1.container(border=True):
    st.plotly_chart(
        fig_gasto,
        width="stretch"
    )

st.markdown("")




fig_fin = plot_perfil_financiamento(
    con,
    grupo=(
        "brics"
        if grupo_fin == "BRICS"
        else "universais"
    )
)

with c2.container(border=True):
    st.plotly_chart(
        fig_fin,
        width="stretch"
    )

st.markdown("")


fig_prev = plot_prevencao_vs_reacao(con)

with st.container(border=True):
    st.plotly_chart(
        fig_prev,
        width="stretch"
    )