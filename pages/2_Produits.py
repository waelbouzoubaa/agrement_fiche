import streamlit as st
from lib.db import get_db, init_db
from lib import crud

st.set_page_config(page_title="Produits — Ramery", page_icon="📦", layout="wide")
init_db()

st.markdown("## 📦 Produits")
st.caption("Bibliothèque de produits pour l'autocomplete")
st.markdown("---")

# ── Ajouter un produit ────────────────────────────────────────────────────────
with st.expander("➕ Nouveau produit", expanded=False):
    with st.form("form_new_product", clear_on_submit=True):
        c1, c2 = st.columns(2)
        designation = c1.text_input("Désignation *", placeholder="Tampon EP d800 d400kn")
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

# ── Recherche ─────────────────────────────────────────────────────────────────
q = st.text_input("🔍 Rechercher", placeholder="Tampon, bordure...")

with get_db() as db:
    products = crud.get_products(db, q)

st.markdown(f"**{len(products)} produit(s)**")

if not products:
    st.info("Aucun produit.")
else:
    hcols = st.columns([3, 3, 2, 1])
    hcols[0].markdown("**Désignation**")
    hcols[1].markdown("**Fournisseur**")
    hcols[2].markdown("**Catégorie**")
    hcols[3].markdown("**Suppr.**")
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
