import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.constants import (
    COR_LINHA, COR_EIXOS, COR_GOV, COR_OUT, COR_PREV, COR_PRIV, COR_NAO, COR_DESEMB, COR_REAT, COR_REC, CORES_BRICS, CORES,
    PAISES_BRICS, PAISES_UNIVERSAL, BRICS_ORDEM, UNIVERSAL_ORDEM, NOMES_PAISES,
    )

def metrica_gasto_total(con: duckdb.DuckDBPyConnection) -> dict:
    """
    Gasto total em saúde no último ano disponível,
    delta percentual desde 2000 e rankings.
    """
    return con.sql("""
        WITH anos AS (
            SELECT
                year,
                value / 1e9 AS value_bi
            FROM silver_health_spending
            WHERE country_name = 'Brazil'
                AND indicator_code = 'che_usd2023'
                AND year IN (
                    SELECT MIN(year) FROM silver_health_spending
                    WHERE country_name = 'Brazil' AND indicator_code = 'che_usd2023'
                    UNION ALL
                    SELECT MAX(year) FROM silver_health_spending
                    WHERE country_name = 'Brazil' AND indicator_code = 'che_usd2023'
                )
        ),
        ranking_brics AS (
            SELECT
                country_name,
                RANK() OVER (ORDER BY value DESC) AS rank_brics
            FROM silver_health_spending
            WHERE country_name IN ('Brazil','China','India','Russian Federation','South Africa')
                AND indicator_code = 'che_usd2023'
                AND year = (SELECT MAX(year) FROM silver_health_spending WHERE indicator_code = 'che_usd2023')
        ),
        ranking_universal AS (
            SELECT
                country_name,
                RANK() OVER (ORDER BY value DESC) AS rank_universal
            FROM silver_health_spending
            WHERE country_name IN (
                    'Brazil',
                    'Australia','Canada','France','Spain',
                    'United Kingdom of Great Britain and Northern Ireland',
                    'Uruguay','Sweden','Portugal'
                )
                AND indicator_code = 'che_usd2023'
                AND year = (SELECT MAX(year) FROM silver_health_spending WHERE indicator_code = 'che_usd2023')
        )          
        SELECT
            MAX(CASE WHEN year = (SELECT MAX(year) FROM anos) THEN value_bi END) AS valor_atual,
            MIN(CASE WHEN year = (SELECT MIN(year) FROM anos) THEN value_bi END) AS valor_2000,
            (SELECT rank_brics    FROM ranking_brics    WHERE country_name = 'Brazil') AS rank_brics,
            (SELECT rank_universal FROM ranking_universal WHERE country_name = 'Brazil') AS rank_universal
        FROM anos
    """).df().iloc[0].to_dict()


def metrica_gasto_per_capita(con: duckdb.DuckDBPyConnection) -> dict:
    """
    Gasto per capita no último ano disponível,
    delta percentual desde 2000 e rankings.
    """
    return con.sql("""
        WITH anos AS (
            SELECT
                year,
                gasto_per_capita / 1e9 AS value_pc
            FROM gold_health_spending_per_capita
            WHERE country_name = 'Brazil'
                AND indicator_code = 'che_usd2023'
                AND year IN (
                    SELECT MIN(year) FROM gold_health_spending_per_capita
                    WHERE country_name = 'Brazil' AND indicator_code = 'che_usd2023'
                    UNION ALL
                    SELECT MAX(year) FROM gold_health_spending_per_capita
                    WHERE country_name = 'Brazil' AND indicator_code = 'che_usd2023'
                )
        ),
        ranking_brics AS (
            SELECT
                country_name,
                RANK() OVER (ORDER BY gasto_per_capita DESC) AS rank_brics
            FROM gold_health_spending_per_capita
            WHERE country_name IN ('Brazil','China','India','Russian Federation','South Africa')
                AND indicator_code = 'che_usd2023'
                AND year = (SELECT MAX(year) FROM gold_health_spending_per_capita WHERE indicator_code = 'che_usd2023')
        ),
        ranking_universal AS (
            SELECT
                country_name,
                RANK() OVER (ORDER BY gasto_per_capita DESC) AS rank_universal
            FROM gold_health_spending_per_capita
            WHERE country_name IN (
                    'Brazil',
                    'Australia','Canada','France','Spain',
                    'United Kingdom of Great Britain and Northern Ireland',
                    'Uruguay','Sweden','Portugal'
                )
                AND indicator_code = 'che_usd2023'
                AND year = (SELECT MAX(year) FROM gold_health_spending_per_capita WHERE indicator_code = 'che_usd2023')
        )          
        SELECT
            MAX(CASE WHEN year = (SELECT MAX(year) FROM anos) THEN value_pc END) AS valor_atual,
            MIN(CASE WHEN year = (SELECT MIN(year) FROM anos) THEN value_pc END) AS valor_2000,
            (SELECT rank_brics    FROM ranking_brics    WHERE country_name = 'Brazil') AS rank_brics,
            (SELECT rank_universal FROM ranking_universal WHERE country_name = 'Brazil') AS rank_universal
        FROM anos
    """).df().iloc[0].to_dict()


def metrica_participacao_publica(con: duckdb.DuckDBPyConnection) -> dict:
    """
    Participação pública (gghed_che) no último ano,
    delta em pontos percentuais desde 2000 e rankings.
    """
    return con.sql("""
        WITH anos AS (
            SELECT year, value
            FROM silver_health_spending
            WHERE country_name = 'Brazil'
                AND indicator_code = 'gghed_che'
                AND year IN (
                    SELECT MIN(year) FROM silver_health_spending
                    WHERE country_name = 'Brazil' AND indicator_code = 'gghed_che'
                    UNION ALL
                    SELECT MAX(year) FROM silver_health_spending
                    WHERE country_name = 'Brazil' AND indicator_code = 'gghed_che'
                )
        ),
        ranking_brics AS (
            SELECT
                country_name,
                RANK() OVER (ORDER BY value DESC) AS rank_brics
            FROM silver_health_spending
            WHERE country_name IN ('Brazil','China','India','Russian Federation','South Africa')
                AND indicator_code = 'gghed_che'
                AND year = (SELECT MAX(year) FROM silver_health_spending WHERE indicator_code = 'gghed_che')
        ),
        ranking_universal AS (
            SELECT
                country_name,
                RANK() OVER (ORDER BY value DESC) AS rank_universal
            FROM silver_health_spending
            WHERE country_name IN (
                    'Brazil','United Kingdom of Great Britain and Northern Ireland',
                    'Canada','France','Spain','Australia','Uruguay','Sweden','Portugal'
                )
                AND indicator_code = 'gghed_che'
                AND year = (SELECT MAX(year) FROM silver_health_spending WHERE indicator_code = 'gghed_che')
        )
        SELECT
            MAX(CASE WHEN year = (SELECT MAX(year) FROM anos) THEN value END) AS valor_atual,
            MIN(CASE WHEN year = (SELECT MIN(year) FROM anos) THEN value END) AS valor_2000,
            (SELECT rank_brics    FROM ranking_brics    WHERE country_name = 'Brazil') AS rank_brics,
            (SELECT rank_universal FROM ranking_universal WHERE country_name = 'Brazil')  AS rank_universal
        FROM anos
    """).df().iloc[0].to_dict()


def metrica_desembolso_direto(con: duckdb.DuckDBPyConnection) -> dict:
    """
    Desembolso direto das famílias (hf3_che) no último ano,
    delta em pontos percentuais desde 2000 e rankings 
    (quanto maior o OOP, pior — rank invertido).
    """
    return con.sql("""
        WITH anos AS (
            SELECT year, value
            FROM silver_financing_schemes
            WHERE country_name = 'Brazil'
                AND indicator_code = 'hf3_che'
                AND year IN (
                    SELECT MIN(year) FROM silver_financing_schemes
                    WHERE country_name = 'Brazil' AND indicator_code = 'hf3_che'
                    UNION ALL
                    SELECT MAX(year) FROM silver_financing_schemes
                    WHERE country_name = 'Brazil' AND indicator_code = 'hf3_che'
                )
        ),
        ranking_brics AS (
            SELECT
                country_name,
                RANK() OVER (ORDER BY value DESC) AS rank_oop_brics
            FROM silver_financing_schemes
            WHERE country_name IN ('Brazil','China','India','Russian Federation','South Africa')
                AND indicator_code = 'hf3_che'
                AND year = (SELECT MAX(year) FROM silver_financing_schemes WHERE indicator_code = 'hf3_che')
        ),
        ranking_universal AS (
            SELECT
                country_name,
                RANK() OVER (ORDER BY value DESC) AS rank__oop_universal
            FROM silver_financing_schemes
            WHERE country_name IN (
                   'Brazil','United Kingdom of Great Britain and Northern Ireland',
                    'Canada','France','Spain','Australia','Uruguay','Sweden','Portugal'
                )
                AND indicator_code = 'hf3_che'
                AND year = (SELECT MAX(year) FROM silver_financing_schemes WHERE indicator_code = 'hf3_che')
        )
        SELECT
            MAX(CASE WHEN year = (SELECT MAX(year) FROM anos) THEN value END) AS valor_atual,
            MIN(CASE WHEN year = (SELECT MIN(year) FROM anos) THEN value END) AS valor_2000,
            (SELECT rank_oop_brics FROM ranking_brics WHERE country_name = 'Brazil') AS rank_oop_brics,
            (SELECT rank__oop_universal FROM ranking_universal WHERE country_name = 'Brazil')  AS rank__oop_universal
        FROM anos
    """).df().iloc[0].to_dict()


def metrica_razao_reativo_preventivo(con: duckdb.DuckDBPyConnection) -> dict:
    """
    Razão entre gasto curativo (hc1) e preventivo (hc6) no último ano.
    Interpreta: para cada R$ 1 em prevenção, gastamos R$ X em tratamento.
    """
    return con.sql("""
        WITH ultimo_ano AS (
            SELECT MAX(year) AS ano
            FROM silver_spending_purpose
            WHERE country_name = 'Brazil'
                AND indicator_code IN ('hc1_usd2023', 'hc6_usd2023')
        ),
        valores AS (
            SELECT
                indicator_code,
                value
            FROM silver_spending_purpose
            WHERE country_name = 'Brazil'
                AND indicator_code IN ('hc1_usd2023', 'hc6_usd2023')
                AND year = (SELECT ano FROM ultimo_ano)
        )
        SELECT
            MAX(CASE WHEN indicator_code = 'hc1_usd2023' THEN value END) AS reativo,
            MAX(CASE WHEN indicator_code = 'hc6_usd2023' THEN value END) AS preventivo,
            ROUND(
                MAX(CASE WHEN indicator_code = 'hc1_usd2023' THEN value END) /
                MAX(CASE WHEN indicator_code = 'hc6_usd2023' THEN value END),
            1) AS razao
        FROM valores
    """).df().iloc[0].to_dict()

def plot_gasto_total_brasil(con: duckdb.DuckDBPyConnection) -> go.Figure:
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
        font=dict(color=COR_EIXOS, size=12),
    )

    fig.update_layout(

        title=dict(
            text="Gasto total em saúde praticamente dobrou em duas décadas",
            x=0.5,
            y=0.93,
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
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023."
                    ),
                xref="paper",
                yref="paper",

                x=0,
                y=-0.1,

                xanchor="left",
                yanchor="top",

                align="left",

                showarrow=False,

                font=dict(size=9),
                ),
        ],

        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="x",
        hoverlabel=dict(
                font_size=13,
                namelength=-1,
            ),

        xaxis=dict(
            range=[ano_min - 0.5, ano_max + 3],
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

def plot_gasto_pct_brasil(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df = con.sql("""
        SELECT
            year,

            SUM(
                CASE
                    WHEN indicator_code = 'gghed_che'
                    THEN value
                END
            ) AS publico_pct,

            SUM(
                CASE
                    WHEN indicator_code = 'pvtd_che'
                    THEN value
                END
            ) AS privado_pct

        FROM silver_health_spending

        WHERE country_name = 'Brazil'

        GROUP BY year

        ORDER BY year
    """).df()

    fig = go.Figure()

    COMPONENTES = [
        ("publico_pct", "% Público", COR_GOV),
        ("privado_pct", "% Privado", COR_PRIV)
        ]

    for col, nome, cor in COMPONENTES:

        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df[col],

                name=nome,

                mode="lines",

                line=dict(
                    width=1,
                    color=cor,
                ),

                stackgroup="one",

                groupnorm="percent",

                fill="tonexty",

                hovertemplate=(
                    f"<b>{nome}</b><br>"
                    "%{y:.1f}%"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(

        title=dict(
            text=("Mesmo com o crescimento do gasto em saúde, a divisão público-privada pouco mudou em 23 anos"),
            x=0.5,
            y=0.93,
            xanchor="center",
        ),

        annotations=[
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023."
                    ),
                xref="paper",
                yref="paper",

                x=0,
                y=-0.1,

                xanchor="left",
                yanchor="top",

                align="left",

                showarrow=False,

                font=dict(size=9),
                ),
        ],

        margin=dict(t=90, b=70, r=20, l=20),

        template="plotly_white",

        hovermode="x unified",

        hoverlabel=dict(
                font_size=13,
                namelength=-1,
            ),

        xaxis=dict(
            range=[df["year"].min() - 0.5, df["year"].max() + 0.5],
            title="",
            tickmode="linear",
            dtick=4,
            showgrid=False,
        ),

        yaxis=dict(
            range=[0, 100],
            ticksuffix="%",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="center",
            x=0.5,
        ),

        height=500,
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
        name="Público",
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
            text=("Pandemia freou o gasto privado e acelerou o público — que embora menor,"
            "<br>"
            "teve o maior crescimento da série histórica"),
            x=0.5,
            y=0.93,
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
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023."
                    ),
                xref="paper",
                yref="paper",

                x=0,
                y=-0.1,

                xanchor="left",
                yanchor="top",

                align="left",

                showarrow=False,

                font=dict(size=9),
                ),
        ],

        margin=dict(t=90, b=70, r=20, l=20),

        template="plotly_white",

        hovermode="x unified",

        xaxis=dict(
            range=[df["year"].min() - 0.5, df["year"].max() + 3],
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
            y=0.98,
            xanchor="center",
            x=0.47,
        ),

        height=500,
    )

    return fig

def plot_evolucao_financiamento_brasil(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df = con.sql("""
        SELECT
            year,
            SUM(CASE WHEN indicator_code = 'hf1_che'   THEN value END) AS sus,
            SUM(CASE WHEN indicator_code = 'hf2_che'   THEN value END) AS planos,
            SUM(CASE WHEN indicator_code = 'hf3_che'   THEN value END) AS oop,
            NULLIF(SUM(CASE WHEN indicator_code = 'hfnec_che' THEN value END), 0) AS nao_identificado        
        
        FROM silver_financing_schemes
        
        WHERE country_name = 'Brazil'
        
        GROUP BY year
        
        ORDER BY year
    """).df()

    tem_nao_identificado = df["nao_identificado"].fillna(0).gt(0).any()

    COMPONENTES = [
        ("sus", "SUS", COR_GOV),
        ("planos", "Planos de Saúde", COR_PRIV),
        ("oop", "Desembolso Direto", COR_DESEMB),
    ]
    if tem_nao_identificado:
        COMPONENTES.append(("nao_identificado", "Não Identificado", COR_NAO))

    ano_min = df["year"].min()
    ano_max = df["year"].max()

    fig = go.Figure()

    for col, nome, cor in COMPONENTES:
        valores = df[col].fillna(0)

        # Filtra anos com valor > 0 para Não Identificado
        if col == "nao_identificado":
            mask   = df[col] > 0        
            x_plot = df["year"][mask]
            y_plot = df[col][mask]
        else:
            x_plot = df["year"]
            y_plot = valores

        fig.add_trace(go.Scatter(
            x=x_plot,
            y=y_plot,
            name=nome,
            mode="lines+markers",
            line=dict(color=cor, width=2.5),
            marker=dict(color=cor),
            stackgroup=None,
            fill="tozeroy",
            opacity=0.95
        ))

    fig.update_layout(

        title=dict(
            text=(
                "O crescimento dos planos de saúde impulsionou o financiamento privado por duas décadas,"
                "<br>"
                "mas a pandemia revelou o SUS como amortecedor real do sistema"),
            x=0.5,
            xanchor="center",
        ),

        annotations=[
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023."
                    ),
                xref="paper",
                yref="paper",

                x=0,
                y=-0.1,

                xanchor="left",
                yanchor="top",

                align="left",

                showarrow=False,

                font=dict(size=9),
                ),
        ],

        xaxis=dict(
            range=[ano_min - 0.5, ano_max + 0.5],
            tickmode="linear",
            dtick=4,
            showgrid=False,
        ),

        yaxis=dict(
            tickformat=".0f",
            ticksuffix="%",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.95,
            xanchor="center",
            x=0.5,
            traceorder="normal",
        ),

        template="plotly_white",
        hovermode="x unified",
        hoverlabel=dict(font_size=13, namelength=-1),
        margin=dict(t=90, b=70, r=20, l=20),
        height=500,
    )

    return fig

def plot_evolucao_componentes(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df_destinos = con.sql("""
        SELECT 
            year,
            SUM(CASE WHEN grupo = 'Reativo' THEN value END) / 1e9 AS Reativo,
            SUM(CASE WHEN grupo = 'Preventivo' THEN value END) / 1e9 AS Preventivo,
            SUM(CASE WHEN grupo = 'Recuperativo' THEN value END) / 1e9 AS Recuperativo,
            SUM(CASE WHEN grupo = 'Outros' THEN value END) / 1e9 AS Outros
        
        FROM silver_spending_purpose
        
        WHERE country_name = 'Brazil'
        
        GROUP BY year
        
        ORDER BY year
    """).df()

    fig = go.Figure()

    COMPONENTES = [
        ("Preventivo", COR_PREV),
        ("Outros", COR_OUT),
        ("Recuperativo", COR_REC),
        ("Reativo", COR_REAT)
        ]

    for nome, cor in COMPONENTES:

        fig.add_trace(
            go.Scatter(
                x=df_destinos["year"],
                y=df_destinos[nome],

                name=nome,

                mode="lines+markers",

                line=dict(
                    width=0.5,
                    color=cor,
                ),

                stackgroup="one",

                groupnorm=None,

                fill="tonexty"

                ),
            )
    
    fig.update_layout(

        title=dict(
            text=("Mesmo após a pandemia, o crescimento do gasto em saúde"
            "<br>"
            "permaneceu concentrado em cuidados reativos"),
            x=0.5,
            y=0.93,
            xanchor="center",
        ),

        annotations=[
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023. 'Outros' inclui gastos com governança e categorias residuais da classificação da WHO."
                    ),
                xref="paper",
                yref="paper",

                x=0,
                y=-0.1,

                xanchor="left",
                yanchor="top",

                align="left",

                showarrow=False,

                font=dict(size=9),
                ),
        ],

        margin=dict(t=90, b=70, r=20, l=20),

        template="plotly_white",

        hovermode="x unified",

        xaxis=dict(
            range=[df_destinos["year"].min() - 0.15, df_destinos["year"].max() + 0.15],
            tickmode="linear",
            dtick=1,
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
            y=0.98,
            xanchor="center",
            x=0.47,
        ),

        height=500,
    )

    return fig

def plot_razao(con: duckdb.DuckDBPyConnection) -> go.Figure:
    df = con.sql("""
        SELECT *
        FROM gold_hc1_hc6_ratio
        WHERE country_name = 'Brazil'
        ORDER BY year
    """).df()
    
    ano_min = df["year"].min()
    ano_max = df["year"].max()

    fig = go.Figure()
    
    for _, row in df.iterrows():

        fig.add_trace(
            go.Scatter(
                x=[row["year"], row["year"]],
                y=[row["hc6"], row["hc1"]],
                mode="lines",
                line=dict(
                    color="rgba(120,120,120,0.45)",
                    width=2,
                ),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["hc6"],
            name="Preventivo",
            mode="markers",
            marker=dict(
                size=11,
                color=COR_PREV,
                line=dict(width=1, color="white")
            ),

            customdata=df["razao_hc1_hc6"],
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["hc1"],
            name="Reativo",
            mode="markers",
            marker=dict(
                size=13,
                color=COR_REAT,
                line=dict(width=1, color="white")
            ),

            customdata=df["razao_hc1_hc6"],
        )
    )

    annotations_razao = []

    for _, row in df.iterrows():
        annotations_razao.append(dict(
            x=row["year"],
            y=(row["hc1"] + row["hc6"]) / 2,
            text=f"<b>{row['razao_hc1_hc6']:.0f}x</b>",
            xanchor="center",
            xshift= 14,
            showarrow=False,
            font=dict(size=12, color=COR_REC),
        )
    )

    fig.update_layout(

        title=dict(
            text=("Em média, o Brasil gasta 10x mais em tratamento reativo do que em prevenção"),
            x=0.5,
            xanchor="center",
        ),

        annotations = annotations_razao + [
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023."
                    ),
                xref="paper",
                yref="paper",

                x=0,
                y=-0.1,

                xanchor="left",
                yanchor="top",

                align="left",

                showarrow=False,

                font=dict(size=9),
                ),
        ],

        template="plotly_white",

        hovermode="closest",

        hoverlabel=dict(
            font_size=13,
            namelength=-1,
        ),

        xaxis=dict(
            range=[ano_min - 0.5, ano_max + 1],
            tickmode="linear",
            dtick=2,
            showgrid=False,
        ),

        yaxis=dict(
            tickformat=".0f",
            ticksuffix=" bi",
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

        margin=dict(t=90, b=70, r=20, l=20
        ),

        height=500,
    )

    return fig

def plot_gasto_pc_comparativo(con: duckdb.DuckDBPyConnection, grupo: str = "BRICS") -> go.Figure:
    
    if grupo == "BRICS":

        paises = PAISES_BRICS

        paises_ordem = BRICS_ORDEM

        titulo = (
            "Brasil lidera gasto per capita em saúde no BRICS durante quase toda a série histórica"
        ) 

    elif grupo == "Sistemas Universais": 

        paises = PAISES_UNIVERSAL

        paises_ordem = UNIVERSAL_ORDEM

        titulo = (
            "Mesmo entre países com sistemas universais, o Brasil mantém gasto per capita inferior"
        ) 
    else: 
        raise ValueError("grupo deve ser 'BRICS' ou 'Sistemas Universais'")

    paises_sql = "', '".join(paises)

    query = f""" 
        SELECT 
            year, 
            country_name, 
            gasto_per_capita / 1e9 AS valor 
            
        FROM 
            gold_health_spending_per_capita 
        
        WHERE 
            country_name IN ('{paises_sql}') AND 
            indicator_code = 'che_usd2023' 
        
        ORDER BY 
            year 
    """
    df = con.sql(query).df()
    df["pais"] = df["country_name"].map(NOMES_PAISES)
    ano_min = df["year"].min()
    ano_max = df["year"].max()

    fig = go.Figure()

    for pais in paises_ordem: 
        
        df_pais = df[df["pais"] == pais] 
        
        if df_pais.empty: 
            continue 
        
        destaque = pais == "Brasil" 
        
        fig.add_trace( 
            go.Scatter( 
                x=df_pais["year"], 
                y=df_pais["valor"], 
                name=pais, 
                mode="lines", 
                line=dict( 
                    color=CORES[pais], 
                    width=4 if destaque else 2,
                ), 
                opacity=1 if destaque else 0.45,
            ) 
        ) 
        
    annotations = [] 

    OFFSET_MIN = 30 

    posicoes_usadas = [] 

    paises_ordenados = sorted( 
        paises_ordem, 
        key=lambda p: ( 
            df[df["pais"] == p]["valor"].iloc[-1] 
            if not df[df["pais"] == p].empty 
            else 0 ) 
    ) 
    
    for pais in paises_ordenados: 
        df_pais = df[df["pais"] == pais] 
        
        if df_pais.empty: 
            continue 
        
        valor_final = df_pais["valor"].iloc[-1] 
        
        y_ajustado = valor_final 
        
        tentativa = 0 
        
        while any( 
            abs(y_ajustado - y) < OFFSET_MIN 
            for y in posicoes_usadas 
        ): 
            tentativa += 1 
            
            direcao = 1 if tentativa % 2 else -1 
            
            y_ajustado = ( 
                valor_final + direcao * OFFSET_MIN * tentativa 
            ) 
            
        posicoes_usadas.append(y_ajustado) 
        annotations.append( 
            dict( 
                x=ano_max, 
                y=y_ajustado, 
                text=( 
                    f"<b>{pais}</b>" 
                    f" — US$ {valor_final:,.0f}" 
                ).replace(",", "."), 
                xanchor="left", 
                xshift=10, 
                showarrow=False, 
                font=dict( 
                    size=11, 
                    color=CORES[pais], 
                ), 
            ) 
        ) 
    
    fig.update_layout( 
        title=dict( 
            text=titulo, 
            x=0.5, 
            xanchor="center", 
            font=dict(size=18), 
        ), 
        annotations=annotations + [ 
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023."
                    ),
                xref="paper",
                yref="paper",

                x=0,
                y=-0.1,

                xanchor="left",
                yanchor="top",

                align="left",

                showarrow=False,

                font=dict(size=9),
                ),
        ], 
        
        xaxis=dict( 
            range=[ano_min - 0.5, ano_max + 4], 
            tickmode="linear", 
            dtick=4, 
            showgrid=False, 
        ), 
        
        yaxis=dict( 
            tickprefix="US$ ", 
            tickformat=",.0f", 
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)", 
        ), 
        
        template="plotly_white",
        hovermode="x unified", 
        hoverlabel=dict( 
            font_size=13, 
            namelength=-1, 
        ), 
        showlegend=False, 
        margin=dict(t=90, b=120, l=30, r=160), 
        height=540, 
    ) 
    
    return fig

def plot_perfil_financiamento(con: duckdb.DuckDBPyConnection, grupo: str = "brics") -> go.Figure: 
    if grupo == "brics":
        paises = PAISES_BRICS 
        titulo = ("Mesmo liderando o gasto per capita no BRICS, o financiamento brasileiro segue altamente privado") 
    elif grupo == "universais": 
        paises = PAISES_UNIVERSAL 
        titulo = ("Entre países com sistemas universais, o Brasil possui uma das menores participações públicas") 
    else: 
        raise ValueError("grupo deve ser 'brics' ou 'universais'") 
    paises_sql = "', '".join(paises)
    query = f""" 
    WITH ultimo_ano AS ( 
   
        SELECT MAX(year) AS ano 
    
        FROM silver_health_spending 
    ) 
    
    SELECT 
        country_name, 
        indicator_code, 
        value 
    
    FROM 
        silver_health_spending 
    
    WHERE 
        country_name IN ('{paises_sql}') AND 
        indicator_code IN ( 'gghed_che', 'pvtd_che', 'oop_che' ) AND 
        year = ( SELECT ano FROM ultimo_ano ) 
        
    """ 
    df = con.sql(query).df() 
    df["pais"] = df["country_name"].map(NOMES_PAISES) 
    indicadores = { 
        "gghed_che": "Público", 
        "pvtd_che": "Privado", 
        "oop_che": "Desembolso Direto", 
    } 
    df["componente"] = ( 
        df["indicator_code"] .map(indicadores) 
    ) 
    cores = { 
        "Público": COR_GOV, 
        "Privado": COR_PRIV, 
        "Desembolso Direto": COR_DESEMB, 
    } 
    ordem_componentes = [
        "Público", 
        "Privado", 
        "Desembolso Direto"
    ] 
    ordem_paises = ( 
        df[df["componente"] == "Público"]
        .sort_values("value", ascending=False) 
        ["pais"]
        .tolist() 
    ) 

    fig = go.Figure() 
    
    for componente in ordem_componentes: 
        df_comp = ( 
            df[df["componente"] == componente] 
            .set_index("pais") 
            .reindex(ordem_paises) 
            .reset_index() ) 
        fig.add_trace( 
            go.Bar( 
                y=df_comp["pais"], 
                x=df_comp["value"], 
                name=componente, 
                orientation="h",
                marker=dict( 
                    color=cores[componente] 
                ), 
                text=[ 
                    f"{v:.0f}%" 
                    if v >= 12 else "" 
                    for v in df_comp["value"] 
                ], 
                textposition="inside", 
                insidetextanchor="middle"
            ) 
        ) 
    fig.update_layout( 
        title=dict( 
            text=titulo, 
            x=0.5, 
            xanchor="center", 
            font=dict(size=18), 
        ), 
        barmode="stack", 
        xaxis=dict( 
            range=[0, 100], 
            ticksuffix="%", 
            showgrid=False, 
            zeroline=False, 
        ), 
        yaxis=dict( 
            categoryorder="array", 
            categoryarray=ordem_paises[::-1],
        ), 
        legend=dict( 
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="center", 
            x=0.5, ), 
            annotations=[ 
                dict( 
                    text=("Fonte: WHO Global Health Expenditure " "Database. Elaboração própria." ), 
                    xref="paper", 
                    yref="paper", 
                    x=-0.02, 
                    y=-0.12, 
                    xanchor="left", 
                    showarrow=False, 
                    font=dict(size=10) 
                ), 
                dict( 
                    text=( "Composição do financiamento da saúde " "no último ano disponível." ), 
                    xref="paper", 
                    yref="paper", 
                    x=1, 
                    y=-0.12, 
                    xanchor="right", 
                    showarrow=False, 
                    font=dict(size=10) 
                ), 
            ], 
            template="plotly_white", 
            hoverlabel=dict( 
                font_size=13, 
                namelength=-1, 
            ), 
            margin=dict( t=90, b=120, l=30, r=30, ), 
            height=550, 
    ) 
    
    return fig

# =========================================================
# BLOCO 3 — PREVENÇÃO VS REAÇÃO
# =========================================================

def plot_prevencao_vs_reacao(
    con: duckdb.DuckDBPyConnection
) -> go.Figure:

    # -----------------------------------------------------
    # PAÍSES
    # -----------------------------------------------------

    paises = list(
        set(PAISES_BRICS + PAISES_UNIVERSAL)
    )

    paises_sql = "', '".join(paises)


    # -----------------------------------------------------
    # QUERY
    # -----------------------------------------------------

    query = f"""
        WITH ultimo_ano AS (

            SELECT MAX(year) AS ano

            FROM gold_hc1_hc6_ratio

        )

        SELECT
            country_name,
            razao_hc1_hc6 AS hc1_hc6_ratio

        FROM gold_hc1_hc6_ratio

        WHERE country_name IN ('{paises_sql}')

            AND year = (
                SELECT ano
                FROM ultimo_ano
            )
    """

    df = con.sql(query).df()


    # -----------------------------------------------------
    # TRANSFORMAÇÕES
    # -----------------------------------------------------

    df["pais"] = (
        df["country_name"]
        .map(NOMES_PAISES)
    )

    df = df.sort_values(
        "hc1_hc6_ratio",
        ascending=True
    )

    media_universais = (

        df[
            df["country_name"]
            .isin(PAISES_UNIVERSAL)
        ]

        ["hc1_hc6_ratio"]

        .mean()
    )


    # -----------------------------------------------------
    # FIGURA
    # -----------------------------------------------------

    fig = go.Figure()


    # -----------------------------------------------------
    # LOLLIPOPS
    # -----------------------------------------------------

    for _, row in df.iterrows():

        pais = row["pais"]
        valor = row["hc1_hc6_ratio"]

        destaque = pais == "Brasil"

        # linha
        fig.add_shape(

            type="line",

            x0=0,
            x1=valor,

            y0=pais,
            y1=pais,

            line=dict(
                color=(
                    CORES_PAISES[pais]
                    if destaque
                    else "rgba(120,120,120,0.35)"
                ),
                width=2,
            )
        )

        # ponto
        fig.add_trace(

            go.Scatter(

                x=[valor],
                y=[pais],

                mode="markers+text",

                text=[
                    f"{valor:.1f}x"
                ],

                textposition="middle right",

                marker=dict(
                    size=14 if destaque else 10,

                    color=(
                        CORES_PAISES[pais]
                        if destaque
                        else "rgba(120,120,120,0.6)"
                    ),
                ),

                showlegend=False,

                hovertemplate=(
                    f"<b>{pais}</b><br>"
                    "Razão: %{x:.1f}x"
                    "<extra></extra>"
                ),
            )
        )


    # -----------------------------------------------------
    # LINHA DE REFERÊNCIA
    # -----------------------------------------------------

    fig.add_vline(

        x=media_universais,

        line_dash="dash",

        line_color="rgba(0,0,0,0.4)",

        annotation_text=(
            "Média sistemas universais"
        ),

        annotation_position="top",
    )


    # -----------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------

    fig.update_layout(

        title=dict(
            text=(
                "Países com sistemas universais "
                "investem proporcionalmente mais em prevenção"
            ),

            x=0.5,
            xanchor="center",

            font=dict(size=18),
        ),

        xaxis=dict(

            title=(
                "Razão entre gastos reativos "
                "e preventivos"
            ),

            showgrid=False,

            zeroline=False,
        ),

        yaxis=dict(
            title="",
        ),

        annotations=[

            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure "
                    "Database. Elaboração própria."
                ),

                xref="paper",
                yref="paper",

                x=-0.02,
                y=-0.12,

                xanchor="left",

                showarrow=False,

                font=dict(size=10)
            ),

            dict(
                text=(
                    "Valores maiores indicam maior "
                    "priorização de cuidados reativos."
                ),

                xref="paper",
                yref="paper",

                x=1,
                y=-0.12,

                xanchor="right",

                showarrow=False,

                font=dict(size=10)
            ),
        ],

        template="plotly_white",

        hoverlabel=dict(
            font_size=13,
            namelength=-1,
        ),

        margin=dict(
            t=90,
            b=120,
            l=30,
            r=30,
        ),

        height=600,
    )

    return fig