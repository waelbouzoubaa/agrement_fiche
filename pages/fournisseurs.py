import streamlit as st
from lib.db import get_db, init_db
from lib import crud

init_db()

# ── En-tête avec logo ─────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 6])
with col_logo:
    try:
        st.image("logo.png", width=110)
    except Exception:
        pass
with col_title:
    st.markdown(
        '<p class="ramery-page-title">Fiches d\'Agrément'
        ' <span class="accent">·</span> Fournisseurs</p>',
        unsafe_allow_html=True,
    )
st.caption("Base de données des fournisseurs — utilisée pour l'autocomplete lors de la saisie des fiches")
st.markdown("---")

with st.expander("➕ Nouveau fournisseur", expanded=False):
    with st.form("form_new_sup", clear_on_submit=True):
        name = st.text_input("Nom *", placeholder="ALKERN / NORMANDY TUB")
        if st.form_submit_button("Ajouter", type="primary"):
            if name.strip():
                with get_db() as db:
                    crud.create_supplier(db, name.strip())
                st.success("Fournisseur ajouté !")
                st.rerun()
            else:
                st.error("Nom obligatoire.")

q = st.text_input("🔍 Rechercher", placeholder="ALKERN, LAFARGE...")

with get_db() as db:
    suppliers = crud.get_suppliers(db, q)

st.markdown(
    f'<p style="font-family:\'Lexend\',sans-serif;font-weight:600;color:#003D7C;">'
    f'Fournisseurs ({len(suppliers)})</p>',
    unsafe_allow_html=True,
)

if not suppliers:
    st.info("Aucun fournisseur. Ils se créent automatiquement quand vous ajoutez une fiche.")
else:
    for s in suppliers:
        c1, c2 = st.columns([8, 1])
        c1.write(s["name"])
        if c2.button("🗑️", key=f"delsup_{s['id']}"):
            with get_db() as db:
                crud.delete_supplier(db, s["id"])
            st.rerun()
