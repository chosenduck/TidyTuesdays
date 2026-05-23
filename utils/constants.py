from matplotlib.ticker import FuncFormatter
from pathlib import Path
import world_bank_data as wb

FMT_BI  = FuncFormatter(lambda y, _: f"US$ {y:.0f}bi")
FMT_PCT = FuncFormatter(lambda y, _: f"{y:.0f}%")

# ─── Grupos de países ─────────────────────────────────────────
PAISES_BRICS = ("Brazil", "Russian Federation", "India", "China", "South Africa")
PAISES_UNIVERSAL = ("Brazil", "United Kingdom of Great Britain and Northern Ireland", "Canada", "France", "Spain", "Australia", "Uruguay", "Sweden", "Portugal")

ISO_PAISES = ['BRA', 'RUS', 'IND', 'CHN', 'ZAF', 'FRA', 'ESP', 'GBR', 'CAN', 'URY', 'SWE', 'PRT', 'AUS']

# ─── URLs ─────────────────────────────────────────────────────
BASE_URL = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-04-21"

# ─── Diretórios ───────────────────────────────────────────────
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "raw"
DB_DIR = DATA_DIR / "warehouse"

ARQUIVOS = {
    "health_spending":   f"{BASE_URL}/health_spending.csv",
    "financing_schemes": f"{BASE_URL}/financing_schemes.csv",
    "spending_purpose":  f"{BASE_URL}/spending_purpose.csv",
    "population": wb.get_series('SP.POP.TOTL', country=ISO_PAISES, date='2000:2023').reset_index()
}

# ─── Textos de rodapé ─────────────────────────────────────────
FONTE = "Fonte: WHO Global Health Expenditure Database. Elaboração própria."
NOTA  = "Nota: Valores em US$ constantes de 2023."

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

# ─── Indicadores — Health Spending ───────────────────────────
INDICADORES_HS_PCT = ["gghed_che", "pvtd_che", "ext_che"]
INDICADORES_HS_ABS = ["che_usd2023", "gghed_usd2023", "pvtd_usd2023", "ext_usd2023"]

RENOMEAR_HS = {
    "gghed_che":    "Governo",
    "pvtd_che":     "Privado",
    "ext_che":      "Externo",
    "che_usd2023":  "Total",
    "gghed_usd2023":"Governo",
    "pvtd_usd2023": "Privado",
    "ext_usd2023":  "Externo",
}

# ─── Indicadores — Financing Schemes ─────────────────────────
INDICADORES_FS_PCT = ["hf1_che", "hf2_che", "hf3_che", "hf4_che", "hfnec_che"]
INDICADORES_FS_ABS = ["hf1_usd2023", "hf2_usd2023", "hf3_usd2023", "hf4_usd2023", "hfnec_usd2023"]

RENOMEAR_FS = {
    "hf1_che":       "SUS + RPPS",
    "hf2_che":       "Planos de Saude",
    "hf3_che":       "Desembolso direto",
    "hf4_che":       "Ajuda Externa",
    "hfnec_che":     "Nao Identificado",
    "hf1_usd2023":   "SUS + RPPS",
    "hf2_usd2023":   "Planos de Saude",
    "hf3_usd2023":   "Desembolso direto",
    "hf4_usd2023":   "Ajuda Externa",
    "hfnec_usd2023": "Nao Identificado",
}

# ─── Indicadores — Spending Purpose ──────────────────────────
INDICADORES_SP_PCT = ["hc1_che","hc2_che","hc3_che","hc4_che","hc5_che","hc6_che","hc7_che","hc9_che"]
INDICADORES_SP_ABS = ["hc1_usd2023","hc2_usd2023","hc3_usd2023","hc4_usd2023",
                      "hc5_usd2023","hc6_usd2023","hc7_usd2023","hc9_usd2023"]

RENOMEAR_SP_PT = {
    "hc1_che":      "Assistencia curativa",
    "hc2_che":      "Reabilitacao",
    "hc3_che":      "Cuidados de longa duracao",
    "hc4_che":      "Servicos auxiliares",
    "hc5_che":      "Produtos medicos",
    "hc6_che":      "Prevencao e promocao",
    "hc7_che":      "Governanca e administracao",
    "hc9_che":      "Outros",
    "hc1_usd2023":  "Assistencia curativa",
    "hc2_usd2023":  "Reabilitacao",
    "hc3_usd2023":  "Cuidados de longa duracao",
    "hc4_usd2023":  "Servicos auxiliares",
    "hc5_usd2023":  "Produtos medicos",
    "hc6_usd2023":  "Prevencao e promocao",
    "hc7_usd2023":  "Governanca e administracao",
    "hc9_usd2023":  "Outros",
}

MAPA_GRUPAMENTO = {
    "hc1": "Reativo",
    "hc2": "Recuperativo/Suporte",
    "hc3": "Recuperativo/Suporte",
    "hc4": "Recuperativo/Suporte",
    "hc5": "Recuperativo/Suporte",
    "hc6": "Preventivo/Proativo",
    "hc7": "Outros",
    "hc9": "Outros",
}

ORDEM_GRUPOS = ["Reativo", "Recuperativo/Suporte", "Preventivo/Proativo", "Outros"]

# ─── Paleta de cores ──────────────────────────────────────────
CORES = {
    # Fontes de financiamento
    "governo": "#1f77b4",
    "privado": "#ff7f0e",
    "oop":     "#d62728",
    "externo": "#2ca02c",
    "outro":   "#999999",
    # Países — BRICS
    "Brasil":        "#f4c300",
    "Rússia":        "#0039a6",
    "Índia":         "#ff9933",
    "China":         "#de2910",
    "África do Sul": "#007749",
    # Países — sistemas universais
    "França":        "#3b5aa3",
    "Espanha":       "#e67e22",
    "Reino Unido":   "#b22222",
    "Canadá":        "#8b0000",
    "Uruguai":       "#5dade2",
    "Portugal":      "#006600",
    "Suécia":        "#4682b4",
    "Austrália":     "#2e8b57",
    # Spending purpose — grupos
    "Reativo":              "#d62728",
    "Recuperativo/Suporte": "#ff7f0e",
    "Preventivo/Proativo":  "#2ca02c",
    "Outros_sp":            "#999999",
}

# Sequências para gráficos empilhados
CORES_HS_INDIC = [CORES["governo"], CORES["privado"], CORES["externo"]]
CORES_FS_INDIC = [CORES["governo"], CORES["privado"], CORES["oop"], CORES["externo"], CORES["outro"]]
CORES_SP_GRUP  = [CORES["Reativo"], CORES["Recuperativo/Suporte"], CORES["Preventivo/Proativo"], CORES["Outros_sp"]]


# Paleta de Cores 
COR_LINHA  = "#fc8181"
COR_BARRAS = "#63b3ed"  

COR_GOV  = "#2ca02c"
COR_PRIV = "#f4c300"

COMPONENTES = ["SUS", "Planos de Saúde", "Desembolso Direto", "Não Identificado"]
CORES_FS    = ["#63b3ed", "#fc8181", "#f6ad55", "#a0aec0"]

PAISES_ORDEM = ["África do Sul", "Brasil", "China", "Índia", "Rússia"]
CORES_BRICS  = {
        "Brasil":        "#f4c300",
        "China":         "#de2910",
        "Índia":         "#ff9933",
        "Rússia":        "#3b5aa3",
        "África do Sul": "#007749",
    }