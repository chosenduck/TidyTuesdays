import streamlit as st

# 1. python movies_based_on_games\utils\rebuild_silver.py
# 2. python movies_based_on_games\poster.py --dry-run    
# 3. python movies_based_on_games\poster.py
# 4. streamlit run movies_based_on_games\main.py   

# CONFIGURAÇÃO DA PÁGINA
# Configurando Aba
st.set_page_config(
    page_title="Do Console pro Cinema",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Navegação
pages = [
    st.Page("pages/panorama.py", title="Panorama Geral", icon="🎥", visibility="visible"),
    st.Page("pages/franquias_e_distribuidoras.py", title="Donos da Tela", icon="🎞️", visibility="visible"),
    st.Page("pages/hall_infamia.py", title="Hall da Infâmia",  icon="💀", visibility="visible"),
    st.Page("pages/debug.py", title="Debug", icon="🛠️", visibility="hidden"),
]

pg = st.navigation(pages, position="sidebar")

with st.sidebar:
    # st.image("assets/logo.png", width=120)
    st.caption("por João Victor Fernandes") 
    st.caption("""
    <div style="display:flex; gap:15px; align-items:center;">

    <a href="https://github.com/chosenduck" target="_blank">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg"
            width="28"
                style="filter: invert(1);">
    </a>

    <a href="https://www.linkedin.com/in/jvfqvaz" target="_blank">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg"
            width="28">
    </a>

    </div>
    """, unsafe_allow_html=True)

pg.run()