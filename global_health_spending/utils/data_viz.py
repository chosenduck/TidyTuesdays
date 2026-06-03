import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.constants import (
    COR_LINHA, COR_GOV, COR_OUT, COR_PREV, COR_PRIV, COR_NAO, COR_DESEMB, COR_RAZAO, COR_REAT, COR_REC, CORES,
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
                value / 1e9 AS value_bi

            FROM silver_health_spending
                     
            WHERE country_name = 'Brazil'
                AND indicator_code = 'che_usd2023'
                     
            ORDER BY year
        """).df()
    
    cresc = (df_abs["value_bi"].iloc[-1] / df_abs["value_bi"].iloc[0] - 1) * 100
    ano_min = df_abs["year"].min()
    ano_max = df_abs["year"].max()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_abs["year"],
        y=df_abs["value_bi"],
        name="Gasto Total",
        mode="lines+markers",
        line=dict(color=COR_LINHA, width=3),
        marker=dict(color=COR_LINHA)
    ))

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
                font=dict(color=COR_LINHA, size=15),
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
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="x unified",
        hoverlabel=dict(font_size=13, namelength=-1),
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
                line=dict(width=1, color=cor),
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
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="x unified",
        hoverlabel=dict(font_size=13, namelength=-1),
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

    COMPONENTES = [
        ("governo", "Público", COR_GOV),
        ("privado", "Privado", COR_PRIV)
        ]
    
    for col, nome, cor in COMPONENTES:

        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df[col],
                name=nome,
                mode="lines+markers",
                line=dict(color=cor, width=3),
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

        xaxis=dict(
            range=[df["year"].min() - 0.5, df["year"].max() + 1.5],
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
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="x unified",
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
        ("planos", "Seguros e Planos Privados", COR_PRIV),
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
                "O crescimento dos seguros e planos privados impulsionaram o financiamento privado por duas décadas,"
                #"<br>"
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
            range=[ano_min - 0.3, ano_max + 0.3],
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

        height=500,
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="x unified",
        hoverlabel=dict(font_size=13, namelength=-1),
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
                line=dict(width=0.5, color=cor),
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
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="x unified",
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

        height=500,
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="closest",
        hoverlabel=dict(font_size=13, namelength=-1),

    )

    return fig

def plot_gasto_pc_comparativo(con: duckdb.DuckDBPyConnection, grupo: str = "BRICS") -> go.Figure:
    
    if grupo == "BRICS":
        paises = PAISES_BRICS
        paises_ordem = BRICS_ORDEM
        titulo = ("China e Rússia convergem rapidamente para o patamar brasileiro, "
        "<br>"
        "ameaçando a liderança histórica") 

    elif grupo == "Sistemas Universais": 
        paises = PAISES_UNIVERSAL
        paises_ordem = UNIVERSAL_ORDEM
        titulo = ("Mesmo após duas décadas de expansão, "
        "<br>"
        "o gasto per capita brasileiro segue abaixo dos pares universais") 
    
    else: 
        raise ValueError("Grupo deve ser 'BRICS' ou 'Sistemas Universais'.")

    paises_sql = "', '".join(paises)

    query = f""" 
        SELECT 
            year, 
            country_name, 
            gasto_per_capita / 1e9 AS valor 
            
        FROM gold_health_spending_per_capita 
        
        WHERE country_name IN ('{paises_sql}') AND 
            indicator_code = 'che_usd2023' 
        
        ORDER BY year 
    """

    df = con.sql(query).df()
    df["pais"] = df["country_name"].map(NOMES_PAISES)

    ano_min = df["year"].min()
    ano_max = df["year"].max()

    def valor_final_pais(pais):
        d = df[df["pais"] == pais]
        return d["valor"].iloc[-1] if not d.empty else 0

    paises_ordem = sorted(paises_ordem, key=valor_final_pais, reverse=True)

    fig = go.Figure()

    annotations = []
    dados_anotacao = []

    for pais in paises_ordem: 
        df_pais = df[df["pais"] == pais].sort_values("year")
        
        if df_pais.empty: 
            continue 
        
        destaque = pais == "Brasil" 

        valor_inicial = df_pais["valor"].iloc[0]
        valor_final   = df_pais["valor"].iloc[-1]

        if valor_inicial and valor_inicial != 0:
            crescimento = ((valor_final / valor_inicial) - 1) * 100
            sinal = "+" if crescimento >= 0 else ""
            txt_cresc = f"{sinal}{crescimento:.0f}%"
        else:
            txt_cresc = "—"
        
        fig.add_trace( 
            go.Scatter( 
                x=df_pais["year"], 
                y=df_pais["valor"], 
                name=pais, 
                mode="lines+markers", 
                line=dict( 
                    color=CORES[pais], 
                    width=3 if destaque else 2,
                ), 
                opacity=1 if destaque else 0.55,
            ) 
        ) 

        dados_anotacao.append({
            "pais":       pais,
            "y_real":     valor_final,
            "texto":      txt_cresc,
        })

    OFFSET_MIN = 35 

    dados_anotacao.sort(key=lambda d: d["y_real"]) 

    posicoes_usadas = []
    for item in dados_anotacao:
        y_ajustado = item["y_real"]
        tentativa  = 0

        while any(abs(y_ajustado - y) < OFFSET_MIN for y in posicoes_usadas):
            tentativa += 1
            direcao    = 1 if tentativa % 2 == 0 else -1
            y_ajustado = item["y_real"] + direcao * OFFSET_MIN * tentativa

        posicoes_usadas.append(y_ajustado)

        annotations.append(
            dict(
                x=ano_max,
                y=y_ajustado,
                text=item["texto"],
                xanchor="left",
                xshift=8,
                yanchor="middle",
                showarrow=False,
                font=dict(
                    size=10,
                    color=CORES[item["pais"]],
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

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
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
            range=[ano_min - 0.5, ano_max + 1], 
            tickmode="linear", 
            dtick=4, 
            showgrid=False, 
        ), 
        
        yaxis=dict( 
            tickprefix="US$ ", 
            tickformat=".0f", 
            showgrid=True,
            gridcolor="rgba(255,255,255,0.08)",
        ), 
        
        height=500,
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="x unified", 
        hoverlabel=dict(font_size=13, namelength=-1), 
        showlegend=True, 
    ) 
    
    return fig

def plot_perfil_financiamento(con: duckdb.DuckDBPyConnection, grupo: str = "BRICS") -> go.Figure: 
    
    if grupo == "BRICS":
        paises = PAISES_BRICS 
        titulo = ("Em 2023, a Rússia assume a liderança do BRICS com financiamento majoritariamente público, "
        "<br>"
        "enquanto o Brasil mantém maior dependência do setor privado") 
    
    elif grupo == "Sistemas Universais": 
        paises = PAISES_UNIVERSAL 
        titulo = ("Países com sistemas universais concentram o financiamento da saúde no setor público "
        "<br>"
        "— o Brasil é exceção") 
    
    else: 
        raise ValueError("Grupo deve ser 'BRICS' ou 'Sistemas Universais'.") 
    
    paises_sql = "', '".join(paises)

    query = f""" 
    WITH ultimo_ano AS ( 
   
        SELECT MAX(year) AS ano 
    
        FROM silver_financing_schemes 
    ) 
    
    SELECT 
        country_name, 
        indicator_code,
        tipo_indicador, 
        value 
    
    FROM 
        silver_financing_schemes 
    
    WHERE 
        country_name IN ('{paises_sql}') AND 
        tipo_indicador = 'PCT' AND 
        year = ( SELECT ano FROM ultimo_ano ) 
        
    """ 
    df = con.sql(query).df() 
    df["pais"] = df["country_name"].map(NOMES_PAISES) 

    indicadores = { 
        "hf1_che":   "Governo",
        "hf2_che":   "Seguros e Planos Privados",
        "hf3_che":   "Desembolso Direto",
        "hf4_che":   "Outros",
        "hfnec_che": "Outros",
    } 

    df["componente"] = df["indicator_code"].map(indicadores)

    df_plot = (
        df.groupby(["pais", "componente"], as_index=False)["value"]
        .sum()
    )

    cores = { 
        "Governo": COR_GOV, 
        "Seguros e Planos Privados": COR_PRIV, 
        "Desembolso Direto": COR_DESEMB,
        "Outros": COR_NAO, 
    } 

    ordem_componentes = [
        "Governo", 
        "Seguros e Planos Privados", 
        "Desembolso Direto",
        "Outros",
    ] 

    ordem_paises = ( 
        df_plot[df_plot["componente"] == "Governo"]
        .sort_values("value", ascending=False)
        ["pais"]
        .tolist()
    ) 

    fig = go.Figure() 
    
    for componente in ordem_componentes: 
        df_comp = ( 
            df_plot[df_plot["componente"] == componente] 
            .set_index("pais") 
            .reindex(ordem_paises) 
            .reset_index() 
        ) 

        fig.add_trace(
            go.Bar(
                y=df_comp["pais"],
                x=df_comp["value"],
                name=componente,
                orientation="h",
                marker=dict(
                    color=cores.get(componente, "#cccccc")
                ),
                text=[
                    f"{v:.0f}%"
                    if (v is not None and not pd.isna(v) and v >= 12)
                    else ""
                    for v in df_comp["value"]
                ],
                textposition="inside",
                insidetextanchor="middle",
                hovertemplate=(
                    f"{componente}: " + "%{x:.1f}%"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout( 
        title=dict( 
            text=titulo, 
            x=0.5, 
            y=0.94,
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
            y=1, 
            xanchor="center", 
            x=0.5, 
        ),

        annotations=[ 
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023."
                    "<br>"
                    "Composição do financiamento da saúde no último ano disponível (2023)."
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

        height=500,
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="y unified", 
        hoverlabel=dict(font_size=13, namelength=-1), 
        showlegend=True, 
    ) 
    
    return fig

def plot_prevencao_vs_reacao(con: duckdb.DuckDBPyConnection) -> go.Figure:

    paises = list(set(PAISES_BRICS + PAISES_UNIVERSAL))
    paises_sql = "', '".join(paises)

    query = f"""
        SELECT
            country_name,
            razao_hc1_hc6 AS hc1_hc6_ratio

        FROM gold_hc1_hc6_ratio

        WHERE country_name IN ('{paises_sql}')
            AND year = 2022
    """

    df = con.sql(query).df()

    df["pais"] = df["country_name"].map(NOMES_PAISES)

    df = df.sort_values("hc1_hc6_ratio", ascending=True)

    media_universais = float(
        df[df["country_name"].isin(PAISES_UNIVERSAL)]
        ["hc1_hc6_ratio"]
        .mean()
    )

    fig = go.Figure()

    for _, row in df.iterrows():

        pais = row["pais"]
        valor = row["hc1_hc6_ratio"]

        destaque = pais == "Brasil"

        fig.add_shape(
            type="line",
            x0=0,
            x1=valor,
            y0=pais,
            y1=pais,
            line=dict(color=CORES[pais], width=2)
        )

        fig.add_trace(
            go.Scatter(
                x=[valor],
                y=[pais],
                mode="markers+text",
                text=[f"{valor:.1f}x"],
                textposition="middle right",
                marker=dict(
                    size=14 if destaque else 10,
                    color=CORES[pais],
                ),
                showlegend=False,
                hovertemplate=(
                    f"<b>{pais}</b><br>"
                    "Razão: %{x:.1f}x"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=dict(
            text=("Brasil apresenta razão preventivo-reativa inferior à média dos sistemas universais"),
            x=0.5,
            xanchor="center",
            font=dict(size=18),
        ),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
        ),

        yaxis=dict(title=""),

        annotations=[
            # Rodapé
            dict(
                text=(
                    "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
                    "<br>"
                    "Nota: Valores em US$ constantes de 2023."
                    "<br>"
                    "Razão calculada para o último ano em comum disponível para esses países (2022)."
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

        height=500,
        margin=dict(t=90, b=70, r=20, l=20),
        template="plotly_white",
        hovermode="y unified", 
        hoverlabel=dict(font_size=13, namelength=-1), 
        showlegend=True, 
    )

    fig.add_vline(
        x=media_universais,
        line_dash="dash",
        line_color=COR_RAZAO,
        line_width=2,
        annotation_text=f"Média: {media_universais:.1f}x",
        annotation_position="top right",
        annotation_font_color=COR_RAZAO,
        annotation_font_size=14,
    )

    return fig