import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.constants import (COR_BARRAS, COR_LINHA, COR_GOV, COR_PRIV, COMPONENTES, CORES_FS, PAISES_ORDEM, CORES_BRICS)

def gasto_total_brasil(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df_abs = con.sql("""
            SELECT
                year,
                value / 1000000000.0 AS value_bi

            FROM silver_health_spending
                     
            WHERE country_name = 'Brazil'
                AND indicator_code = 'che_usd2023'
                     
            ORDER BY year
        """).df()
    
    cresc = (df_abs["value_bi"].iloc[-1] / df_abs["value_bi"].iloc[0] - 1) * 100
    ano_min = df_abs["year"].min()
    ano_max = df_abs["year"].max()

    fig = go.Figure()

    # Linha
    fig.add_trace(go.Scatter(
        x=df_abs["year"],
        y=df_abs["value_bi"],
        name="Gasto Total",
        mode="lines+markers",
        line=dict(color=COR_LINHA, width=3),
        marker=dict(color=COR_LINHA)
    ))

    fig.add_annotation(
        x=ano_max,
        y=df_abs["value_bi"].iloc[-1],
        text=f"<b>+{cresc:.0f}%</b>",
        xanchor="left", xshift=8,
        showarrow=False,
        font=dict(color=COR_LINHA, size=12),
    )

    fig.update_layout(

        title=dict(
            text="Gasto total em saúde quase dobrou em duas décadas",
            x=0.5,
            xanchor="center",
        ),

        annotations=[
            # Crescimento percentual
            dict(
                x=ano_max, y=df_abs["value_bi"].iloc[-1],
                text=f"<b>+{cresc:.0f}%</b>",
                xanchor="left", xshift=8,
                showarrow=False,
                font=dict(color=COR_LINHA, size=12),
            ),
            # Rodapé esquerdo
            dict(
                text="Fonte: WHO Global Health Expenditure Database. Elaboração própria.",
                xref="paper", yref="paper",
                x=0, y=-0.12,
                xanchor="left",
                showarrow=False,
                font=dict(size=9),
            ),
            # Rodapé direito
            dict(
                text="Nota: Valores em US$ constantes de 2023.",
                xref="paper", yref="paper",
                x=1, y=-0.12,
                xanchor="right",
                showarrow=False,
                font=dict(size=9),
            ),
        ],

        margin=dict(b=60),
        template="plotly_white",
        hovermode="x",
        hoverlabel=dict(
                font_size=13,
                namelength=-1,  # -1 = sem limite de caracteres no nome da série
            ),

        xaxis=dict(
            range=[ano_min - 0.5, ano_max + 2],
            tickmode="linear",
            dtick=4,
            showgrid=False,
        ),

        yaxis=dict(
            tickformat=".0f",
            ticksuffix="bi",
            tickprefix="US$ ",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),

        height=500,
    )

    return fig


def plot_gasto_publico_brasil(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df_abs = con.sql("""
            SELECT
                year,
                value / 1000000000.0 AS value_bi

            FROM silver_health_spending

            WHERE country_name = 'Brazil'
                AND tipo_indicador = 'ABS'
                AND indicator_code = 'gghed_usd2023'

            ORDER BY year
        """).df()
    
    df_pct = con.sql("""
        SELECT
            year,
            value

        FROM silver_health_spending

        WHERE country_name = 'Brazil'
            AND tipo_indicador = 'PCT'
            AND indicator_code = 'gghed_che'

        ORDER BY year
    """).df()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_abs["year"],
            y=df_abs["value_bi"],
            name="US$ bilhões (2023)",
            marker_color=COR_BARRAS,
            opacity=0.85
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_pct["year"],
            y=df_pct["value"],
            name="% do gasto total em saúde",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color=COR_LINHA, width=2.5),
            marker=dict(color=COR_LINHA)
        )
    )

    fig.update_layout(

        title=dict(
            text=("Gasto público em saúde dobrou, mas sem aumento relevante da participação pública no total"),
            x=0.5,
            xanchor="center",
        ),

        annotations=[
            # Rodapé esquerdo
            dict(
                text="Fonte: WHO Global Health Expenditure Database. Elaboração própria.",
                xref="paper", yref="paper",
                x=0, y=-0.12,
                xanchor="left",
                showarrow=False,
                font=dict(size=9),
            ),
            # Rodapé direito
            dict(
                text="Nota: Valores em US$ constantes de 2023.",
                xref="paper", yref="paper",
                x=1, y=-0.12,
                xanchor="right",
                showarrow=False,
                font=dict(size=9),
            ),
        ],

        margin=dict(b=60),

        template="plotly_white",

        hovermode="x",

        hoverlabel=dict(
                font_size=13,
                namelength=-1,  # -1 = sem limite de caracteres no nome da série
            ),

        xaxis=dict(
            range=[df_abs["year"].min() - 0.5, df_abs["year"].max() + 0.5],
            title="",
            tickmode="linear",
            dtick=4,
            showgrid=False,
        ),

        yaxis=dict(
            title=dict(text="US$ bilhões (2023)", font=dict(color=COR_BARRAS)),
            tickfont=dict(color=COR_BARRAS),
            tickformat=".1f",
            ticksuffix="bi",
            tickprefix="US$ ",
            rangemode="tozero",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
        ),

        yaxis2=dict(
            title=dict(text="% do gasto total em saúde", font=dict(color=COR_LINHA)),
            tickfont=dict(color=COR_LINHA),
            tickformat=".0f",  
            ticksuffix="%",
            overlaying="y",
            side="right",
            rangemode="tozero",
            showgrid=False,
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),

        bargap=0.2,

        height=550,
    )

    return fig

def plot_evolucao_pub_x_priv(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df = con.sql("""
        SELECT
            year,
            SUM(CASE WHEN indicator_code = 'gghed_usd2023' THEN value / 1e9 END) AS governo,
            SUM(CASE WHEN indicator_code = 'pvtd_usd2023' THEN value / 1e9 END) AS privado
                 
        FROM silver_health_spending
                 
        WHERE country_name = 'Brazil'
            AND tipo_indicador = 'ABS'
            AND indicator_code IN ('gghed_usd2023', 'pvtd_usd2023')
                 
        GROUP BY year
                 
        ORDER BY year
    """).df()

    cresc_gov  = (df["governo"].iloc[-1] / df["governo"].iloc[0] - 1) * 100
    cresc_priv = (df["privado"].iloc[-1] / df["privado"].iloc[0] - 1) * 100
    ano_max = df["year"].max()

    fig = go.Figure()

    # Linha Governo
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["governo"],
        name="Governo",
        mode="lines+markers",
        line=dict(color=COR_GOV, width=3),
    ))

    # Linha Privado
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["privado"],
        name="Privado",
        mode="lines+markers",
        line=dict(color=COR_PRIV, width=3),
    ))

    fig.update_layout(

        title=dict(
            text=("Gastos públicos e privados com saúde praticamente dobraram desde 2000"),
            x=0.5,
            xanchor="center",
        ),

        annotations=[
            # Crescimento Governo
            dict(
                x=ano_max, y=df["governo"].iloc[-1],
                text=f"<b>+{cresc_gov:.0f}%</b>",
                xanchor="left", xshift=8,
                showarrow=False,
                font=dict(color=COR_GOV, size=12),
            ),
            # Crescimento Privado
            dict(
                x=ano_max, y=df["privado"].iloc[-1],
                text=f"<b>+{cresc_priv:.0f}%</b>",
                xanchor="left", xshift=8,
                showarrow=False,
                font=dict(color=COR_PRIV, size=12),
            ),
            # Rodapé esquerdo
            dict(
                text="Fonte: WHO Global Health Expenditure Database. Elaboração própria.",
                xref="paper", yref="paper",
                x=0, y=-0.12,
                xanchor="left",
                showarrow=False,
                font=dict(size=9),
            ),
            # Rodapé direito
            dict(
                text="Nota: Valores em US$ constantes de 2023.",
                xref="paper", yref="paper",
                x=1, y=-0.12,
                xanchor="right",
                showarrow=False,
                font=dict(size=9),
            ),
        ],

        margin=dict(b=60),

        template="plotly_white",

        hovermode="x",

        xaxis=dict(
            range=[df["year"].min() - 0.5, df["year"].max() + 2],
            tickmode="linear",
            dtick=4,
            showgrid=False,
        ),

        yaxis=dict(
            tickformat=".0f",
            ticksuffix="bi",
            tickprefix="US$ ",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.47,
        ),

        height=500,
    )

    return fig

def plot_perfil_financiamento_brasil(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df_perfil = con.sql("""
        SELECT
            year as ANO,
            SUM(CASE WHEN indicator_code = 'hf1_che' THEN value END) AS "SUS",
            SUM(CASE WHEN indicator_code = 'hf2_che' THEN value END) AS "Planos de Saúde",
            SUM(CASE WHEN indicator_code = 'hf3_che' THEN value END) AS "Desembolso Direto",
            SUM(CASE WHEN indicator_code = 'hfnec_che' THEN value END) AS "Não Identificado"
                 
        FROM silver_financing_schemes
                 
        WHERE country_name = 'Brazil'
                 
        GROUP BY year
                 
        ORDER BY year
    """).df()

    fig = go.Figure()

    for componente, cor in zip(COMPONENTES, CORES_FS):
        fig.add_trace(go.Bar(
            name=componente,
            x=df_perfil[componente],
            y=df_perfil["ANO"],
            orientation="h",
            marker_color=cor,
            text=df_perfil[componente].apply(lambda v: f"{v:.1f}%" if v > 3 else ""),
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=9),
            hovertemplate=f"<b>{componente}</b>: %{{x:.0f}}%<extra></extra>"
        ))

    fig.update_layout(
        barmode="stack",

        title=dict(
            text="SUS financia menos da metade da saúde no Brasil, e famílias ainda arcam com 26% dos gastos",
            x=0.5,
            xanchor="center",
        ),

        annotations=[
            # Rodapé esquerdo
            dict(
                text="Fonte: WHO Global Health Expenditure Database. Elaboração própria.",
                xref="paper", yref="paper",
                x=0, y=-0.12,
                xanchor="left",
                showarrow=False,
                font=dict(size=9),
            ),
            # Rodapé direito
            dict(
                text="Nota: Valores em US$ constantes de 2023.",
                xref="paper", yref="paper",
                x=1, y=-0.12,
                xanchor="right",
                showarrow=False,
                font=dict(size=9),
            ),
        ],

        xaxis=dict(
            showticklabels=False,
            showgrid=False,
            range=[0, 100]
        ),

        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            tickmode="linear",
            dtick=2
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            traceorder="normal"
        ),

        template="plotly_white",
        hovermode="y unified",
        hoverlabel=dict(
                font_size=13,
                namelength=-1,  # -1 = sem limite de caracteres no nome da série
            ),
        margin=dict(b=60),
        height=700,
    )

    return fig

def plot_gasto_pc_brics(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df_brics_pc = con.sql("""
        SELECT
            year,
            CASE country_name
                WHEN 'Brazil'             THEN 'Brasil'
                WHEN 'China'              THEN 'China'
                WHEN 'India'              THEN 'Índia'
                WHEN 'Russian Federation' THEN 'Rússia'
                WHEN 'South Africa'       THEN 'África do Sul'
            END AS pais,
            gasto_per_capita / 1000000000.0 AS value_bi
        FROM gold_health_spending_per_capita
        WHERE country_name IN ('Brazil','China','India','Russian Federation','South Africa')
            AND indicator_code = 'che_usd2023'
        ORDER BY year
    """).df()

    ano_min = df_brics_pc["year"].min()
    ano_max = df_brics_pc["year"].max()

    # ── 1. Calcula valores finais de todos os países ──────────
    valores_finais = {}
    for pais in PAISES_ORDEM:
        df_pais = df_brics_pc[df_brics_pc["pais"] == pais]
        if df_pais.empty:
            continue
        valores_finais[pais] = df_pais["value_bi"].iloc[-1]

    # ── 2. Calcula annotations com offset anti-sobreposição ───
    OFFSET_MIN = 25

    paises_ordenados = sorted(valores_finais, key=lambda p: valores_finais[p])
    posicoes_usadas  = []
    annotations_crescimento = []

    for pais in paises_ordenados:
        df_pais = df_brics_pc[df_brics_pc["pais"] == pais]

        y_ini   = df_pais["value_bi"].iloc[0]
        y_fim   = valores_finais[pais]

        cresc   = (y_fim / y_ini - 1) * 100

        y_ajustado = y_fim

        tentativa = 0
        while any(abs(y_ajustado - y) < OFFSET_MIN for y in posicoes_usadas):

            tentativa += 1

            direcao = 1 if tentativa % 2 else -1

            y_ajustado = y_fim + direcao * OFFSET_MIN * tentativa

        posicoes_usadas.append(y_ajustado)

        annotations_crescimento.append(dict(
            x=ano_max,
            y=y_ajustado,
            text=f"<b>+{cresc:.0f}%</b>",
            xanchor="left", 
            xshift=8,
            showarrow=False,
            font=dict(color=CORES_BRICS[pais], size=11),
        ))

    # ── 3. Adiciona traces ────────────────────────────────────
    fig = go.Figure()

    for pais in PAISES_ORDEM:
        df_pais = df_brics_pc[df_brics_pc["pais"] == pais]
        if df_pais.empty:
            continue

        fig.add_trace(go.Scatter(
            x=df_pais["year"],
            y=df_pais["value_bi"],
            name=pais,
            mode="lines+markers",
            line=dict(color=CORES_BRICS[pais], width=2),
            marker=dict(color=CORES_BRICS[pais]),
            hovertemplate=f"<b>{pais}</b>: US$ %{{y:.0f}}<extra></extra>",
        ))

    fig.update_layout(

        title=dict(
            text="Brasil lidera gasto per capita em saúde no BRICS durante quase toda a série histórica",
            x=0.5,
            xanchor="center",
        ),

        annotations=annotations_crescimento + [
            dict(
                text="Fonte: WHO Global Health Expenditure Database. Elaboração própria.",
                xref="paper", yref="paper",
                x=0, y=-0.12,
                xanchor="left",
                showarrow=False,
                font=dict(size=9)
            ),
            dict(
                text="Nota: Valores em US$ constantes de 2023.",
                xref="paper", yref="paper",
                x=1, y=-0.12,
                xanchor="right",
                showarrow=False,
                font=dict(size=9)
            ),
        ],

        xaxis=dict(
            range=[ano_min - 0.5, ano_max + 1],
            tickmode="linear",
            dtick=4,
            showgrid=False,
        ),

        yaxis=dict(
            tickformat=".0f",
            tickprefix="US$ ",
            ticksuffix="bi",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
        ),

        template="plotly_white",
        hovermode="x unified",
        hoverlabel=dict(font_size=13, namelength=-1),
        margin=dict(b=60, r=120),
        height=500,
    )

    return fig