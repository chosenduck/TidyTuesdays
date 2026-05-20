# utils/data_loader.py
import pandas as pd
import streamlit as st
from utils.constants import BASE_URL

@st.cache_data
def carregar_dados() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Baixa os três datasets do GHED uma única vez por sessão.
    Retorna: health_spending, financing_schemes, spending_purpose
    """
    health_spending   = pd.read_csv(f"{BASE_URL}/health_spending.csv")
    financing_schemes = pd.read_csv(f"{BASE_URL}/financing_schemes.csv")
    spending_purpose  = pd.read_csv(f"{BASE_URL}/spending_purpose.csv")
    return health_spending, financing_schemes, spending_purpose