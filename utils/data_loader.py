from pathlib import Path
from typing import Union

import duckdb
import pandas as pd
import streamlit as st

from utils.constants import ARQUIVOS, CACHE_DIR, DB_DIR

def _garantir_parquet(nome: str, fonte: Union[str, pd.DataFrame]) -> Path:
    """
    Garante que o dataset exista localmente em parquet.
    
    Fluxo:
    - Se o parquet existir, reutiliza.
    - Caso contrário:
        - baixa o CSV
        - salva como parquet
    """

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    caminho_parquet = CACHE_DIR / f"{nome}.parquet"

    if caminho_parquet.exists():
        return caminho_parquet

    try:
        if isinstance(fonte, str):
            df = pd.read_csv(fonte)
        elif isinstance(fonte, pd.DataFrame):
            df = fonte.copy()
        else:
            raise TypeError(
                f"Tipo inválido para '{nome}': {type(fonte)}"
            )
    except Exception as e:
        raise RuntimeError(
            f"Erro ao baixar dataset '{nome}': {e}"
        )

    df.to_parquet(caminho_parquet, index=False)

    return caminho_parquet


@st.cache_resource(show_spinner=False)
def carregar_conexao() -> duckdb.DuckDBPyConnection:
    """
    Cria e retorna uma conexão persistente com DuckDB.

    Responsabilidades:
    - garantir os arquivos parquet locais
    - criar conexão com banco DuckDB
    - registrar views raw apontando para os parquets

    Retorna:
        duckdb.DuckDBPyConnection
    """

    DB_DIR.mkdir(parents=True, exist_ok=True)

    db_path = DB_DIR / "ghed.duckdb"

    con = duckdb.connect(str(db_path))

    datasets = {
        "health_spending": ARQUIVOS["health_spending"],
        "financing_schemes": ARQUIVOS["financing_schemes"],
        "spending_purpose": ARQUIVOS["spending_purpose"],
        "population": ARQUIVOS["population"]
    }

    for nome, url in datasets.items():

        parquet_path = _garantir_parquet(nome, url)

        con.execute(f"""
            CREATE OR REPLACE VIEW {nome} AS
            SELECT *
            FROM read_parquet('{parquet_path.as_posix()}')
        """)

    return con