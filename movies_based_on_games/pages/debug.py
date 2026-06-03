import streamlit as st
from utils.data_loader import carregar_conexao

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