import streamlit as st

st.set_page_config(
    page_title="Fiches d'Agrément — Ramery",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Charte graphique Ramery 2023 ──────────────────────────────────────────────
# Bleu principal : #003D7C  |  Rouge accent : #D41317  |  Gris texte : #4A4A49
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600;700;900&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

<style>
/* ── Typographie ───────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #4A4A49;
}
h1, h2, h3, h4, h5, h6,
.ramery-title, .ramery-heading {
    font-family: 'Lexend', 'Segoe UI', sans-serif !important;
    color: #003D7C !important;
    font-weight: 700;
}

/* ── Sidebar ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #003D7C !important;
}
[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] a:hover,
[data-testid="stSidebarNav"] a:hover {
    background-color: rgba(255,255,255,0.15) !important;
    border-radius: 6px;
}
/* Lien actif dans la sidebar */
[data-testid="stSidebarNav"] li[aria-selected="true"] a,
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: rgba(255,255,255,0.2) !important;
    border-left: 3px solid #D41317 !important;
    border-radius: 0 6px 6px 0;
    font-weight: 600;
}
/* Logo Ramery dans la sidebar */
[data-testid="stSidebarHeader"] {
    border-bottom: 1px solid rgba(255,255,255,0.2);
    padding-bottom: 0.5rem;
    margin-bottom: 0.5rem;
}

/* ── Boutons principaux → Bleu Ramery ──────────────────────────────── */
.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background-color: #003D7C !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px;
    font-family: 'Lexend', sans-serif;
    font-weight: 600;
    transition: background-color 0.2s;
}
.stButton > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    background-color: #002D5E !important;
}

/* ── Boutons secondaires ────────────────────────────────────────────── */
.stButton > button[kind="secondary"],
button[data-testid="baseButton-secondary"] {
    border: 1px solid #003D7C !important;
    color: #003D7C !important;
    border-radius: 6px;
    font-weight: 500;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #EEF3FA !important;
}

/* ── Download button ────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
    background-color: #003D7C !important;
    color: white !important;
    border: none !important;
    border-radius: 6px;
}

/* ── Toggle (switch) ────────────────────────────────────────────────── */
[data-testid="stToggle"] label span {
    color: #003D7C;
}

/* ── Inputs ──────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #003D7C !important;
    box-shadow: 0 0 0 1px #003D7C !important;
}

/* ── Selectbox ───────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div:first-child:focus-within {
    border-color: #003D7C !important;
}

/* ── Metric / info boxes ─────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background-color: #EEF3FA;
    border-left: 3px solid #003D7C;
    border-radius: 0 6px 6px 0;
    padding: 0.5rem 1rem;
}

/* ── Divider ─────────────────────────────────────────────────────────── */
hr {
    border-color: #EEF3FA !important;
}

/* ── Expander ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] summary {
    font-family: 'Lexend', sans-serif;
    font-weight: 600;
    color: #003D7C;
}

/* ── Info / success / warning banners ───────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 6px;
}

/* ── Table headers ───────────────────────────────────────────────────── */
.ramery-table-header {
    font-family: 'Lexend', sans-serif;
    font-weight: 600;
    font-size: 0.8rem;
    color: #003D7C;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 2px solid #003D7C;
    padding-bottom: 4px;
    margin-bottom: 4px;
}

/* ── Classe utilitaire rouge accent ─────────────────────────────────── */
.ramery-accent { color: #D41317 !important; }

/* ── Header de page ──────────────────────────────────────────────────── */
.ramery-page-title {
    font-family: 'Lexend', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #003D7C;
    border-bottom: 2px solid #EEF3FA;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}
.ramery-page-title span.accent {
    color: #D41317;
}

/* ── Badge statut ────────────────────────────────────────────────────── */
.badge-pending  { background: #FFF3CD; color: #856404; border-radius:12px; padding:2px 10px; font-size:0.78rem; }
.badge-ok       { background: #D1ECF1; color: #0C5460; border-radius:12px; padding:2px 10px; font-size:0.78rem; }

/* Masquer la page projet dans la nav quand pas de projet sélectionné */
</style>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
pages = [
    st.Page("pages/chantiers.py",    title="Chantiers",       icon="🏗️", default=True),
    st.Page("pages/projet.py",       title="Projet en cours", icon="📋"),
    st.Page("pages/produits.py",     title="Produits",        icon="📦"),
    st.Page("pages/fournisseurs.py", title="Fournisseurs",    icon="🏭"),
]

pg = st.navigation(pages)
pg.run()
