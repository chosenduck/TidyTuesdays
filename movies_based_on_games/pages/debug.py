import streamlit as st
import pandas as pd
from utils.data_loader import carregar_conexao
from utils.data_transformer import carregar_silver

# CARREGAR DADOS
con = carregar_conexao()

df = con.sql("""
    SELECT *
    FROM game_films
""").df()

st.write("Shape:", df.shape)
st.dataframe(df)

with st.expander("Informações das colunas"):
    tipos = (
        df.dtypes
        .astype(str)
        .reset_index()
        .rename(columns={"index": "coluna", 0: "tipo"})
    )

    st.dataframe(tipos)

with st.expander("Valores nulos"):
    nulos = df.isnull().sum().reset_index().rename(columns={"index": "coluna", 0: "nulos"})
    nulos["%"] = (nulos["nulos"] / len(df) * 100).round(2)
    st.dataframe(nulos)

with st.expander("Valores por Coluna"):
    for col in df.select_dtypes(include=['object', 'string', 'int64']).columns:
        st.markdown(f"**Coluna: {col}**")
        st.dataframe(df[col].value_counts(dropna=False))
        st.divider()

with st.expander("Estatísticas descritivas"):
    st.dataframe(df.describe())

with st.expander("Duplicatas"):
    st.write(f"Linhas duplicadas: {df.duplicated().sum()}")
    st.dataframe(df[df.duplicated(keep=False)])

with st.expander("Cardinalidade"):
    card = df.nunique().reset_index().rename(columns={"index": "coluna", 0: "únicos"})
    card["% únicos"] = (card["únicos"] / len(df) * 100).round(2)
    st.dataframe(card)


# CARREGAR DADOS
with st.expander("Camada Silver — transformações aplicadas"):
 
    df_silver = carregar_silver(con)
 
    # --- Shape antes / depois ---
    st.markdown("#### Shape")
    col1, col2, col3 = st.columns(3)
    col1.metric("Linhas bronze", df.shape[0])
    col2.metric("Linhas silver", df_silver.shape[0],
                delta=df_silver.shape[0] - df.shape[0])
    col3.metric("Colunas novas",
                df_silver.shape[1] - df.shape[1])
 
    st.divider()

    st.markdown("#### Entradas removidas pelo filtro")
    removidos = df[~df.index.isin(df_silver.index)] if False else (
        df.assign(release_year_tmp=pd.to_datetime(df["release_date"], errors="coerce").dt.year)
        .pipe(lambda d: d[
            d["release_year_tmp"].isna() |
            (d["release_year_tmp"] > pd.Timestamp.now().year) |
            d["title"].str.startswith("Untitled", na=False)
        ])[["title", "release_date"]]
        .reset_index(drop=True)
    )
    st.dataframe(removidos)
 
    # --- Colunas novas no Silver ---
    colunas_novas = [c for c in df_silver.columns if c not in df.columns]
    st.markdown("#### Colunas adicionadas")
    st.write(colunas_novas)
 
    st.divider()
 
    # --- Comparativo de nulos: bronze vs silver ---
    st.markdown("#### Nulos: bronze vs silver")
 
    nulos_bronze = df.isnull().sum().rename("bronze")
    nulos_silver = df_silver.isnull().sum().rename("silver")

    comparativo = (
        nulos_bronze.to_frame()
        .join(nulos_silver, how="outer")
        .assign(delta=lambda x: x["silver"] - x["bronze"])
        .reset_index()
        .rename(columns={"index": "coluna"})
    )

    st.dataframe(
        comparativo.style.map(
            lambda v: "color: green" if isinstance(v, (int, float)) and v < 0 else "",
            subset=["delta"],
        )
    )
 
    st.divider()
 
    # --- Tipos: bronze vs silver ---
    st.markdown("#### Tipos: bronze vs silver")
    tipos_bronze = df.dtypes.astype(str).rename("bronze")
    tipos_silver = df_silver.dtypes.astype(str).rename("silver")

    comparativo_tipos = (
        tipos_bronze.to_frame()
        .join(tipos_silver, how="outer")
        .reset_index()
        .rename(columns={"index": "coluna"})
    )

    st.dataframe(comparativo_tipos)
    st.divider()
 
    # --- Amostra do Silver ---
    st.markdown("#### Amostra do Silver (10 linhas)")
    st.dataframe(df_silver.head(10))

with st.expander("🔍 Filmes sem pôster"):
    tabelas = con.sql("SHOW TABLES").df()["name"].tolist()
    if "game_films_silver" not in tabelas:
        st.info("Tabela silver ainda não gerada. Rode poster.py primeiro.")
    else:
        df_silver = con.sql("SELECT * FROM game_films_silver").df()
        sem_poster = df_silver[df_silver["poster_url"].isna()][
            ["title", "release_year"]
        ].reset_index(drop=True)

        st.metric("Total sem pôster", len(sem_poster))
        st.dataframe(sem_poster, width='stretch')

with st.expander("🎬 KPI records — poster_url"):
    df_silver = carregar_silver(con)
    from utils.data_transformer import _gold_kpis
    kpis = _gold_kpis(df_silver)
    records = pd.DataFrame([
        kpis["maior_bilheteria"],
        kpis["maior_rt"],
        kpis["pior_rt"],
    ])
    st.dataframe(records[["title", "release_year", "poster_url"]])

with st.expander("🍅 Extremos de Rotten Tomatoes"):
    df_silver = carregar_silver(con)
    df_rt = df_silver[df_silver["rotten_tomatoes"].notna()][["title", "release_year", "rotten_tomatoes", "poster_url"]].copy()

    st.markdown("#### Melhores")
    top = df_rt.sort_values("rotten_tomatoes", ascending=False)
    # todos com 100, mais o primeiro abaixo
    corte_top = top[top["rotten_tomatoes"] < 100]["rotten_tomatoes"].iloc[0]
    st.dataframe(top[top["rotten_tomatoes"] >= corte_top].reset_index(drop=True))

    st.markdown("#### Piores")
    bot = df_rt.sort_values("rotten_tomatoes")
    # todos com 0 (ou sem nota numérica), mais o primeiro acima de zero
    corte_bot = bot[bot["rotten_tomatoes"] > 0]["rotten_tomatoes"].iloc[0]
    st.dataframe(bot[bot["rotten_tomatoes"] <= corte_bot].reset_index(drop=True))