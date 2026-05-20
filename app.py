import streamlit as st
import seaborn as sns

from utils.data_loader import carregar_dados
from utils.data_processor import preparar_hs, para_bilhoes
from utils.constants import FMT_BI, CORES

from utils.graficos import grafico_hs_linha


# ─── Configuração visual ─────────────────────────────
sns.set_theme(style="whitegrid")

st.title("🌍 Global Health Spending")
st.write("O Brasil gasta bem em saúde, ou apenas gasta muito?")

# ─── 1. Carregar dados ───────────────────────────────
health_spending, financing_schemes, spending_purpose = carregar_dados()

# ─── 2. Preparar dados ──────────────────────────────
df_hs = preparar_hs(health_spending, ["Brazil"])

df_hs_abs = (
    df_hs[df_hs["indicator_code"] == "gghed_usd2023"]
    .pipe(para_bilhoes, ["value"])
    .rename(columns={"value": "value_bi"})
)

# ─── 4. Visualizar ──────────────────────────────────
fig = grafico_hs_linha(
    df=df_hs_abs,
    col_y="value_bi",
    titulo="O Brasil hoje gasta mais que o dobro com saúde pública do que há 20 anos",
    cor=CORES["governo"],
    fmt=FMT_BI,
)

st.plotly_chart(fig, use_container_width=True)