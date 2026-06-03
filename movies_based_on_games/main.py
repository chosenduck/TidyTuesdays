import streamlit as st

# CONFIGURAÇÃO DA PÁGINA
# Configurando Aba
st.set_page_config(
    page_title="Do Console pro Cinema",
    page_icon="🎮",
    layout="wide"
)

# Navegação
pg = st.navigation([
    st.Page("pages/home.py", title="Home"),
    st.Page("pages/debug.py", title="Debug")
])

pg.run()