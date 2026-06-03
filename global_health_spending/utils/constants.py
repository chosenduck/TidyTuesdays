from matplotlib.ticker import FuncFormatter
from pathlib import Path
import world_bank_data as wb

# ─── URLs ─────────────────────────────────────────────────────
BASE_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-04-21"

# ─── Diretórios ───────────────────────────────────────────────
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "raw"
DB_DIR = DATA_DIR / "warehouse"

ISO_PAISES = ['BRA', 'RUS', 'IND', 'CHN', 'ZAF', 'FRA', 'ESP', 'GBR', 'CAN', 'URY', 'SWE', 'PRT', 'AUS']

ARQUIVOS = {
    "health_spending":   f"{BASE_URL}/health_spending.csv",
    "financing_schemes": f"{BASE_URL}/financing_schemes.csv",
    "spending_purpose":  f"{BASE_URL}/spending_purpose.csv",
    "population": wb.get_series('SP.POP.TOTL', country=ISO_PAISES, date='2000:2023').reset_index()
}

# ─── Grupos de países ─────────────────────────────────────────
PAISES_BRICS = ("Brazil", "Russian Federation", "India", "China", "South Africa")
PAISES_UNIVERSAL = ("Brazil", "United Kingdom of Great Britain and Northern Ireland", "Canada", "France", "Spain", "Australia", "Uruguay", "Sweden", "Portugal")

BRICS_ORDEM = ["África do Sul", "Brasil", "China", "Índia", "Rússia"]
UNIVERSAL_ORDEM = ["Uruguai", "Portugal", "Suécia", "Espanha", "Austrália", "Canadá", "França", "Reino Unido", "Brasil"]

# ─── Tradução de nomes ────────────────────────────────────────
NOMES_PAISES = {
    "Brazil":                                              "Brasil",
    "Russian Federation":                                  "Rússia",
    "India":                                               "Índia",
    "China":                                               "China",
    "South Africa":                                        "África do Sul",
    "Iran (Islamic Republic of)":                          "Irã",
    "Indonesia":                                           "Indonésia",
    "Saudi Arabia":                                        "Arábia Saudita",
    "Egypt":                                               "Egito",
    "United Arab Emirates":                                "Emirados Árabes Unidos",
    "Ethiopia":                                            "Etiópia",
    "United Kingdom of Great Britain and Northern Ireland": "Reino Unido",
    "Australia":                                           "Austrália",
    "Canada":                                              "Canadá",
    "France":                                              "França",
    "Spain":                                               "Espanha",
    "Uruguay":                                             "Uruguai",
    "Sweden":                                              "Suécia",
    "Portugal":                                            "Portugal",
}

MAPA_GRUPAMENTO = {
    "hc1": "Reativo",
    "hc2": "Recuperativo",
    "hc3": "Recuperativo",
    "hc4": "Recuperativo",
    "hc5": "Recuperativo",
    "hc6": "Preventivo",
    "hc7": "Outros",
    "hc9": "Outros",
}

ORDEM_GRUPOS = ["Reativo", "Recuperativo/Suporte", "Preventivo/Proativo", "Outros"]

# ─── Paleta de cores ──────────────────────────────────────────
COR_LINHA  = "#CCE5FF"
COR_BARRAS = "#F9F5E6"
COR_EIXOS =  "#a0aec0"

COR_GOV  = "#26422b"
COR_PRIV = "#F9F5E6"
COR_DESEMB = "#CCE5FF"
COR_NAO = "#a0aec0"
COR_RAZAO = "#c03927"

COMPONENTES = ["SUS", "Planos de Saúde", "Desembolso Direto", "Não Identificado"]

CORES_FS    = ["#63b3ed", "#fc8181", "#f6ad55", "#a0aec0"]

COR_REAT = "#26422b"
COR_REC = "#E0DBCE"
COR_PREV = "#CCE5FF"
COR_OUT = "#a0aec0"

CORES_BRICS  = {
        "Brasil":        "#f4c300",
        "China":         "#de2910",
        "Índia":         "#ff9933",
        "Rússia":        "#a0aec0",
        "África do Sul": "#007749",
    }

CORES = {
    # Países — BRICS 
    "Brasil": "#f4c300", 
    "Rússia": "#a0aec0", 
    "Índia": "#ff9933", 
    "China": "#de2910", 
    "África do Sul": "#007749",
    # Países — sistemas universais 
    "França": "#3b5aa3", 
    "Espanha": "#e67e22", 
    "Reino Unido": "#b22222", 
    "Canadá": "#8b0000", 
    "Uruguai": "#5dade2", 
    "Portugal": "#006600", 
    "Suécia": "#4682b4", 
    "Austrália": "#2e8b57",
}