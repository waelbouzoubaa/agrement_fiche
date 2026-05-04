import streamlit as st
from lib.db import get_db, init_db
from lib import crud, storage

# Reset formulaire nouveau produit
if st.session_state.get("prod_reset"):
    for k in ["prod_designation", "prod_sup_select", "prod_sup_manual", "prod_category"]:
        st.session_state.pop(k, None)
    st.session_state.pop("prod_reset", None)

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
st.caption("Base de données des produits — chaque produit a sa propre fiche technique stockée sur GCS")
st.markdown("---")

with st.expander("➕ Nouveau produit", expanded=False):
    with get_db() as db:
        suppliers_list = crud.get_suppliers(db)

    sup_options = ["— Nouveau fournisseur —"] + [s["name"] for s in suppliers_list]

    if "prod_sup_select" not in st.session_state:
        st.session_state["prod_sup_select"] = "— Nouveau fournisseur —"

    c1, c2 = st.columns(2)
    designation = c1.text_input("Désignation *", placeholder="Tampon EP d800 d400kn",
                                key="prod_designation")
    c2.selectbox("Fournisseur *", sup_options, key="prod_sup_select")

    if st.session_state["prod_sup_select"] == "— Nouveau fournisseur —":
        supplier_name = st.text_input("Nom du fournisseur *",
                                      placeholder="ALKERN / NORMANDY TUB",
                                      key="prod_sup_manual")
    else:
        supplier_name = st.session_state["prod_sup_select"]

    category = st.text_input("Catégorie", placeholder="assainissement des EP",
                             key="prod_category")

    if st.button("Ajouter", type="primary"):
        if designation.strip() and supplier_name.strip():
            with get_db() as db:
                crud.create_product(db, designation.strip(),
                                    supplier_name.strip(), category.strip())
            st.success("Produit ajouté !")
            st.session_state["prod_reset"] = True
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
    hcols = st.columns([3, 2, 2, 3, 1])
    for col, label in zip(hcols, ["**Désignation**", "**Fournisseur**", "**Catégorie**", "**Fiche technique**", ""]):
        col.markdown(label)
    st.divider()

    for p in products:
        cols = st.columns([3, 2, 2, 3, 1])
        cols[0].write(p["designation"])
        cols[1].write(p["supplier_name"])
        cols[2].write(p["category"] or "—")

        with cols[3]:
            blob = p.get("datasheet_url")
            if blob:
                try:
                    pdf_bytes = storage.download_datasheet(blob)
                    safe = p["designation"][:20].replace(" ", "_")
                    st.download_button("📄 Télécharger", data=pdf_bytes,
                                       file_name=f"FT_{safe}.pdf",
                                       mime="application/pdf",
                                       key=f"dl_prod_{p['id']}")
                except Exception as e:
                    st.warning(f"Indisponible : {e}")
                if st.button("✕ Retirer", key=f"rm_prod_{p['id']}"):
                    try:
                        storage.delete_datasheet(blob)
                    except Exception:
                        pass
                    with get_db() as db:
                        crud.update_product_datasheet_url(db, p["id"], None)
                    st.rerun()
            else:
                up = st.file_uploader("PDF", type="pdf", key=f"up_prod_{p['id']}",
                                      label_visibility="collapsed")
                if up:
                    with st.spinner("Upload..."):
                        try:
                            blob_name = storage.upload_datasheet(up.getvalue(), f"product_{p['id']}")
                            with get_db() as db:
                                crud.update_product_datasheet_url(db, p["id"], blob_name)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur upload : {e}")

        with cols[4]:
            if st.button("🗑️", key=f"delprod_{p['id']}"):
                if p.get("datasheet_url"):
                    try:
                        storage.delete_datasheet(p["datasheet_url"])
                    except Exception:
                        pass
                with get_db() as db:
                    crud.delete_product(db, p["id"])
                st.rerun()
