"""
Script standalone para enriquecer a tabela game_films_silver com URLs de pôsteres do TMDB.

Roda de forma incremental — processa apenas filmes sem poster_url preenchida.
Salva checkpoint no DuckDB a cada 25 filmes para evitar perda de progresso.

Uso:
    python scripts/poster.py            # enriquecimento real
    python scripts/poster.py --dry-run  # lista o que seria buscado, sem chamar a API
"""

import sys
import time

import duckdb
import pandas as pd

from utils.constants import DB_DIR, REQUEST_DELAY
from utils.data_transformer import _buscar_poster_tmdb

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

CHECKPOINT_INTERVALO = 25   # salva no DuckDB a cada N filmes processados

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _conectar() -> duckdb.DuckDBPyConnection:
    db_path = DB_DIR / "games_movies.duckdb"
    if not db_path.exists():
        print(f"[erro] Banco não encontrado em: {db_path}")
        sys.exit(1)
    return duckdb.connect(str(db_path))


def _carregar_silver(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    tabelas = con.sql("SHOW TABLES").df()["name"].tolist()
    if "game_films_silver" not in tabelas:
        print("[erro] Tabela game_films_silver não encontrada.")
        print("       Rode o pipeline Silver antes de executar este script.")
        sys.exit(1)
    df = con.sql("SELECT * FROM game_films_silver").df()
    df["poster_url"] = df["poster_url"].astype("string")
    return df


def _salvar_silver(con: duckdb.DuckDBPyConnection, df: pd.DataFrame) -> None:
    con.execute("DROP TABLE IF EXISTS game_films_silver")
    con.execute("CREATE TABLE game_films_silver AS SELECT * FROM df")


def _dry_run(df_pendentes: pd.DataFrame) -> None:
    """Imprime o que seria buscado sem fazer nenhuma requisição."""
    print(f"\n{'─' * 60}")
    print(f"DRY RUN — {len(df_pendentes)} filmes seriam processados:\n")

    for _, row in df_pendentes.iterrows():
        ano = int(row["release_year"]) if pd.notna(row["release_year"]) else None
        categoria = row.get("category", "?")
        is_tv = "Television" in str(categoria)

        fallbacks = [
            f"/search/movie  pt-BR" + (f" + ano={ano}" if ano else ""),
            f"/search/movie  pt-BR  (sem ano)",
            f"/search/movie  en-US",
            f"/search/tv     en-US" + ("provável hit" if is_tv else ""),
        ]

        print(f"  • {row['title']} ({ano or 'sem ano'})")
        print(f"    categoria : {categoria}")
        print(f"    fallbacks : {' → '.join(fallbacks)}")

    print(f"\n{'─' * 60}")
    print("Nenhuma requisição foi feita. Remova --dry-run para executar.")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def enriquecer(dry_run: bool = False) -> None:
    con = _conectar()
    df_silver = _carregar_silver(con)

    # Garante que a coluna existe mesmo em silver sem enriquecimento anterior
    if "poster_url" not in df_silver.columns:
        df_silver["poster_url"] = pd.NA

    mask_sem_poster = df_silver["poster_url"].isna()
    total_pendentes = mask_sem_poster.sum()

    print(f"\nTotal na tabela  : {len(df_silver)}")
    print(f"Com poster       : {df_silver['poster_url'].notna().sum()}")
    print(f"Sem poster       : {total_pendentes}")

    if total_pendentes == 0:
        print("\nNada a fazer — todos os filmes já têm poster.")
        con.close()
        return

    df_pendentes = df_silver[mask_sem_poster].copy()

    if dry_run:
        _dry_run(df_pendentes)
        con.close()
        return

    # Filtra entradas que nunca terão poster no TMDB
    mask_pular = (
        df_pendentes["title"].str.startswith("Untitled", na=False) |
        (df_pendentes["category"] == "Short films")
    )
    df_para_buscar = df_pendentes[~mask_pular].copy()
    df_pulados     = df_pendentes[mask_pular].copy()

    print(f"Iniciando busca de pôsteres para {len(df_para_buscar)} filmes...")
    print(f"  ({len(df_pulados)} entradas puladas — Untitled/Short films)\n")

    encontrados = 0
    nao_encontrados = 0

    # --- Enriquecimento real ---
    print(f"\nIniciando busca de pôsteres para {total_pendentes} filmes...\n")

    encontrados = 0
    nao_encontrados = 0

    for i, (idx, row) in enumerate(df_para_buscar.iterrows(), start=1):
        titulo = row["title"]
        ano = int(row["release_year"]) if pd.notna(row["release_year"]) else None

        url = _buscar_poster_tmdb(titulo, ano)
        df_silver.at[idx, "poster_url"] = url

        if url:
            encontrados += 1
            status = "OK"
        else:
            nao_encontrados += 1
            status = "ERRO"

        print(f"  [{i:>3}/{total_pendentes}] {status} {titulo} ({ano or '—'})")

        # Checkpoint incremental
        if i % CHECKPOINT_INTERVALO == 0:
            _salvar_silver(con, df_silver)
            pct = df_silver["poster_url"].notna().sum() / len(df_silver) * 100
            print(f"\n Checkpoint salvo ({i}/{total_pendentes} processados | "
                  f"{pct:.0f}% da tabela com poster)\n")

        time.sleep(REQUEST_DELAY)

    # Salva estado final
    _salvar_silver(con, df_silver)
    con.close()

    total_com_poster = df_silver["poster_url"].notna().sum()
    cobertura = total_com_poster / len(df_silver) * 100

    print(f"\n{'─' * 60}")
    print(f"Concluído.")
    print(f"  Encontrados nesta rodada : {encontrados}")
    print(f"  Não encontrados          : {nao_encontrados}")
    print(f"  Cobertura total          : {total_com_poster}/{len(df_silver)} ({cobertura:.1f}%)")
    print(f"{'─' * 60}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    enriquecer(dry_run=dry_run)