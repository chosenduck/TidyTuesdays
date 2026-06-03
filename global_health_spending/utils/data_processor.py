import pandas as pd
from utils.constants import (
    PAISES_BRICS, PAISES_UNIVERSAL, NOMES_PAISES,
    INDICADORES_HS_PCT, INDICADORES_HS_ABS,
    INDICADORES_FS_PCT, INDICADORES_FS_ABS,
    INDICADORES_SP_PCT, INDICADORES_SP_ABS,
    MAPA_GRUPAMENTO,
)

# ─── Auxiliares ───────────────────────────────────────────────
def traduzir_paises(df: pd.DataFrame, coluna: str = "country_name") -> pd.DataFrame:
    df = df.copy()
    df[coluna] = df[coluna].replace(NOMES_PAISES)
    return df


def para_bilhoes(df: pd.DataFrame, colunas: list) -> pd.DataFrame:
    df = df.copy()
    for col in colunas:
        if col in df.columns:
            df[col] = df[col] / 1_000_000_000
    return df


def preparar_pct_pivot(df: pd.DataFrame, indicadores: list, renomear: dict) -> pd.DataFrame:
    return (
        df[df["indicator_code"].isin(indicadores)]
        .pivot(index="year", columns="indicator_code", values="value")
        .reset_index()
        .rename(columns=renomear)
    )

# ─── Health Spending ──────────────────────────────────────────
def preparar_hs(health_spending: pd.DataFrame, lista_paises: list = None) -> pd.DataFrame:
    mask = health_spending["indicator_code"].isin(INDICADORES_HS_PCT + INDICADORES_HS_ABS)
    if lista_paises:
        mask &= health_spending["country_name"].isin(lista_paises)
    return health_spending[mask].copy()


# ─── Financing Schemes ────────────────────────────────────────
def preparar_fs(financing_schemes: pd.DataFrame, lista_paises: list = None) -> pd.DataFrame:
    mask = financing_schemes["indicator_code"].isin(INDICADORES_FS_PCT + INDICADORES_FS_ABS)
    if lista_paises:
        mask &= financing_schemes["country_name"].isin(lista_paises)
    return financing_schemes[mask].copy()


# ─── Spending Purpose ─────────────────────────────────────────
def adicionar_grupamento(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["grupo"] = (
        df["indicator_code"]
        .str.extract(r"^(hc\d+)", expand=False)
        .map(MAPA_GRUPAMENTO)
    )
    return df


def preparar_sp(spending_purpose: pd.DataFrame, lista_paises: list = None) -> pd.DataFrame:
    mask = spending_purpose["indicator_code"].isin(INDICADORES_SP_PCT + INDICADORES_SP_ABS)
    if lista_paises:
        mask &= spending_purpose["country_name"].isin(lista_paises)
    return spending_purpose[mask].copy().pipe(adicionar_grupamento)


def calcular_pct_grupo(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df[df["indicator_code"].isin(INDICADORES_SP_ABS)]
        .groupby(["year", "grupo"])["value"]
        .sum()
        .reset_index()
    )
    g["pct"] = g.groupby("year")["value"].transform(lambda x: x / x.sum() * 100)
    return g


def anos_comuns(df: pd.DataFrame, lista_paises: list) -> list:
    contagem = (
        df[df["country_name"].isin(lista_paises)]
        .groupby("year")["country_name"]
        .nunique()
    )
    return contagem[contagem == len(lista_paises)].index.tolist()