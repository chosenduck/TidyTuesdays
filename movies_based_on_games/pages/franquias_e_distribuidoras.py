import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import carregar_conexao
from utils.data_transformer import carregar_gold, carregar_silver
from utils.constants import Colors
from utils.helpers import _identificar_franquia, _fmt_bilheteria, _clean_url, _identificar_distribuidora

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
# DADOS
# ---------------------------------------------------------------------------
con = carregar_conexao()
gold = carregar_gold(con)
silver = carregar_silver(con)

# Franquias
df_silver = silver.copy()
df_silver["franquia"] = df_silver["title"].apply(_identificar_franquia)

df_franquias = (
    df_silver.groupby("franquia")
    .agg(
        total_filmes=("title", "count"),
        bilheteria_total=("worldwide_box_office_usd", "sum"),
        media_rt=("rotten_tomatoes", "mean"),
        categorias=("category", lambda x: x.dropna().unique().tolist()),
    )
    .reset_index()
    .sort_values("total_filmes", ascending=False)
)

# Distribuidoras
df_pub = silver.copy()
df_pub["publisher"] = (
    df_pub["original_game_publisher"]
    .fillna("Não informado")
    .str.split(r"\s*\|\s*")
)
df_pub = df_pub.explode("publisher")
df_pub["publisher"] = df_pub["publisher"].apply(_identificar_distribuidora)

df_silver_pub = df_pub[df_pub["publisher"] != "Não informado"].copy()

df_distribuidoras = (
    df_silver_pub.groupby("publisher")
    .agg(
        total_filmes=("title", "count"),
        bilheteria_total=("worldwide_box_office_usd", "sum"),
        bilheteria_media=("worldwide_box_office_usd", "mean"),
        media_rt=("rotten_tomatoes", "mean"),
        media_meta=("metacritic", "mean"),
    )
    .reset_index()
    .sort_values("total_filmes", ascending=False)
)

# ---------------------------------------------------------------------------
# HELPER: card de destaque (reutilizado nas duas abas)
# ---------------------------------------------------------------------------
def _render_card(df_grupo, nome_grupo, col_grupo):
    """
    df_grupo  : linhas do silver filtradas para o grupo selecionado
    nome_grupo: label exibido (franquia ou publisher)
    col_grupo : nome da coluna de agrupamento (para exibir no card)
    """
    destaque = (
        df_grupo
        .assign(
            rotten_tomatoes=df_grupo["rotten_tomatoes"].fillna(-1),
            worldwide_box_office_usd=df_grupo["worldwide_box_office_usd"].fillna(-1),
        )
        .sort_values(
            ["rotten_tomatoes", "worldwide_box_office_usd"],
            ascending=[False, False],
        )
        .iloc[0]
    )

    poster   = _clean_url(destaque.get("poster_url"))
    rt_val   = destaque.get("rotten_tomatoes")
    mc_val   = destaque.get("metacritic")
    box_val  = destaque.get("worldwide_box_office_usd")

    anos_validos = df_grupo["release_year"].dropna().astype(int)
    primeiro_ano = anos_validos.min() if not anos_validos.empty else None
    ultimo_ano   = anos_validos.max() if not anos_validos.empty else None
    total_filmes = len(df_grupo)

    rt_html = (
        f"<div>Rotten Tomatoes: <span style='color:{Colors.GREEN}'>{int(rt_val)}%</span></div>"
        if pd.notna(rt_val) and rt_val != -1
        else "<div>Rotten Tomatoes: <span style='color:#8a9bb0'>Não disponível</span></div>"
    )
    mc_html = (
        f"<div>Metacritic: <span style='color:{Colors.BLUE}'>{int(mc_val)}</span></div>"
        if pd.notna(mc_val)
        else ""
    )
    box_html = (
        f"<div>Bilheteria: <span style='color:{Colors.ORANGE}'>{_fmt_bilheteria(box_val)}</span></div>"
        if pd.notna(box_val) and box_val != -1
        else ""
    )
    periodo_html = (
        f"<div>{total_filmes} filmes · {primeiro_ano}–{ultimo_ano}</div>"
        if primeiro_ano and ultimo_ano
        else ""
    )

    metricas_html = periodo_html + rt_html + mc_html + box_html
    if not metricas_html:
        metricas_html = "<div style='color:#8a9bb0;font-size:0.75rem'>Informações indisponíveis.</div>"

    poster_html = (
        f'<img src="{poster}" style="width:100%;border-radius:6px 6px 0 0;display:block;">'
        if poster
        else '<div style="background:#0d1519;height:140px;border-radius:6px 6px 0 0;display:flex;align-items:center;justify-content:center;font-size:2rem">🎬</div>'
    )

    st.markdown(
        f"""
        <div style="background:#1a2228;border-radius:6px;font-size:0.82rem;color:#ffffff;">
        {poster_html}
        <div style="padding:0.75rem;">
            <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.08em;
                    text-transform:uppercase;color:#8a9bb0;margin-bottom:0.4rem;">
                Destaque
            </div>
            <div style="font-size:0.95rem;font-weight:700;margin-bottom:0.25rem;line-height:1.2;">
                {destaque["title"]}
            </div>
            <div style="color:#8a9bb0;font-size:0.75rem;margin-bottom:0.75rem;">
                {nome_grupo}
            </div>
            <div style="display:flex;flex-direction:column;gap:0.25rem;font-size:0.78rem;">
                {metricas_html}
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_card_vazio():
    st.markdown(
        """
        <div style="
            height:650px;
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            background:#1a2228;
            border-radius:6px;
            color:#8a9bb0;
            font-size:0.80rem;
            text-align:center;
            padding:1rem;
        ">
            🎮<br><br>
            Clique em uma<br>
            franquia no gráfico
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# HELPER: gráfico de barras horizontal
# ---------------------------------------------------------------------------
def _bar_chart(df_plot, y_col, chart_key):
    hover = [
        f"<b>{row[y_col]}</b><br>"
        f"Filmes: {int(row['total_filmes'])}<br>"
        + (f"RT médio: {int(row['media_rt'])}%" if pd.notna(row["media_rt"]) else "RT: Não disponível")
        + "<extra></extra>"
        for _, row in df_plot.iterrows()
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=df_plot[y_col],
            x=df_plot["total_filmes"],
            orientation="h",
            marker_color=Colors.BLUE,
            marker_opacity=0.75,
            text=df_plot["total_filmes"],
            textposition="outside",
            textfont=dict(color=Colors.WHITE),
            hovertemplate=hover,
        )
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8a9bb0"),
        margin=dict(t=10, b=10, l=10, r=40),
        height=max(700, len(df_plot) * 28),
        hovermode="closest",
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(128,128,128,0.15)",
        zeroline=False,
        color="#8a9bb0",
    )
    fig.update_yaxes(showgrid=False, color="#8a9bb0")

    return st.plotly_chart(fig, width="stretch", on_select="rerun", key=chart_key)


# ---------------------------------------------------------------------------
# HELPER: scatter bilheteria
# ---------------------------------------------------------------------------
def _scatter_bilheteria(df_agg, x_col, label_col):
    df_scatter = (
        df_agg
        .dropna(subset=["bilheteria_total"])
        .query("bilheteria_total > 0")
    )

    mediana_filmes     = df_scatter["total_filmes"].median()
    mediana_bilheteria = df_scatter["bilheteria_total"].median()

    hover = [
        f"<b>{row[label_col]}</b><br>"
        f"Filmes: {int(row['total_filmes'])}<br>"
        f"Bilheteria total: {_fmt_bilheteria(row['bilheteria_total'])}<br>"
        + (f"RT médio: {int(row['media_rt'])}%" if pd.notna(row["media_rt"]) else "RT: Não disponível")
        + "<extra></extra>"
        for _, row in df_scatter.iterrows()
    ]

    df_labels    = df_scatter.nlargest(5, "bilheteria_total")
    df_sem_label = df_scatter[~df_scatter[label_col].isin(df_labels[label_col])]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_sem_label["total_filmes"],
            y=df_sem_label["bilheteria_total"],
            mode="markers",
            marker=dict(
                size=14,
                color=df_sem_label["media_rt"],
                colorscale="RdYlGn",
                cmin=0,
                cmax=100,
                opacity=0.7,
                colorbar=dict(
                    title="RT médio",
                ),
                line=dict(width=0.8, color="rgba(255,255,255,0.2)")
            ),
            hovertemplate=[
                f"<b>{row[label_col]}</b><br>"
                f"Filmes: {int(row['total_filmes'])}<br>"
                f"Bilheteria total: {_fmt_bilheteria(row['bilheteria_total'])}<br>"
                + (f"RT médio: {int(row['media_rt'])}%" if pd.notna(row["media_rt"]) else "RT: Não disponível")
                + "<extra></extra>"
                for _, row in df_sem_label.iterrows()
            ],
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_labels["total_filmes"],
            y=df_labels["bilheteria_total"],
            mode="markers+text",
            marker=dict(
                size=18,
                color=df_labels["media_rt"],
                colorscale="RdYlGn",
                cmin=0,
                cmax=100,
                opacity=0.95,
                line=dict(width=1.5, color="white"),
            ),
            text=[
                f"{nome}"
                if pd.notna(rt)
                else nome
                for nome, rt in zip(
                    df_labels[label_col],
                    df_labels["media_rt"]
                )
            ],
            textposition="top center",
            textfont=dict(size=11, color="#8a9bb0"),
            hovertemplate=[
                f"<b>{row[label_col]}</b><br>"
                f"Filmes: {int(row['total_filmes'])}<br>"
                f"Bilheteria total: {_fmt_bilheteria(row['bilheteria_total'])}<br>"
                + (f"RT médio: {int(row['media_rt'])}%" if pd.notna(row["media_rt"]) else "RT: Não disponível")
                + "<extra></extra>"
                for _, row in df_labels.iterrows()
            ],
            showlegend=False,
        )
    )

    fig.add_vline(x=mediana_filmes,     line_dash="dot", line_color="rgba(180,180,180,0.4)")
    fig.add_hline(y=mediana_bilheteria, line_dash="dot", line_color="rgba(180,180,180,0.4)")

    fig.update_layout(
        xaxis=dict(
            title="Número de adaptações",
            showgrid=True,
            gridcolor="rgba(128,128,128,0.12)",
            zeroline=False,
            dtick=1,
            color="#8a9bb0",
        ),
        yaxis=dict(
            title="Bilheteria acumulada (USD)",
            showgrid=True,
            gridcolor="rgba(128,128,128,0.12)",
            zeroline=False,
            color="#8a9bb0",
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8a9bb0"),
        hovermode="closest",
        margin=dict(t=20, b=20),
        height=500,
    )

    st.plotly_chart(fig, width="stretch")


# ---------------------------------------------------------------------------
# ABAS
# ---------------------------------------------------------------------------
aba_franquias, aba_distribuidoras = st.tabs(["🎮 Franquias", "🏢 Distribuidoras"])

# FRANQUIAS
with aba_franquias:

    st.subheader("Quais universos mais chegaram aos cinemas?")

    todas_cats = sorted(df_silver["category"].dropna().unique())
    cats_selecionadas = st.multiselect(
        "Filtrar por categoria",
        options=todas_cats,
        default=[],
        placeholder="Todas as categorias",
        key="cats_franquias",
    )

    df_filtrado = df_silver.copy()
    if cats_selecionadas:
        df_filtrado = df_filtrado[df_filtrado["category"].isin(cats_selecionadas)]

    df_plot_f = (
        df_filtrado
        .groupby("franquia", as_index=False)
        .agg(total_filmes=("title", "count"), media_rt=("rotten_tomatoes", "mean"))
        .sort_values("total_filmes", ascending=False)
        .head(10)
        .sort_values("total_filmes", ascending=True)
    )

    st.caption("💡 Clique em uma franquia para ver seu filme mais bem avaliado no Rotten Tomatoes (bilheteria desempata)")

    col_chart, col_card = st.columns([3, 1])

    with col_chart:
        evento_f = _bar_chart(df_plot_f, y_col="franquia", chart_key="grafico_franquias")

    with col_card:
        pontos_f = evento_f.get("selection", {}).get("points", []) if evento_f else []
        franquia_sel = pontos_f[0]["y"] if pontos_f else None

        if franquia_sel is None:
            _render_card_vazio()
        else:
            _render_card(
                df_grupo=df_filtrado[df_filtrado["franquia"] == franquia_sel].copy(),
                nome_grupo=franquia_sel,
                col_grupo="franquia",
            )

    st.divider()

    st.subheader("Quantidade ou impacto?")

    min_filmes_f = st.slider(
        "Filtro: Mínimo de filmes na franquia",
        min_value=1,
        max_value=16,
        value=1,
        step=1,
        key="slider_franquias",
    )

    _scatter_bilheteria(
        df_agg=df_franquias[df_franquias["total_filmes"] >= min_filmes_f],
        x_col="total_filmes",
        label_col="franquia",
    )

# DISTRIBUIDORAS
with aba_distribuidoras:

    st.subheader("Quem mais transformou jogos em filmes?")

    top_n = st.slider("Top publishers", min_value=5, max_value=25, value=15, key="slider_pub")

    df_plot_p = (
        df_distribuidoras
        .nlargest(top_n, "total_filmes")
        .sort_values("total_filmes")
    )

    st.caption("💡 Clique em uma publisher para ver seu filme mais bem avaliado no Rotten Tomatoes (bilheteria desempata)")

    col_chart_p, col_card_p = st.columns([3, 1])

    with col_chart_p:
        evento_p = _bar_chart(df_plot_p, y_col="publisher", chart_key="grafico_distribuidoras")

    with col_card_p:
        pontos_p = evento_p.get("selection", {}).get("points", []) if evento_p else []
        pub_sel = pontos_p[0]["y"] if pontos_p else None

        if pub_sel is None:
            _render_card_vazio()
        else:
            _render_card(
                df_grupo=df_silver_pub[df_silver_pub["publisher"] == pub_sel].copy(),
                nome_grupo=pub_sel,
                col_grupo="publisher",
            )

    st.divider()

    st.subheader("Presença ou desempenho?")
    st.markdown(
        "Volume ajuda na bilheteria, mas a recepção crítica conta uma história diferente."
    )

    min_filmes_p = st.slider(
        "Filtro: Mínimo de filmes da publisher",
        min_value=1,
        max_value=30,
        value=1,
        step=1,
        key="slider_pub_scatter",
    )

    _scatter_bilheteria(
        df_agg=df_distribuidoras[df_distribuidoras["total_filmes"] >= min_filmes_p],
        x_col="total_filmes",
        label_col="publisher",
    )