import duckdb

from typing import Iterable

from utils.constants import (PAISES_BRICS, PAISES_UNIVERSAL, MAPA_GRUPAMENTO)

# AUX
def _sql_lista(valores: Iterable[str]) -> str:
    """
    Converte iterável Python em lista SQL segura.

    Ex:
        ("Brazil", "China")  ->   'Brazil', 'China'
    """

    return ", ".join(f"'{v}'" for v in valores)

# CAMADA SILVER
def criar_camadas_silver(con: duckdb.DuckDBPyConnection) -> None:
    """
    Cria views padronizadas e limpas.
    """
    # HEALTH SPENDING
    con.execute("""
        CREATE OR REPLACE VIEW silver_health_spending AS
        SELECT
            country_name,
            year,
            indicator_code,
            expenditure_type AS indicator_name,
            value,

            CASE
                WHEN indicator_code LIKE '%_usd2023'
                    THEN 'ABS'

                WHEN indicator_code LIKE '%_che'
                    THEN 'PCT'

                ELSE 'OUTROS'
            END AS tipo_indicador

        FROM health_spending
        WHERE value IS NOT NULL
    """)

    # FINANCING SCHEMES
    con.execute("""
        CREATE OR REPLACE VIEW silver_financing_schemes AS
        SELECT
            country_name,
            year,
            indicator_code,
            financing_scheme AS indicator_name,
            value,

            CASE
                WHEN indicator_code LIKE '%_usd2023'
                    THEN 'ABS'

                WHEN indicator_code LIKE '%_che'
                    THEN 'PCT'

                ELSE 'OUTROS'
            END AS tipo_indicador

        FROM financing_schemes
        WHERE value IS NOT NULL
    """)

    # SPENDING PURPOSE
    case_grupo = "\n".join([
        f"""
        WHEN regexp_extract(lower(indicator_code), '^(hc[0-9]+)', 1) = '{k}'
            THEN '{v}'
        """
        for k, v in MAPA_GRUPAMENTO.items()
    ])

    con.execute(f"""
        CREATE OR REPLACE VIEW silver_spending_purpose AS
        SELECT
            country_name,
            year,
            indicator_code,
            "spending_purpose" AS indicator_name,
            value,

            regexp_extract(
                lower(indicator_code),
                '^(hc[0-9]+)',
                1
            ) AS hc_grupo,

            CASE
                {case_grupo}
                ELSE 'Outros'
            END AS grupo,

            CASE
                WHEN indicator_code LIKE '%_usd2023'
                    THEN 'ABS'

                WHEN indicator_code LIKE '%_che'
                    THEN 'PCT'

                ELSE 'OUTROS'
            END AS tipo_indicador

        FROM spending_purpose
        WHERE value IS NOT NULL
    """)

    # POPULATION
    con.execute("""
        CREATE OR REPLACE VIEW silver_population_clean AS
        SELECT
            Country AS country_name,

            CAST(Year AS INTEGER) AS year,

            CAST("SP.POP.TOTL" AS DOUBLE) AS population

        FROM population

        WHERE "SP.POP.TOTL" IS NOT NULL
    """)

# CAMADA GOLD
def criar_camadas_gold(con: duckdb.DuckDBPyConnection) -> None:
    """
    Cria views analíticas finais.
    """
    brics_sql = _sql_lista(PAISES_BRICS)
    universal_sql = _sql_lista(PAISES_UNIVERSAL)

    # HEALTH SPENDING + POPULAÇÃO
    con.execute("""
        CREATE OR REPLACE VIEW gold_health_spending_per_capita AS
        SELECT
            hs.country_name,
            hs.year,
            hs.indicator_code,
            hs.indicator_name,
            hs.value,
            pop.population,

            (hs.value * 1000000000.0) / pop.population
                AS gasto_per_capita

        FROM silver_health_spending hs

        LEFT JOIN silver_population_clean pop
            ON hs.country_name = pop.country_name
            AND hs.year = pop.year

        WHERE hs.tipo_indicador = 'ABS'
    """)

    # BRICS
    con.execute(f"""
        CREATE OR REPLACE VIEW gold_brics_health_spending AS
        SELECT *
        FROM gold_health_spending_per_capita
        WHERE country_name IN ({brics_sql})
    """)

    # UNIVERSAL
    con.execute(f"""
        CREATE OR REPLACE VIEW gold_universal_health_spending AS
        SELECT *
        FROM gold_health_spending_per_capita
        WHERE country_name IN ({universal_sql})
    """)

    # PERFIL PREVENTIVO VS REATIVO
    con.execute("""
        CREATE OR REPLACE VIEW gold_spending_profile AS
        SELECT
            country_name,
            year,
            grupo,
            SUM(value) AS total

        FROM silver_spending_purpose

        WHERE tipo_indicador = 'ABS'

        GROUP BY
            country_name,
            year,
            grupo
    """)

    # RAZÃO HC1 / HC6
    con.execute("""
        CREATE OR REPLACE VIEW gold_hc1_hc6_ratio AS

        WITH base AS (

            SELECT
                country_name,
                year,

                SUM(
                    CASE
                        WHEN hc_grupo = 'hc1'
                            THEN value
                        ELSE 0
                    END
                ) AS hc1,

                SUM(
                    CASE
                        WHEN hc_grupo = 'hc6'
                            THEN value
                        ELSE 0
                    END
                ) AS hc6

            FROM silver_spending_purpose

            WHERE tipo_indicador = 'ABS'

            GROUP BY
                country_name,
                year
        )

        SELECT
            country_name,
            year,
            hc1,
            hc6,

            CASE
                WHEN hc6 = 0
                    THEN NULL

                ELSE hc1 / hc6
            END AS razao_hc1_hc6

        FROM base
    """)


# PIPELINE
def executar_transformacoes(con: duckdb.DuckDBPyConnection) -> None:
    """
    Executa pipeline completo de transformação.
    """
    criar_camadas_silver(con)
    criar_camadas_gold(con)