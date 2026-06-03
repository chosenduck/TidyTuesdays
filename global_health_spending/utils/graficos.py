import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import pandas as pd

from utils.constants import (
    FONTE, NOTA,
    FMT_BI, FMT_PCT,
    CORES,
    CORES_HS_INDIC, CORES_FS_INDIC, CORES_SP_GRUP,
    ORDEM_GRUPOS,
    RENOMEAR_HS, RENOMEAR_FS, RENOMEAR_SP_PT,
    INDICADORES_HS_PCT, INDICADORES_SP_ABS,
)
from utils.data_processor import traduzir_paises, para_bilhoes


# ─── Helpers visuais ──────────────────────────────────────────
def _adicionar_fonte():
    """Adiciona rodapé de fonte e nota em todos os gráficos."""
    plt.figtext(0.01, -0.02, FONTE, ha="left",  fontsize=9, color="gray")
    plt.figtext(0.99, -0.02, NOTA,  ha="right", fontsize=9, color="gray")


def _adicionar_rotulos_internos(ax, threshold: int = 3):
    """Adiciona rótulos percentuais dentro de barras empilhadas."""
    for container in ax.containers:
        labels = [
            f"{v:.1f}%" if v > threshold else ""
            for v in container.datavalues
        ]
        ax.bar_label(
            container,
            labels=labels,
            label_type="center",
            color="white",
            fontsize=9,
            weight="bold",
        )


def _estilo_limpo(ax):
    """Remove bordas superiores e direitas — padrão para gráficos de linha."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    ax.grid(axis="x", visible=False)


# ─── Health Spending ──────────────────────────────────────────
def grafico_hs_linha(df, col_y, titulo, cor, fmt):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df[col_y],
            mode="lines+markers",
            line=dict(color=cor, width=3),
            marker=dict(size=7),
            hovertemplate=
                "<b>Ano:</b> %{x}<br>" +
                "<b>Valor:</b> %{y:.1f}<extra></extra>"
        )
    )

    fig.update_layout(
        height=550,
        template="simple_white",

        title=dict(
            text=titulo,
            font=dict(size=20),
            x=0,
        ),

        margin=dict(
            l=40,
            r=40,
            t=80,
            b=80,
        ),

        xaxis=dict(
            title="",
            tickmode="linear",
            tick0=2000,
            dtick=4,
            showgrid=False,
        ),

        yaxis=dict(
            title="",
            gridcolor="rgba(0,0,0,0.08)",
            tickprefix="US$ ",
            ticksuffix=" bi",
        ),

        hovermode="x unified",

        annotations=[
            dict(
                text=FONTE,
                xref="paper",
                yref="paper",
                x=0,
                y=-0.18,
                showarrow=False,
                font=dict(size=11, color="gray"),
                align="left",
            ),

            dict(
                text=NOTA,
                xref="paper",
                yref="paper",
                x=1,
                y=-0.18,
                showarrow=False,
                font=dict(size=11, color="gray"),
                xanchor="right",
                align="right",
            ),
        ]
    )

    return fig


def grafico_hs_duplo_eixo(
    df_abs: pd.DataFrame,
    df_pct: pd.DataFrame,
    titulo: str,
) -> plt.Figure:
    """
    Gráfico 3 — Barras (absoluto) + linha (%) em eixos Y duplos.

    Parâmetros
    ----------
    df_abs : DataFrame com colunas 'year' e 'value_bi'
    df_pct : DataFrame com colunas 'year' e 'value'
    titulo : título do gráfico
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_axisbelow(True)
    ax1.grid(axis="y", alpha=0.3)
    ax1.bar(df_abs["year"], df_abs["value_bi"], color=CORES["outro"], label="US$ bilhões (2023)")
    ax1.yaxis.set_major_formatter(FMT_BI)
    ax1.set_ylabel("US$ bilhões (2023)")

    ax2 = ax1.twinx()
    ax2.grid(False)
    ax2.plot(
        df_pct["year"], df_pct["value"],
        color=CORES["governo"], marker="o", linewidth=2,
        label="% do gasto total em saúde",
    )
    ax2.yaxis.set_major_formatter(FMT_PCT)
    ax2.set_ylabel("% do gasto total em saúde", color=CORES["governo"])
    ax2.tick_params(axis="y", labelcolor=CORES["governo"])

    ax1.set_xticks(range(2000, 2024, 4))
    ax1.set_xlabel("")
    ax1.set_title(titulo, fontsize=14, weight="bold", pad=12)

    _adicionar_fonte()
    plt.tight_layout()
    return fig


def grafico_hs_evolucao_fontes(
    df_abs_pivot: pd.DataFrame,
    df_pct_pivot: pd.DataFrame,
) -> tuple[plt.Figure, plt.Figure]:
    """
    Gráficos 4 e 5 — Evolução absoluta (linhas) e perfil percentual (área empilhada).

    Parâmetros
    ----------
    df_abs_pivot : pivot com colunas 'year', 'Governo', 'Privado'
    df_pct_pivot : pivot com colunas 'year', 'Governo', 'Privado'

    Retorna dois objetos Figure (absoluto, percentual).
    """
    # Gráfico 4 — Linhas absolutas
    gov  = df_abs_pivot["Governo"]
    priv = df_abs_pivot["Privado"]
    anos = df_abs_pivot["year"]

    fig4, ax4 = plt.subplots(figsize=(12, 6))

    ax4.plot(anos, gov,  linewidth=3, color=CORES["governo"], label="Governo")
    ax4.plot(anos, priv, linewidth=3, color=CORES["privado"], label="Privado")

    ax4.yaxis.set_major_formatter(FMT_BI)

    cresc_gov  = (gov.iloc[-1]  / gov.iloc[0]  - 1) * 100
    cresc_priv = (priv.iloc[-1] / priv.iloc[0] - 1) * 100

    ax4.text(2023.2, gov.iloc[-1],  f"+{cresc_gov:.0f}%",  fontsize=11, fontweight="bold", color=CORES["governo"], va="center")
    ax4.text(2023.2, priv.iloc[-1], f"+{cresc_priv:.0f}%", fontsize=11, fontweight="bold", color=CORES["privado"], va="center")

    ax4.set_xlim(2000, 2024.8)
    ax4.set_xticks(range(2000, 2024, 4))
    ax4.set_xlabel("")
    ax4.set_ylabel("")
    ax4.legend(loc="lower left", bbox_to_anchor=(0.3, 1.02), ncol=2, frameon=False)

    fig4.suptitle(
        "Gastos públicos e privados com saúde praticamente dobraram desde 2000",
        fontsize=15, fontweight="bold", x=0.125, ha="left", y=0.98,
    )

    _estilo_limpo(ax4)
    _adicionar_fonte()
    plt.tight_layout()

    # Gráfico 5 — Área empilhada percentual
    fig5, ax5 = plt.subplots(figsize=(12, 6))

    ax5.stackplot(
        df_pct_pivot["year"],
        df_pct_pivot["Governo"],
        df_pct_pivot["Privado"],
        labels=["Governo", "Privado"],
        colors=[CORES["governo"], CORES["privado"]],
        alpha=0.9,
    )

    ax5.set_xlim(2000, 2023)
    ax5.set_ylim(0, 100)
    ax5.yaxis.set_major_formatter(FMT_PCT)
    ax5.set_xticks(range(2000, 2024, 4))
    ax5.set_xlabel("")
    ax5.set_ylabel("")
    ax5.grid(axis="y", alpha=0.2)
    ax5.grid(axis="x", visible=False)
    ax5.legend(title="", loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False)
    ax5.set_title(
        "Mesmo com a expansão do gasto público, o setor privado predominou durante toda a série histórica",
        fontsize=13, weight="bold",
    )

    _adicionar_fonte()
    plt.tight_layout()

    return fig4, fig5


def grafico_hs_grupo_linha(
    df: pd.DataFrame,
    col_y: str,
    palette: dict,
    hue_order: list,
    titulo: str,
    fmt,
) -> plt.Figure:
    """
    Gráficos 6, 7, 9, 10 — Linha multissérie para grupos de países (BRICS ou universais).

    Parâmetros
    ----------
    df        : DataFrame com colunas 'year', col_y e 'Pais'
    col_y     : coluna do eixo Y ('total' ou 'gasto_pc')
    palette   : dicionário {país: cor}
    hue_order : ordem das séries na legenda
    titulo    : título do gráfico
    fmt       : formatador do eixo Y (FMT_BI ou FMT_PCT)
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    sns.lineplot(
        data=df, x="year", y=col_y,
        hue="Pais", hue_order=hue_order,
        marker="o", linewidth=2.5,
        palette={p: palette.get(p, "#cccccc") for p in df["Pais"].unique()},
        ax=ax,
    )

    ax.yaxis.set_major_formatter(fmt)
    ax.set_xticks(range(2000, 2024, 4))
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(titulo, fontsize=14, weight="bold")
    ax.legend(title="", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)

    _adicionar_fonte()
    plt.tight_layout()
    return fig


def grafico_hs_perfil_grupo(
    df: pd.DataFrame,
    ano: int,
    titulo: str,
) -> plt.Figure:
    """
    Gráficos 8 e 11 — Barras horizontais empilhadas do perfil de financiamento
    (Governo / Privado / Externo) para um grupo de países em um ano específico.

    Parâmetros
    ----------
    df    : DataFrame filtrado (df_hs_brics ou df_hs_universal)
    ano   : ano de corte para o snapshot
    titulo: título do gráfico
    """
    df_ano = (
        df[
            (df["year"] == ano) &
            (df["indicator_code"].isin(INDICADORES_HS_PCT))
        ]
        .pipe(traduzir_paises)
        .pivot(index="country_name", columns="indicator_code", values="value")
        .reset_index()
        .rename(columns=RENOMEAR_HS)
        .sort_values("Governo", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(12, 8))
    df_ano.set_index("country_name")[["Governo", "Privado", "Externo"]].plot(
        kind="barh", stacked=True,
        color=CORES_HS_INDIC, width=0.8, ax=ax,
    )

    _adicionar_rotulos_internos(ax, threshold=4)
    ax.invert_yaxis()
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(titulo, fontsize=14, weight="bold")
    ax.legend(title="", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)

    _adicionar_fonte()
    plt.tight_layout()
    return fig


# ─── Financing Schemes ────────────────────────────────────────

def grafico_fs_barras_brasil(df_pct_pivot: pd.DataFrame, titulo: str) -> plt.Figure:
    """
    Gráfico 12 — Barras horizontais empilhadas do perfil de financiamento do Brasil ao longo dos anos.

    Parâmetros
    ----------
    df_pct_pivot : pivot com index 'Ano' e colunas SUS/Planos/Desembolso/Nao Identificado
    titulo       : título do gráfico
    """
    df = df_pct_pivot.drop(columns=["Ajuda Externa"], errors="ignore")

    fig, ax = plt.subplots(figsize=(15, 14))
    df.set_index("Ano").plot(
        kind="barh", stacked=True,
        color=CORES_FS_INDIC, width=0.85, ax=ax,
    )

    _adicionar_rotulos_internos(ax, threshold=3)
    ax.grid(axis="y", visible=False)
    ax.invert_yaxis()
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(titulo, fontsize=14, weight="bold", pad=35)
    ax.legend(title="", loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=4, frameon=False)

    _adicionar_fonte()
    plt.tight_layout()
    return fig


def grafico_fs_evolucao_linhas(df_abs_plot: pd.DataFrame, titulo: str) -> plt.Figure:
    """
    Gráfico 13 — Linhas de crescimento absoluto por componente de financiamento (Brasil).

    Parâmetros
    ----------
    df_abs_plot : DataFrame com colunas 'Ano', 'SUS + RPPS', 'Planos de Saude', 'Desembolso direto'
    titulo      : título do gráfico
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    anos   = df_abs_plot["Ano"]
    sus    = df_abs_plot["SUS + RPPS"]
    planos = df_abs_plot["Planos de Saude"]
    oop    = df_abs_plot["Desembolso direto"]

    ax.plot(anos, sus,    linewidth=3, color=CORES["governo"], label="SUS + RPPS")
    ax.plot(anos, planos, linewidth=3, color=CORES["privado"], label="Planos de Saúde")
    ax.plot(anos, oop,    linewidth=3, color=CORES["oop"],     label="Desembolso direto")

    ax.yaxis.set_major_formatter(FMT_BI)
    ax.set_xticks(range(2000, 2024, 4))
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(titulo, fontsize=14, weight="bold")
    ax.legend(title="", loc="lower left", bbox_to_anchor=(0.3, 1.02), ncol=3, frameon=False)

    _estilo_limpo(ax)
    _adicionar_fonte()
    plt.tight_layout()
    return fig


def grafico_fs_perfil_grupo(
    df: pd.DataFrame,
    ano: int,
    titulo: str,
) -> plt.Figure:
    """
    Gráficos 14 e 15 — Barras horizontais empilhadas de desembolso direto
    para um grupo de países (BRICS ou universais) em um ano específico.

    Parâmetros
    ----------
    df    : DataFrame filtrado (df_fs_brics ou df_fs_universal)
    ano   : ano de corte
    titulo: título do gráfico
    """
    from utils.constants import INDICADORES_FS_PCT

    df_ano = (
        df[
            (df["year"] == ano) &
            (df["indicator_code"].isin(INDICADORES_FS_PCT))
        ]
        .pipe(traduzir_paises)
        .pivot(index="country_name", columns="indicator_code", values="value")
        .reset_index()
        .rename(columns=RENOMEAR_FS)
        .rename(columns={"SUS + RPPS": "Governo"})
        .sort_values("Desembolso direto", ascending=False)
    )

    colunas = ["Governo", "Planos de Saude", "Desembolso direto"]

    fig, ax = plt.subplots(figsize=(12, 8))
    df_ano.set_index("country_name")[colunas].plot(
        kind="barh", stacked=True,
        color=CORES_FS_INDIC, width=0.8, ax=ax,
    )

    _adicionar_rotulos_internos(ax, threshold=4)
    ax.invert_yaxis()
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.suptitle(titulo, fontsize=15, fontweight="bold")
    ax.legend(loc="lower left", bbox_to_anchor=(0.25, 1.02), ncol=3, frameon=False)

    _adicionar_fonte()
    plt.tight_layout()
    return fig


# ─── Spending Purpose ─────────────────────────────────────────
def grafico_sp_componentes(df_sp_abs_plot: pd.DataFrame, titulo: str) -> plt.Figure:
    """
    Gráfico 16 — Linhas de evolução absoluta por componente de gasto (Brasil).

    Parâmetros
    ----------
    df_sp_abs_plot : DataFrame no formato longo com colunas 'Ano', 'Componente', 'Valor'
    titulo         : título do gráfico
    """
    palette_sp = {
        "Assistencia curativa":      CORES["Reativo"],
        "Reabilitacao":              CORES["privado"],
        "Cuidados de longa duracao": CORES["oop"],
        "Servicos auxiliares":       "#9467bd",
        "Produtos medicos":          "#8c564b",
        "Prevencao e promocao":      CORES["Preventivo/Proativo"],
        "Governanca e administracao":"#17becf",
        "Outros":                    CORES["outro"],
    }

    fig, ax = plt.subplots(figsize=(14, 7))

    sns.lineplot(
        data=df_sp_abs_plot, x="Ano", y="Valor",
        hue="Componente", marker="o", linewidth=2.5,
        palette=palette_sp, ax=ax,
    )

    ax.yaxis.set_major_formatter(FMT_BI)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(titulo, fontsize=14, weight="bold")
    ax.legend(title="", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)

    _adicionar_fonte()
    plt.tight_layout()
    return fig


def grafico_sp_grupos(df_pct_pivot: pd.DataFrame, titulo: str) -> plt.Figure:
    """
    Gráfico 17 — Barras horizontais empilhadas por grupo de gasto ao longo dos anos (Brasil).

    Parâmetros
    ----------
    df_pct_pivot : pivot com index 'year' e colunas em ORDEM_GRUPOS
    titulo       : título do gráfico
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    df_pct_pivot.set_index("year")[ORDEM_GRUPOS].plot(
        kind="barh", stacked=True,
        color=CORES_SP_GRUP, width=0.85, ax=ax,
    )

    _adicionar_rotulos_internos(ax, threshold=5)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.suptitle(titulo, fontsize=14, weight="bold")
    ax.legend(loc="lower left", bbox_to_anchor=(0.2, 1.02), ncol=4, frameon=False)

    _adicionar_fonte()
    plt.tight_layout()
    return fig


def grafico_sp_razao(df_sp_brasil: pd.DataFrame) -> plt.Figure:
    """
    Gráfico 18 — Razão HC1/HC6 (curativo vs preventivo) ao longo do tempo.

    Parâmetros
    ----------
    df_sp_brasil : DataFrame processado do Brasil (saída de preparar_sp)
    """
    df_razao = df_sp_brasil[
        df_sp_brasil["indicator_code"].isin(["hc1_usd2023", "hc6_usd2023"])
    ].copy()

    df_pivot = (
        df_razao
        .pivot(index="year", columns="indicator_code", values="value")
        .reset_index()
        .rename(columns={"hc1_usd2023": "Reativo", "hc6_usd2023": "Prevenção"})
    )

    df_pivot["Razao"] = df_pivot["Reativo"] / df_pivot["Prevenção"]
    media = df_pivot["Razao"].mean()

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df_pivot["year"], df_pivot["Razao"], linewidth=3, color=CORES["oop"], label="HC1 / HC6")
    ax.axhline(media, linestyle="--", linewidth=2, color="gray", alpha=0.7, label=f"Média ({media:.1f})")
    ax.text(0.92, 0.67, f"Média: {media:.1f}", transform=ax.transAxes, ha="left", va="center", color="gray", fontsize=10)

    ax.yaxis.set_major_formatter(FMT_BI)
    ax.set_xlabel("")
    ax.set_ylabel("Razão Reativo/Preventivo")
    ax.set_xlim(df_pivot["year"].min(), df_pivot["year"].max())

    fig.suptitle(
        "Brasil têm predominância do gasto curativo sobre o preventivo,\ncom leve redução do desequilíbrio em 2022",
        fontsize=15, fontweight="bold",
    )

    _estilo_limpo(ax)
    _adicionar_fonte()
    plt.tight_layout()
    return fig


def grafico_sp_perfil_comparado(
    df: pd.DataFrame,
    lista_paises: list,
    ano: int,
    titulo: str,
) -> plt.Figure:
    """
    Gráficos 19 e universal — Barras horizontais empilhadas por grupo de gasto
    para múltiplos países em um ano específico.

    Parâmetros
    ----------
    df          : DataFrame processado (saída de preparar_sp)
    lista_paises: lista de países no padrão original em inglês
    ano         : ano de corte
    titulo      : título do gráfico
    """
    df_ano = (
        df[
            (df["year"] == ano) &
            (df["country_name"].isin(lista_paises)) &
            (df["indicator_code"].isin(INDICADORES_SP_ABS))
        ]
        .groupby(["country_name", "grupo"])["value"]
        .sum()
        .reset_index()
    )

    df_ano["pct"] = df_ano.groupby("country_name")["value"].transform(
        lambda x: x / x.sum() * 100
    )
    df_ano = df_ano.pipe(traduzir_paises)

    pivot = (
        df_ano
        .pivot(index="country_name", columns="grupo", values="pct")
        .reset_index()
    )

    for col in ORDEM_GRUPOS:
        if col not in pivot.columns:
            pivot[col] = 0.0

    pivot = pivot.sort_values("Preventivo/Proativo", ascending=False)

    fig, ax = plt.subplots(figsize=(14, 7))
    pivot.set_index("country_name")[ORDEM_GRUPOS].plot(
        kind="barh", stacked=True,
        color=CORES_SP_GRUP, width=0.85, ax=ax,
    )

    _adicionar_rotulos_internos(ax, threshold=5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.suptitle(titulo, fontsize=14, weight="bold")
    ax.legend(loc="lower left", bbox_to_anchor=(0.2, 1.02), ncol=4, frameon=False)

    _adicionar_fonte()
    plt.tight_layout()
    return fig