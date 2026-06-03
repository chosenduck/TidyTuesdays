from pathlib import Path

# ─── URLs ─────────────────────────────────────────────────────
BASE_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-06-09"

# ─── Diretórios ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "raw"
DB_DIR = DATA_DIR / "warehouse"

ARQUIVOS = {
    "game_films": f"{BASE_URL}/game_films.csv",
}