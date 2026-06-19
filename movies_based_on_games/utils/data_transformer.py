import pandas as pd
import streamlit as st
import requests
import time
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.constants import TAXA_CONVERSAO, TMDB_API_KEY, TMDB_IMAGE_BASE, TMDB_SEARCH_URL, TMDB_TV_SEARCH_URL, REQUEST_DELAY, REQUEST_TIMEOUT 

def _seletor_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove colunas que não vão ser utilizadas na análise, por alta taxa de nulos ou outros motivos.
    """
    colunas_remover = [
        "air_date_raw",
        "network",
        "cinema_score",
        "domestic_box_office",
        "subject"
    ]

    colunas_existentes = [col for col in colunas_remover if col in df.columns]

    df = df.drop(columns=colunas_existentes)
    return df


def _remover_duplicatas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove linhas 100% duplicadas.
    As linhas 62 e 129 são duplicatas confirmadas.
    """
    df = df.drop_duplicates()
    return df.reset_index(drop=True)

def _tratar_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas para os tipos corretos."""

    # Data de lançamento
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce", format="%Y-%m-%d")
    
    # Numéricas — já chegam como float64, garante coerção
    for col in [ 
        "rotten_tomatoes", 
        "metacritic",
        "budget_low", 
        "budget_high"
        ]:

        df[col] = pd.to_numeric(df[col], errors="coerce")
 
    # Strings — strip em branco e normaliza None/NaN para pd.NA
    str_cols = [
        "category", "subcategory", "title", "director", "release_date_raw",
        "worldwide_box_office_currency",
        "distributor", "original_game_publisher", "budget_currency",
    ]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
            df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})
 
    return df

def _tratar_nulos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Tenta recuperar ano de release_date_raw quando release_date é nulo
    mask = df["release_date"].isna() & df["release_date_raw"].notna()

    anos_extraidos = (
        df.loc[mask, "release_date_raw"]
        .str.extract(r"(\d{4})", expand=False)
        .apply(lambda y: pd.to_datetime(f"{y}-01-01") if pd.notna(y) else pd.NaT)
    )

    df.loc[mask, "release_date"] = anos_extraidos
 
    # Coluna de ano derivada (útil para agrupamentos)
    df["release_year"] = df["release_date"].dt.year.astype("Int64")
    df = df.drop(columns="release_date_raw")
 
    # Strings que não podem ficar nulas em filtros de UI
    df["subcategory"] = df["subcategory"].fillna("N/A")
    df["distributor"] = df["distributor"].fillna("Não informado")
    df["original_game_publisher"] = df["original_game_publisher"].fillna("Não informado")
 
    return df

def _filtrar_filmes(df: pd.DataFrame) -> pd.DataFrame:
    ano_atual = pd.Timestamp.now().year
    antes = len(df)

    mask_remover = (
        df["release_year"].isna() |                                      # sem ano
        (df["release_year"] > ano_atual) |                               # ano futuro
        df["title"].str.startswith("Untitled", na=False)                 # anúncio sem título
    )

    df = df[~mask_remover]

    removidos = antes - len(df)
    if removidos:
        print(f"[filtro] {removidos} entradas removidas (sem ano, ano futuro ou Untitled)")
    return df.reset_index(drop=True)

def _normalizar_moeda(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria `worldwide_box_office_usd` convertendo para USD quando possível.
    Linhas com moeda desconhecida ou sem valor ficam com NaN.
    """
    def converter(row):
        currency = row["worldwide_box_office_currency"]
        valor = row["worldwide_box_office"]
        if pd.isna(valor) or pd.isna(currency):
            return float("nan")
        taxa = TAXA_CONVERSAO.get(str(currency), float("nan"))
        return valor * taxa
 
    df["worldwide_box_office_usd"] = df.apply(converter, axis=1)
    return df

def _criar_sessao() -> requests.Session:
    """Sessão com retry automático para erros de conexão."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,       # espera 1s, 2s, 4s entre tentativas
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session

_session = _criar_sessao()

@lru_cache(maxsize=2048)
def _buscar_poster_tmdb(titulo: str, ano: int | None = None) -> str | None:
    """
    Busca pôster no TMDB com cadeia de fallbacks:
      1. /search/movie  pt-BR + ano
      2. /search/movie  pt-BR  (sem ano)
      3. /search/movie  en-US  (sem ano — cobre títulos japoneses transliterados)
      4. /search/tv     en-US  (cobre séries, webseries, TV films)
    Retorna a URL completa (w342) ou None se nenhum fallback encontrar.
    """
    params_base: dict[str, str | int] = {
        "api_key": TMDB_API_KEY,
        "query": titulo,
        "include_adult": "false",
    }

    tentativas = [
        (TMDB_SEARCH_URL, {"language": "pt-BR", "year": ano} if ano else {"language": "pt-BR"}),
        (TMDB_SEARCH_URL, {"language": "pt-BR"}),
        (TMDB_SEARCH_URL, {"language": "en-US"}),
        (TMDB_TV_SEARCH_URL, {"language": "en-US"}),
    ]

    for endpoint, extras in tentativas:
        params = {
            **params_base,
            **{k: v for k, v in extras.items() if v is not None}
        }

        try:
            r = _session.get(endpoint, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            resultados = r.json().get("results", [])

            if resultados:
                # Tenta encontrar o melhor match: mesmo ano e com poster
                candidato = None

                for resultado in resultados[:5]:
                    poster_path = resultado.get("poster_path")
                    if not poster_path:
                        continue

                    if ano:
                        data_resultado = resultado.get("release_date", "")
                        ano_resultado = (
                            int(data_resultado[:4])
                            if data_resultado else None
                        )

                        if ano_resultado and abs(ano_resultado - ano) <= 1:
                            return f"{TMDB_IMAGE_BASE}{poster_path}"
                        elif candidato is None:
                            candidato = poster_path
                    else:
                        return f"{TMDB_IMAGE_BASE}{poster_path}"

                if candidato:
                    return f"{TMDB_IMAGE_BASE}{candidato}"

        except requests.exceptions.HTTPError as e:
            print(f"[TMDB] HTTP {e.response.status_code} para '{titulo}'")
            break  # erro de auth/rate limit — não adianta tentar de novo

        except requests.exceptions.Timeout:
            print(f"[TMDB] Timeout para '{titulo}'")

        except Exception as e:
            print(f"[TMDB] Erro inesperado para '{titulo}': {e}")

    return None

def _adicionar_posters(
    df: pd.DataFrame,
    usar_api: bool = True,
    tamanho_imagem: str = "w342",
) -> pd.DataFrame:
    """
    Enriquece o DataFrame com a coluna `poster_url`.

    Args:
        df:              DataFrame com colunas `title` e `release_year`.
        usar_api:        Se False, preenche com pd.NA (útil para testes sem consumir API).
        tamanho_imagem:  Tamanho do pôster TMDB. Opções: w92, w154, w185, w342, w500, w780, original.
                         w342 é o melhor custo-benefício para cards de dashboard.
    """
    if not usar_api:
        df["poster_url"] = pd.NA
        return df

    # Permite trocar o tamanho sem alterar a constante global
    global TMDB_IMAGE_BASE
    TMDB_IMAGE_BASE = f"https://image.tmdb.org/t/p/{tamanho_imagem}"

    total = len(df)
    print(f"[enriquecimento] Buscando pôsteres para {total} filmes...")

    poster_urls: list[str | None] = []
    for i, row in enumerate(df.itertuples(), start=1):
        ano = int(row.release_year) if pd.notna(row.release_year) else None
        url = _buscar_poster_tmdb(row.title, ano)
        poster_urls.append(url)

        if i % 50 == 0 or i == total:
            acertos = sum(1 for u in poster_urls if u)
            print(f"  {i}/{total} processados — {acertos} pôsteres encontrados")

        time.sleep(REQUEST_DELAY)   # throttle gentil com a API

    df["poster_url"] = pd.array(poster_urls, dtype="string")
    return df

def gerar_silver(df_bronze: pd.DataFrame, buscar_posters: bool = False) -> pd.DataFrame:
    """
    Aplica toda a limpeza e enriquecimento sobre o DataFrame bronze.
 
    Parâmetros
    ----------
    df_bronze    : DataFrame bruto vindo do data_loader.
    buscar_posters : Se True, consulta OMDb para preencher poster_url (lento).
 
    Retorna
    -------
    DataFrame Silver limpo e enriquecido.
    """
    df = df_bronze.copy()

    df = _remover_duplicatas(df)
    df = _seletor_colunas(df)
    df = _tratar_tipos(df)
    df = _tratar_nulos(df)
    df = _filtrar_filmes(df)
    df = _normalizar_moeda(df)
    df = _adicionar_posters(df, usar_api=buscar_posters)
 
    return df

def _gold_kpis(df: pd.DataFrame) -> dict:
    """KPIs globais para o header do dashboard."""
    filmes_theatricals = df[df["category"].str.contains("Theatrical", na=False)]
 
    total_filmes = len(df)
    total_publishers = df["original_game_publisher"].nunique()
    bilheteria_total = df["worldwide_box_office_usd"].sum()
    media_rt = df["rotten_tomatoes"].mean()
    media_mc = df["metacritic"].mean()
 
    # Colunas extras disponíveis para os cards de recordes
    _record_cols = ["title", "release_year", "poster_url"]

    # Maior bilheteria
    idx_box = df["worldwide_box_office_usd"].idxmax()
    maior_bilheteria = df.loc[idx_box, _record_cols + ["worldwide_box_office_usd"]] if pd.notna(idx_box) else None
 
    # Maior RT
    idx_rt = df["rotten_tomatoes"].idxmax()
    maior_rt = df.loc[idx_rt, _record_cols + ["rotten_tomatoes"]] if pd.notna(idx_rt) else None
 
    # Pior RT (mínimo com pelo menos 1 crítica)
    df_com_rt = df[df["rotten_tomatoes"].notna()]
    idx_pior = df_com_rt["rotten_tomatoes"].idxmin()
    pior_rt = df_com_rt.loc[idx_pior, _record_cols + ["rotten_tomatoes"]] if len(df_com_rt) > 0 else None
 
    return {
        "total_filmes": total_filmes,
        "total_publishers": total_publishers,
        "bilheteria_total_usd": bilheteria_total,
        "media_rotten_tomatoes": round(media_rt, 1) if pd.notna(media_rt) else None,
        "media_metacritic": round(media_mc, 1) if pd.notna(media_mc) else None,
        "maior_bilheteria": maior_bilheteria.to_dict() if maior_bilheteria is not None else {},
        "maior_rt": maior_rt.to_dict() if maior_rt is not None else {},
        "pior_rt": pior_rt.to_dict() if pior_rt is not None else {},
    }
 
 
def _gold_evolucao_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """Filmes por ano de lançamento (seção 2)."""
    return (
        df[df["release_year"].notna()]
        .groupby("release_year")
        .agg(
            total_filmes=("title", "count"),
            bilheteria_total=("worldwide_box_office_usd", "sum"),
            media_rt=("rotten_tomatoes", "mean"),
            media_mc=("metacritic", "mean"), 
        )
        .reset_index()
        .rename(columns={"release_year": "ano"})
        .sort_values("ano")
    )
 
 
def _gold_publishers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ranking de publishers por filmes e bilheteria (seção 5).
    Explode publishers separados por ' | '.
    """
    df_exp = df.copy()
    df_exp["original_game_publisher"] = df_exp["original_game_publisher"].str.split(r"\s*\|\s*")
    df_exp = df_exp.explode("original_game_publisher")
    df_exp["original_game_publisher"] = df_exp["original_game_publisher"].str.strip()
    df_exp = df_exp[df_exp["original_game_publisher"] != "Não informado"]
 
    return (
        df_exp.groupby("original_game_publisher")
        .agg(
            total_filmes=("title", "count"),
            bilheteria_total=("worldwide_box_office_usd", "sum"),
            bilheteria_media=("worldwide_box_office_usd", "mean"),
            media_rt=("rotten_tomatoes", "mean"),
        )
        .reset_index()
        .sort_values("total_filmes", ascending=False)
    )
 
 
def _gold_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dados para scatter Críticos vs Audiência (seção 6).
    Retorna apenas filmes com pelo menos RT e CinemaScore preenchidos.
    """
    cols = ["title", "release_year", "rotten_tomatoes", "metacritic",
            "worldwide_box_office_usd", "original_game_publisher", "poster_url"]
    return (
        df[cols]
        .dropna(subset=["rotten_tomatoes"])
        .reset_index(drop=True)
    )
 
 
def _gold_fracassos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabela para a seção de maiores fracassos (seção 7).
    Inclui filmes com RT < 40 OU Metacritic < 40.
    """
    mask = (df["rotten_tomatoes"] < 40) | (df["metacritic"] < 40)
    cols = [
        "title", "release_year", "director", "original_game_publisher",
        "worldwide_box_office_usd", "rotten_tomatoes", "metacritic", "poster_url",
    ]
    return (
        df[mask][cols]
        .sort_values("rotten_tomatoes")
        .reset_index(drop=True)
    )

 
def _gold_bilheteria_por_publisher(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scatter: nº de adaptações × bilheteria acumulada por publisher (seção 4).
    """
    return (
        _gold_publishers(df)[
            ["original_game_publisher", "total_filmes", "bilheteria_total", "bilheteria_media"]
        ]
        .dropna(subset=["bilheteria_total"])
        .reset_index(drop=True)
    )
 
 
def gerar_gold(df_silver: pd.DataFrame) -> dict[str, pd.DataFrame | dict]:
    """
    Gera todas as tabelas Gold a partir do Silver.
 
    Retorna um dicionário com as chaves:
    - kpis                  → dict com métricas globais
    - evolucao_temporal     → DataFrame por ano
    - publishers            → DataFrame de ranking de publishers
    - scores                → DataFrame para scatter críticos vs audiência
    - fracassos             → DataFrame para tabela de fracassos
    - bilheteria_publisher  → DataFrame para scatter bilheteria × adaptações
    """
    return {
        "kpis": _gold_kpis(df_silver),
        "evolucao_temporal": _gold_evolucao_temporal(df_silver),
        "publishers": _gold_publishers(df_silver),
        "scores": _gold_scores(df_silver),
        "fracassos": _gold_fracassos(df_silver),
        "bilheteria_publisher": _gold_bilheteria_por_publisher(df_silver),
    }

@st.cache_data
def carregar_silver(_con, buscar_posters: bool = False) -> pd.DataFrame:
    """
    Carrega a camada Silver: puxa o bronze do DuckDB e aplica todo o pipeline.
 
    Exemplo:
        from utils.data_transformer import carregar_silver
        df_silver = carregar_silver(con)
    """

    # Se a tabela silver com poster já foi gerada offline, usa ela diretamente
    tabelas = _con.sql("SHOW TABLES").df()["name"].tolist()
    if "game_films_silver" in tabelas:
        return _con.sql("SELECT * FROM game_films_silver").df()

    # Fallback: gera na hora (sem pôsteres, para desenvolvimento)
    df_bronze = _con.sql("SELECT * FROM game_films").df()
    return gerar_silver(df_bronze, buscar_posters=buscar_posters)
 
@st.cache_data
def carregar_gold(_con, buscar_posters: bool = False) -> dict:
    """
    Carrega todas as tabelas Gold prontas para visualização.
 
    Exemplo:
        from utils.data_transformer import carregar_gold
        gold = carregar_gold(con)
        kpis = gold["kpis"]
        df_tempo = gold["evolucao_temporal"]
    """
    df_silver = carregar_silver(_con, buscar_posters=buscar_posters)
    return gerar_gold(df_silver)