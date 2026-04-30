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
        ' <span class="accent">·</span> Produits</p>',
        unsafe_allow_html=True,
    )
st.caption("Base de données des produits — utilisée pour l'autocomplete lors de la saisie des fiches")
st.markdown("---")

with st.expander("➕ Nouveau produit", expanded=False):
    with st.form("form_new_product", clear_on_submit=True):
        c1, c2 = st.columns(2)
        designation  = c1.text_input("Désignation *", placeholder="Tampon EP d800 d400kn")
        supplier_name = c2.text_input("Fournisseur *", placeholder="ALKERN / NORMANDY TUB")
        category = st.text_input("Catégorie", placeholder="assainissement des EP")
        if st.form_submit_button("Ajouter", type="primary"):
            if designation.strip() and supplier_name.strip():
                with get_db() as db:
                    crud.create_product(db, designation.strip(),
                                        supplier_name.strip(), category.strip())
                st.success("Produit ajouté !")
                st.rerun()
            else:
                st.error("Désignation et fournisseur obligatoires.")

q = st.text_input("🔍 Rechercher", placeholder="Tampon, bordure, béton...")

with get_db() as db:
    products = crud.get_products(db, q)

st.markdown(
    f'<p style="font-family:\'Lexend\',sans-serif;font-weight:600;color:#003D7C;">'
    f'Produits ({len(products)})</p>',
    unsafe_allow_html=True,
)

if not products:
    st.info("Aucun produit. Les produits se créent automatiquement quand vous ajoutez une fiche.")
else:
    hcols = st.columns([3, 3, 2, 1])
    for col, label in zip(hcols, ["**Désignation**", "**Fournisseur**", "**Catégorie**", ""]):
        col.markdown(label)
    st.divider()
    for p in products:
        cols = st.columns([3, 3, 2, 1])
        cols[0].write(p["designation"])
        cols[1].write(p["supplier_name"])
        cols[2].write(p["category"] or "—")
        if cols[3].button("🗑️", key=f"delprod_{p['id']}"):
            with get_db() as db:
                crud.delete_product(db, p["id"])
            st.rerun()
