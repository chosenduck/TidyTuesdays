import pandas as pd
import streamlit as st
from utils.constants import DECADAS, FRANQUIA_MAP, DISTRIBUIDORA_MAP

def _fmt_bilheteria(valor: float | None) -> str:
    if valor is None:
        return "—"
    if valor >= 1_000_000_000:
        return f"US$ {valor / 1_000_000_000:.1f} bi"
    if valor >= 1_000_000:
        return f"US$ {valor / 1_000_000:.0f} M"
    return f"US$ {valor:,.0f}"


def _clean_url(val) -> str:
    """Normaliza poster_url, tratando pd.NA, None e strings vazias."""
    try:
        s = str(val)
        return s if s.startswith("http") else ""
    except Exception:
        return ""
    
def kpi_card(label: str, value: str, caption: str = "", accent: str = "green") -> str:
    caption_html = f'<div class="kpi-caption">{caption}</div>' if caption else ""
    return f"""
    <div class="kpi-card kpi-{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {caption_html}
    </div>
    """


def kpi_record_card(
    container,
    label: str,
    value: str,
    title: str = "",
    year: str = "",
    poster_url: str = "",
    accent: str = "green",
) -> None:
    """
    Renderiza um card de recorde com pôster usando st.columns nativo.
    Usa st.image() para o poster (evita bloqueio de CSP do st.markdown).
    """
    accent_colors = {
        "green": "#00e054",
        "orange": "#ff8000",
        "blue": "#40bcf4",
        "red": "#e05454",
        "white": "#ffffff",
    }
    border_color = accent_colors.get(accent, "#00e054")

    year_html = f' <span style="color:#8a9bb0;font-size:0.7rem">({year})</span>' if year else ""
    caption_html = f'<div class="kpi-caption">{title}{year_html}</div>' if title else ""

    # wrapper com borda colorida
    container.markdown(
        f"""<div style="background:#1a2228;border-radius:6px;border-bottom:3px solid {border_color};overflow:hidden;">""",
        unsafe_allow_html=True,
    )

    col_img, col_txt = container.columns([1, 3])

    with col_img:
        if poster_url:
            st.image(poster_url, width='stretch')
        else:
            st.markdown(
                '<div style="background:#0d1519;height:100%;min-height:100px;display:flex;'
                'align-items:center;justify-content:center;font-size:1.6rem;padding:1rem">🎬</div>',
                unsafe_allow_html=True,
            )

    with col_txt:
        st.markdown(
            f"""
            <div style="padding:0.75rem 0.5rem 0.85rem 0;">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                {caption_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    container.markdown("</div>", unsafe_allow_html=True)

def decada_de(ano: int) -> str:
    for nome, (inicio, fim) in DECADAS.items():
        if inicio <= ano <= fim:
            return nome
    return "Outros"
 
def _identificar_franquia(titulo: str) -> str:
    if pd.isna(titulo):
        return "Outros"
    t = str(titulo)
    for chave, franquia in FRANQUIA_MAP.items():
        if chave.lower() in t.lower():
            return franquia
    return t  # título completo quando não mapeado

def _identificar_distribuidora(texto: str) -> str:
    """
    Normaliza publishers/distribuidoras para uma entidade única.

    Exemplos:
        Nintendo Co., Ltd.       -> Nintendo
        Bandai                   -> Bandai Namco
        Namco                    -> Bandai Namco
        Warner Interactive       -> Warner Bros.
    """

    if texto is None:
        return "Não informado"
    
    texto = str(texto).strip()
    if not texto:
        return "Não informado"

    for chave, publisher in DISTRIBUIDORA_MAP.items():
        if chave.lower() in texto.lower():
            return publisher

    return texto

def calcular_score(rt, meta):
    notas = [v for v in [rt, meta] if pd.notna(v)]

    if not notas:
        return None

    return round(sum(notas) / len(notas), 1)