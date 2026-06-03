import streamlit as st
from utils.data_loader import carregar_conexao

# CARREGAR DADOS
con = carregar_conexao()

# CONFIGURAÇÃO DA PÁGINA
# Configurando Aba
st.set_page_config(
    page_title="Do Console pro Cinema",
    page_icon="🎮",
    layout="wide"
)

# HEADER
st.title("🎮 Do Console para o Cinema 🎬")
st.markdown( """Uma análise de adaptações cinematográficas baseadas em videogames, comparando performance de bilheteria, recepção crítica, avaliação de audiência e influência de publisher  — TidyTuesday de 09 de Junho de 2026""" )
st.caption("por João Victor Fernandes") 
st.caption("v1.0")

st.markdown("""
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

st.divider()

# SEÇÃO 1: KPI'S
# Total de adaptações
# Total de franquias adaptadas
# Bilheteria acumulada
# Média Rotten Tomatoes
# Média Metacritic
# Filme de maior arrecadação
# Maior Rotten Tomatoes
# Maior número de filmes (franquia)
# Pior filme (nota)

# SEÇÃO 2: EVOLUÇÃO DAS ADAPTAÇÕES
# Pergunta: Hollywood está produzindo mais filmes baseados em videogames do que antes?
# Visualizações: 
# Linha temporal por ano de lançamento
# Número de filmes lançados por ano
# Destaque para décadas

# SEÇÃO 3: AS FRANQUIAS MAIS ADAPTADAS
# Pergunta: Quais universos de videogame mais chegaram às telas?
# Visualizações: 
# Bar chart horizontal
# Top 15 franquias por quantidade de filmes
# Filtro por gênero

# SEÇÃO 4: QUEM REALMENTE GANHOU DINHEIRO?
# Pergunta: Ter muitos filmes significa sucesso financeiro?
# Visualização: Scatter plot:
# X = número de adaptações
# Y = bilheteria acumulada
# Tamanho = média de bilheteria
# Cada bolha = franquia.
# Isso permite descobrir:
# franquias com muitos filmes mas pouca receita;
# franquias com poucos filmes e enorme retorno.


# SEÇÃO 5: PUBLISH POWER
# Pergunta: Quais publishers dominam Hollywood?
# Visualização: Ranking de publishers
# Métricas: Número de filmes, Bilheteria total, Bilheteria média

# SEÇÃO 6: Críticos vs Audiência
# Pergunta: Audiência e crítica concordam sobre filmes de videogame?
# Visualização: Scatter plot:
# X = Rotten Tomatoes
# Y = CinemaScore
# Cada ponto = filme
# Adicionar linha de tendência.

# SEÇÃO 7: OS MAIORES FRACASSOS
# Pergunta: Quais adaptações tiveram a pior recepção?
# Visualização: Tabela interativa com filtro por Rotten < 40 e Metacritic < 40

# tentar incluir cards com posteres dos filmes
