import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import carregar_conexao
from utils.data_transformer import carregar_gold, carregar_silver
from utils.constants import Colors, DECADAS
from utils.helpers import _fmt_bilheteria, _clean_url, kpi_card, kpi_record_card, decada_de

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.title("🎮 Do Console para o Cinema 🎬")
st.markdown( """Explorando o sucesso das adaptações de videogames no cinema • TidyTuesday de 09 de Junho de 2026""" )

st.divider()

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
.block-container { padding-top: 2rem; }

.kpi-card {
    background: #1a2228;
    border-radius: 6px;
    padding: 1rem 1.1rem 0.85rem;
    border-bottom: 3px solid var(--kpi-accent, #00e054);
    height: 100%;
}
.kpi-card .kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8a9bb0;
    margin-bottom: 0.35rem;
}
.kpi-card .kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}
.kpi-card .kpi-caption {
    font-size: 0.72rem;
    color: #8a9bb0;
    margin-top: 0.3rem;
}

.kpi-green  { --kpi-accent: #00e054; }
.kpi-orange { --kpi-accent: #ff8000; }
.kpi-blue   { --kpi-accent: #40bcf4; }
.kpi-white  { --kpi-accent: #ffffff; }
.kpi-red    { --kpi-accent: #e05454; }

/* card de recorde: remove padding interno p/ dar espaço ao poster */
.kpi-record {
    background: #1a2228;
    border-radius: 6px;
    border-bottom: 3px solid var(--kpi-accent, #00e054);
    overflow: hidden;
    height: 100%;
}
.kpi-record-text {
    padding: 0.75rem 1rem 0.85rem;
}
.kpi-record-text .kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8a9bb0;
    margin-bottom: 0.35rem;
}
.kpi-record-text .kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}
.kpi-record-text .kpi-caption {
    font-size: 0.72rem;
    color: #8a9bb0;
    margin-top: 0.3rem;
}

hr.section-divider {
    border: none;
    border-top: 1px solid #1e2c35;
    margin: 2rem 0;
}

/* remove margem extra que o st.image adiciona */
[data-testid="stImage"] { margin-bottom: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# DADOS
# ---------------------------------------------------------------------------

con = carregar_conexao()
gold = carregar_gold(con)
silver = carregar_silver(con)

kpis: dict = gold["kpis"]
df_tempo   = gold["evolucao_temporal"]   # colunas: ano, total_filmes, bilheteria_total, media_rt

# ---------------------------------------------------------------------------
# SEÇÃO 1: KPIs
# ---------------------------------------------------------------------------

st.subheader("Panorama Geral")

#  Linha 1: números macro
col1, col2, col3, col4, col5 = st.columns(5)

col1.markdown(kpi_card(
    "Adaptações",
    str(kpis["total_filmes"]),
    accent="green",
), unsafe_allow_html=True)

col2.markdown(kpi_card(
    "Distribuidoras",
    str(kpis["total_publishers"]),
    accent="blue",
), unsafe_allow_html=True)

col3.markdown(kpi_card(
    "Bilheteria acumulada",
    _fmt_bilheteria(kpis["bilheteria_total_usd"]),
    accent="orange",
), unsafe_allow_html=True)

col4.markdown(kpi_card(
    "Média Rotten Tomatoes",
    f"{kpis['media_rotten_tomatoes']}%" if kpis["media_rotten_tomatoes"] is not None else "—",
    accent="green",
), unsafe_allow_html=True)

col5.markdown(kpi_card(
    "Média Metacritic",
    str(kpis["media_metacritic"]) if kpis["media_metacritic"] is not None else "—",
    accent="blue",
), unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# Linha 2: recordes (largura total, com pôster via st.image)
col_a, col_b, col_c = st.columns(3)

maior_box = kpis.get("maior_bilheteria", {})
kpi_record_card(
    col_a,
    label="Maior bilheteria",
    value=_fmt_bilheteria(maior_box.get("worldwide_box_office_usd")),
    title=maior_box.get("title", ""),
    year=str(int(maior_box["release_year"])) if pd.notna(maior_box.get("release_year")) else "",
    poster_url=_clean_url(maior_box.get("poster_url")),
    accent="orange",
)

maior_rt = kpis.get("maior_rt", {})
kpi_record_card(
    col_b,
    label="Maior Rotten Tomatoes",
    value=f"{int(maior_rt['rotten_tomatoes'])}%" if maior_rt.get("rotten_tomatoes") is not None else "—",
    title=maior_rt.get("title", ""),
    year=str(int(maior_rt["release_year"])) if pd.notna(maior_rt.get("release_year")) else "",
    poster_url=_clean_url(maior_rt.get("poster_url")),
    accent="green",
)

pior_rt = kpis.get("pior_rt", {})
kpi_record_card(
    col_c,
    label="Pior Rotten Tomatoes",
    value=f"{int(pior_rt['rotten_tomatoes'])}%" if pior_rt.get("rotten_tomatoes") is not None else "0%",
    title=pior_rt.get("title", ""),
    year=str(int(pior_rt["release_year"])) if pd.notna(pior_rt.get("release_year")) else "",
    poster_url=_clean_url(pior_rt.get("poster_url")),
    accent="red",
)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SEÇÃO 2: EVOLUÇÃO DAS ADAPTAÇÕES
# ---------------------------------------------------------------------------

st.subheader("Hollywood está produzindo mais filmes baseados em videogames?")

df_tempo = df_tempo.copy()
df_tempo["decada"] = df_tempo["ano"].apply(lambda a: decada_de(int(a)))

_agg = {"Filmes": ("total_filmes", "sum")}
if "media_rt" in df_tempo.columns:
    _agg["media_rt"] = ("media_rt", "mean")
if "media_mc" in df_tempo.columns:
    _agg["media_mc"] = ("media_mc", "mean")

df_por_decada = (
    df_tempo.groupby("decada")
    .agg(**_agg)
    .reindex(DECADAS.keys())
    .fillna(0)
    .reset_index()
    .rename(columns={"decada": "Década"})
)

# Volume por década
st.markdown("##### Volume por década")

cols = st.columns(len(df_por_decada))
for i, row in df_por_decada.iterrows():
    rt = f"Média Rotten Tomatoes {row['media_rt']:.0f}%" if "media_rt" in df_por_decada.columns and row["media_rt"] else "Média Rotten Tomatoes —"
    mc = f"Média Metacritic {row['media_mc']:.0f}"       if "media_mc" in df_por_decada.columns and row["media_mc"] else "Média Metacritic —"
    cols[i].markdown(kpi_card(
        row["Década"],
        str(int(row["Filmes"])),
        caption=f"{rt} · {mc}",
        accent="blue",
    ), unsafe_allow_html=True)

st.markdown("")
st.markdown("")

# Filtros
anos_disponiveis = sorted(df_tempo["ano"].dropna().astype(int).unique())
_, col_slider, _ = st.columns([1, 4, 1])
with col_slider:
    intervalo = st.slider(
        "Período",
        min_value=int(anos_disponiveis[0]),
        max_value=int(anos_disponiveis[-1]),
        value=(int(anos_disponiveis[0]), int(anos_disponiveis[-1])),
        label_visibility="collapsed",
    )

df_filtrado = df_tempo[
    (df_tempo["ano"] >= intervalo[0]) & (df_tempo["ano"] <= intervalo[1])
].copy()

# Gráfico + card lateral
col_chart, col_card = st.columns([3, 1])

with col_chart:
    st.caption("💡 Clique em uma barra para ver o filme melhor avaliado no Rotten Tomatoes do ano (bilheteria desempata)")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_filtrado["ano"],
        y=df_filtrado["total_filmes"],
        marker_color=Colors.BLUE,
        marker_opacity=0.7,
        showlegend=False,
    ))
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8a9bb0"),
        margin=dict(t=10, b=10),
        height=700,
    )
    fig.update_xaxes(showgrid=False, color="#8a9bb0")
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.12)", zeroline=False, color="#8a9bb0")

    evento = st.plotly_chart(fig, width='stretch', on_select="rerun", key="grafico_evolucao")

with col_card:
    pontos = evento.get("selection", {}).get("points", []) if evento else []
    ano_selecionado = int(pontos[0]["x"]) if pontos else None

    if ano_selecionado is None:
        st.markdown(
            """
            <div style="height:650px;display:flex;flex-direction:column;
                        align-items:center;justify-content:center;
                        background:#1a2228;border-radius:6px;
                        color:#8a9bb0;font-size:0.78rem;text-align:center;padding:1rem;">
                🎮<br><br>Clique em um<br>ano no gráfico
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        df_silver = carregar_silver(con)
        df_ano = df_silver[df_silver["release_year"] == ano_selecionado].copy()

        # destaque: melhor RT com bilheteria conhecida; fallback: só melhor RT
        df_com_rt = df_ano[df_ano["rotten_tomatoes"].notna()]
        df_com_box = df_com_rt[df_com_rt["worldwide_box_office_usd"].notna()]
        if not df_com_box.empty:
            destaque = df_com_box.loc[df_com_box["rotten_tomatoes"].idxmax()]
        elif not df_com_rt.empty:
            destaque = df_com_rt.loc[df_com_rt["rotten_tomatoes"].idxmax()]
        else:
            destaque = df_ano.iloc[0]

        poster = _clean_url(destaque.get("poster_url"))
        rt_val  = destaque.get("rotten_tomatoes")
        mc_val  = destaque.get("metacritic")
        box_val = destaque.get("worldwide_box_office_usd")

        rt_html  = f"<div>Rotten Tomatoes <span style='color:#00e054'>{int(rt_val)}%</span></div>"  if (rt_val  is not None and pd.notna(rt_val))  else ""
        mc_html  = f"<div>Metacritic: <span style='color:#40bcf4'>{int(mc_val)}</span></div>"   if (mc_val  is not None and pd.notna(mc_val))  else ""
        box_html = f"<div>Bilheteria: <span style='color:#ff8000'>{_fmt_bilheteria(box_val)}</span></div>" if (box_val is not None and pd.notna(box_val)) else ""

        metricas_html = rt_html + mc_html + box_html
        if not metricas_html:
            metricas_html = "<div style='color:#8a9bb0;font-size:0.75rem'>Informações indisponíveis no banco de dados.</div>"

        poster_html = f'<img src="{poster}" style="width:100%;border-radius:6px 6px 0 0;display:block;">' if poster else \
                      '<div style="background:#0d1519;height:140px;border-radius:6px 6px 0 0;display:flex;align-items:center;justify-content:center;font-size:2rem">🎬</div>'

        st.markdown(
            f"""
            <div style="background:#1a2228;border-radius:6px;font-size:0.82rem;color:#ffffff;">
                {poster_html}
                <div style="padding:0.75rem;">
                    <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.08em;
                                text-transform:uppercase;color:#8a9bb0;margin-bottom:0.4rem">
                        Destaque de {ano_selecionado}
                    </div>
                    <div style="font-weight:700;margin-bottom:0.5rem;line-height:1.2">
                        {destaque['title']}
                    </div>
                    <div style="display:flex;flex-direction:column;gap:0.25rem;font-size:0.78rem">
                        {metricas_html}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )