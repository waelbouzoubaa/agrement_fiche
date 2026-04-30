import streamlit as st
from lib.db import get_db, init_db
from lib import crud

st.set_page_config(page_title="Fournisseurs — Ramery", page_icon="🏭", layout="wide")
init_db()

st.markdown("## 🏭 Fournisseurs")
st.caption("Liste des fournisseurs pour l'autocomplete")
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

st.markdown(f"**{len(suppliers)} fournisseur(s)**")

if not suppliers:
    st.info("Aucun fournisseur.")
else:
    for s in suppliers:
        c1, c2 = st.columns([8, 1])
        c1.write(s["name"])
        if c2.button("🗑️", key=f"delsup_{s['id']}"):
            with get_db() as db:
                crud.delete_supplier(db, s["id"])
            st.rerun()
