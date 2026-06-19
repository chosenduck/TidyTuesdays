import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import carregar_conexao
from utils.data_transformer import carregar_gold, carregar_silver
from utils.helpers import calcular_score
# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.title("🎮 Do Console para o Cinema 🎬")
st.markdown("""Explorando o sucesso das adaptações de videogames no cinema • TidyTuesday de 09 de Junho de 2026""")

st.divider()

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.block-container { padding-top: 2rem; }
hr.section-divider {
    border: none;
    border-top: 1px solid #1e2c35;
    margin: 2rem 0;
}
[data-testid="stImage"] { margin-bottom: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# DADOS (carregados uma vez, fora das abas)
# ---------------------------------------------------------------------------
con = carregar_conexao()
gold = carregar_gold(con)
silver = carregar_silver(con)

df = silver.copy()
df["score_medio"] = df.apply(
    lambda r: calcular_score(
        r["rotten_tomatoes"],
        r["metacritic"]
    ),
    axis=1
)

df = df[df["score_medio"].notna()].copy()
df = df.sort_values("score_medio", ascending=True)

# -----------------------------------------------------------------------------
# HALL DA INFÂMIA
# -----------------------------------------------------------------------------

st.subheader("🏆 Hall da Infâmia")

top5 = df.head(5)

cols = st.columns(5)

for i, (_, row) in enumerate(top5.iterrows()):

    with cols[i]:

        if pd.notna(row.get("poster_url")):
            st.image(row["poster_url"])
        else:
            st.markdown(
                """
                <div style="
                    height:220px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    border-radius:10px;
                    background:#f3f3f3;
                    font-size:50px;
                ">
                🎮
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            f"""
            **#{i+1} — {row['title']}**

            {int(row['release_year']) if pd.notna(row['release_year']) else '—'}
            """
        )

        st.caption(
            f"🍅 Rotten Tomatoes: {int(row['rotten_tomatoes']) if pd.notna(row['rotten_tomatoes']) else '—'}%"
        )

        st.caption(
            f"🎯 Metacritic: {int(row['metacritic']) if pd.notna(row['metacritic']) else '—'}"
        )

st.divider()