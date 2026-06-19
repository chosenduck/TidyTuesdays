from pathlib import Path
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# URLs
BASE_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-06-09"

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR / "raw"
DB_DIR = DATA_DIR / "warehouse"

ARQUIVOS = {
    "game_films": f"{BASE_URL}/game_films.csv",
}

# Mapeamentos
MOEDAS_USD = {"$"}

TAXA_CONVERSAO: dict[str, float] = {
    "$":  1.0,
    "¥":  0.006,
}



# API
def _get_tmdb_key() -> str:
    # Streamlit Cloud / app publicado
    if hasattr(st, "secrets") and "TMDB_API_KEY" in st.secrets:
        return st.secrets["TMDB_API_KEY"]
    # fallback local (variável de ambiente)
    key = os.environ.get("TMDB_API_KEY")
    if not key:
        raise RuntimeError(
            "TMDB_API_KEY não encontrada. Configure em .streamlit/secrets.toml "
            "(local) ou em Settings → Secrets (Streamlit Cloud)."
        )
    return key

TMDB_API_KEY = _get_tmdb_key()
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w342"
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_TV_SEARCH_URL = "https://api.themoviedb.org/3/search/tv"
REQUEST_DELAY = 1                                               # segundos entre requisições (respeita rate limit: 40 req/10s)
REQUEST_TIMEOUT = 5

# PALETA DE CORES
class Colors:
    ORANGE   = "#ff8000" 
    WHITE    = "#ffffff"
    GREEN    = "#00e054"
    BLUE     = "#40bcf4"
    BG       = "#13181B"
    BG_SECONDARY = "#1a2228"

    # Sequência útil para gráficos com múltiplas séries
    PALETTE  = [GREEN, ORANGE, BLUE, WHITE]

# DECADAS
DECADAS: dict[str, tuple[int, int]] = {
    "1980": (1980, 1989),
    "1990": (1990, 1999),
    "2000": (2000, 2009),
    "2010": (2010, 2019),
    "2020": (2020, 2029),
}

# MAPEAMENTO DE FRANQUIAS
FRANQUIA_MAP: dict[str, str] = {
    # Resident Evil
    "Resident Evil":                            "Resident Evil",
    "Biohazard":                                "Resident Evil",
    "Raccoon City":                             "Resident Evil",

    # Mortal Kombat
    "Mortal Kombat":                            "Mortal Kombat",

    # Pokémon
    "Pokémon":                                  "Pokémon",
    "Pokemon":                                  "Pokémon",
    "Mewtwo":                                   "Pokémon",
    "Pikachu":                                  "Pokémon",

    # Street Fighter
    "Street Fighter":                           "Street Fighter",
    
    # Lara Croft / Tomb Raider
    "Lara Croft":                               "Tomb Raider",
    "Tomb Raider":                              "Tomb Raider",
    
    # Sonic
    "Sonic":                                    "Sonic",
    
    # Mario
    "Super Mario":                              "Mario",
    "Mario":                                    "Mario",
    
    # Final Fantasy
    "Final Fantasy":                            "Final Fantasy",
    "Kingsglaive":                              "Final Fantasy",
    
    # Prince of Persia
    "Prince of Persia":                         "Prince of Persia",
    
    # Need for Speed
    "Need for Speed":                           "Need for Speed",
    
    # Warcraft
    "Warcraft":                                 "Warcraft",
    "World of Warcraft":                        "Warcraft",
    
    # Assassin's Creed
    "Assassin":                                 "Assassin's Creed",
    
    # Tekken
    "Tekken":                                   "Tekken",
    
    # DOA
    "Dead or Alive":                            "Dead or Alive",
    
    # Doom
    "Doom":                                     "Doom",
    
    # Hitman
    "Hitman":                                   "Hitman",
    
    # Max Payne
    "Max Payne":                                "Max Payne",
    
    # Silent Hill
    "Silent Hill":                              "Silent Hill",
    
    # Wing Commander
    "Wing Commander":                           "Wing Commander",
    
    # BloodRayne
    "BloodRayne":                               "BloodRayne",
    
    # Dungeons & Dragons
    "Dungeons":                                 "Dungeons & Dragons",
    
    # Alone in the Dark
    "Alone in the Dark":                        "Alone in the Dark",
    
    # House of the Dead
    "House of the Dead":                        "House of the Dead",
    
    # Far Cry
    "Far Cry":                                  "Far Cry",
    
    # Double Dragon
    "Double Dragon":                            "Double Dragon",
    
    # Castlevania
    "Castlevania":                              "Castlevania",
    
    # Zelda
    "Zelda":                                    "The Legend of Zelda",

    # Monster Hunter
    "Monster Hunter":                           "Monster Hunter",

    # Uncharted
    "Uncharted":                                "Uncharted",

    # Five Nights at Freddy's
    "Five Nights at Freddy's":                  "Five Nights at Freddy's",

    # Borderlands
    "Borderlands":                              "Borderlands",

    # Minecraft
    "Minecraft":                                "Minecraft",

    # Until Dawn
    "Until Dawn":                               "Until Dawn",

    # Watch Dogs
    "Watch Dogs":                               "Watch Dogs",

    # Call of Duty
    "Modern Warfare":                           "Call of Duty",

    # Grand Theft Auto
    "Grand Theft":                              "Grand Theft Auto",

    # Persona
    "Persona":                                  "Persona",

    # Fatal Fury
    "Fatal Fury":                               "Fatal Fury",

    # Fate
    "Fate":                                     "Fate",

    # Tom Clancy's
    "The Division":                             "Tom Clancy's",
    "Ghost Recon":                              "Tom Clancy's",

    # DragonBall
    "Dragon Ball":                              "Dragon Ball",

    # Crash
    "Crash":                                    "Crash"
}

# MAPEAMENTO DE DISTRIBUIDORAS
DISTRIBUIDORA_MAP: dict[str, str] = {
    # Nintendo
    "Nintendo":                            "Nintendo",

    # Majesco
    "Majesco":                             "Majesco",

    # Koei
    "Koei Tecmo":                          "Koei Tecmo",

    # Hudson Soft
    "Hudson Soft":                         "Hudson Soft",

    # Bandai Namco
    "Bandai":                              "Bandai Namco",
    "Namco":                               "Bandai Namco",

    # Microsoft Studios
    "Microsoft":                           "Microsoft Studios",

    # SNK
    "SNK":                                 "SNK",

    # Sony
    "Sony":                                "Sony",

    # Square Enix
    "Square":                              "Square Enix",
    "Enix":                                "Square Enix",

    # Warner Bros
    "Warner":                              "Warner Bros."
}