import os
from datetime import date, datetime

import streamlit as st

from lib.db import get_db, UPLOADS_DIR, init_db
from lib import crud
from lib.pdf import generate_doe

st.set_page_config(page_title="Projet — Ramery", page_icon="📋", layout="wide")
init_db()

# ── Guard ─────────────────────────────────────────────────────────────────────
if "project_id" not in st.session_state:
    st.warning("Sélectionnez un chantier depuis la page d'accueil.")
    if st.button("← Retour à l'accueil"):
        st.switch_page("app.py")
    st.stop()

project_id = st.session_state["project_id"]

with get_db() as db:
    project  = crud.get_project(db, project_id)
    agrements = crud.get_agrements(db, project_id)
    products  = crud.get_products(db)
    suppliers = crud.get_suppliers(db)

if not project:
    st.error("Chantier introuvable.")
    st.switch_page("app.py")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
col_back, col_title = st.columns([1, 8])
with col_back:
    if st.button("← Chantiers"):
        st.switch_page("app.py")
with col_title:
    st.markdown(f"## 📋 {project['name']}")
    st.caption(f"Conducteur : {project['conducteur']} · {len(agrements)} fiche(s)")

st.markdown("---")

# ── Actions ───────────────────────────────────────────────────────────────────
col_add, col_doe, col_del = st.columns([2, 2, 1])

with col_add:
    show_form = st.toggle("➕ Ajouter une fiche", key="show_add_form")

with col_doe:
    if st.button("⬇️ Générer le DOE PDF", disabled=len(agrements) == 0,
                 type="primary", use_container_width=True):
        with st.spinner("Génération du PDF..."):
            pdf_bytes = generate_doe(project, agrements, UPLOADS_DIR)
        safe = project["name"].replace(" ", "_")[:40]
        st.download_button("📥 Télécharger le DOE", data=pdf_bytes,
                           file_name=f"DOE_{safe}.pdf", mime="application/pdf",
                           key="dl_doe")

with col_del:
    if st.button("🗑️ Supprimer", use_container_width=True):
        st.session_state["confirm_delete_project"] = True

if st.session_state.get("confirm_delete_project"):
    st.warning(f"⚠️ Supprimer **{project['name']}** et toutes ses fiches ?")
    c1, c2 = st.columns(2)
    if c1.button("Oui, supprimer", type="primary"):
        with get_db() as db:
            crud.delete_project(db, project_id)
        st.session_state.pop("project_id", None)
        st.session_state.pop("confirm_delete_project", None)
        st.switch_page("app.py")
    if c2.button("Annuler"):
        st.session_state.pop("confirm_delete_project", None)
        st.rerun()

# ── Formulaire ajout fiche (sans st.form pour permettre l'autofill) ───────────
if show_form:
    st.markdown("#### Nouvelle fiche d'agrément")

    # Initialisation des champs autofill dans session_state
    if "ag_supplier" not in st.session_state:
        st.session_state["ag_supplier"] = ""
    if "ag_category" not in st.session_state:
        st.session_state["ag_category"] = ""
    if "ag_submitted_by" not in st.session_state:
        st.session_state["ag_submitted_by"] = project["conducteur"]

    next_num = max((a["number"] for a in agrements), default=0) + 1

    r1, r2 = st.columns([1, 2])
    number       = r1.number_input("N° de fiche *", min_value=1, value=next_num, step=1)
    submitted_at = r2.date_input("Date", value=date.today())

    # ── Désignation avec autofill ─────────────────────────────────────────────
    des_options = ["— Nouveau produit —"] + [p["designation"] for p in products]

    def on_designation_change():
        sel = st.session_state["ag_des_select"]
        if sel == "— Nouveau produit —":
            return
        matched = next((p for p in products if p["designation"] == sel), None)
        if matched:
            st.session_state["ag_supplier"] = matched["supplier_name"]
            st.session_state["ag_category"] = matched.get("category") or ""

    des_select = st.selectbox(
        "Désignation *",
        des_options,
        key="ag_des_select",
        on_change=on_designation_change,
        help="Choisissez un produit existant → fournisseur et catégorie se remplissent automatiquement"
    )

    if des_select == "— Nouveau produit —":
        designation = st.text_input(
            "Nom du produit *",
            placeholder="Tampon EP d800 d400kn",
            key="ag_des_manual"
        )
    else:
        designation = des_select
        st.caption(f"✅ Produit sélectionné : **{designation}**")

    # ── Fournisseur (autofillé, modifiable) ───────────────────────────────────
    st.text_input(
        "Fournisseur / Provenance *",
        key="ag_supplier",
        placeholder="ALKERN / NORMANDY TUB",
        help="Rempli automatiquement si vous avez sélectionné un produit existant"
    )

    # ── Catégorie + Conducteur ────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    c1.text_input(
        "Catégorie / Utilisation",
        key="ag_category",
        placeholder="assainissement des EP"
    )
    c2.text_input("Conducteur de travaux", key="ag_submitted_by")

    st.markdown("")
    btn_save, btn_cancel, _ = st.columns([1, 1, 4])

    if btn_save.button("💾 Enregistrer", type="primary", use_container_width=True):
        final_des = st.session_state.get("ag_des_manual", "").strip() \
            if des_select == "— Nouveau produit —" else designation
        final_sup = st.session_state["ag_supplier"].strip()
        final_cat = st.session_state["ag_category"].strip()
        final_by  = st.session_state["ag_submitted_by"].strip()

        if not final_des:
            st.error("La désignation est obligatoire.")
        elif not final_sup:
            st.error("Le fournisseur est obligatoire.")
        else:
            dt = datetime.combine(submitted_at, datetime.min.time())
            with get_db() as db:
                crud.create_agrement(db, project_id, int(number), final_des,
                                     final_sup, final_cat, final_by, dt)
            # Réinitialiser le formulaire
            for k in ["ag_supplier", "ag_category", "ag_des_select",
                      "ag_des_manual", "ag_submitted_by"]:
                st.session_state.pop(k, None)
            st.session_state["show_add_form"] = False
            st.success(f"Fiche n°{number} — **{final_des}** ajoutée !")
            st.rerun()

    if btn_cancel.button("Annuler", use_container_width=True):
        for k in ["ag_supplier", "ag_category", "ag_des_select",
                  "ag_des_manual", "ag_submitted_by"]:
            st.session_state.pop(k, None)
        st.session_state["show_add_form"] = False
        st.rerun()

    st.markdown("---")

# ── Tableau des agréments ──────────────────────────────────────────────────────
if not agrements:
    st.info("Aucune fiche. Activez '➕ Ajouter une fiche' ci-dessus.")
else:
    st.markdown(f"#### Fiches d'agrément ({len(agrements)})")

    hcols = st.columns([1, 3, 3, 2, 3, 1])
    for col, label in zip(hcols, ["**N°**", "**Désignation**", "**Fournisseur**",
                                   "**Catégorie**", "**Fiche technique**", "**↓**"]):
        col.markdown(label)
    st.markdown('<hr style="margin:4px 0">', unsafe_allow_html=True)

    for a in agrements:
        cols = st.columns([1, 3, 3, 2, 3, 1])
        cols[0].markdown(f"**{a['number']}**")
        cols[1].write(a["designation"])
        cols[2].write(a["supplier_name"])
        cols[3].write(a["category"] or "—")

        with cols[4]:
            if a["datasheet_path"]:
                ds_path = os.path.join(UPLOADS_DIR, a["datasheet_path"])
                if os.path.exists(ds_path):
                    with open(ds_path, "rb") as f:
                        st.download_button("📄 PDF", data=f.read(),
                                           file_name=os.path.basename(a["datasheet_path"]),
                                           mime="application/pdf",
                                           key=f"dl_{a['id']}")
                if st.button("✕ Retirer", key=f"rm_{a['id']}"):
                    if os.path.exists(ds_path):
                        os.remove(ds_path)
                    with get_db() as db:
                        crud.update_agrement_datasheet(db, a["id"], None)
                    st.rerun()
            else:
                up = st.file_uploader("PDF", type="pdf", key=f"up_{a['id']}",
                                      label_visibility="collapsed")
                if up:
                    os.makedirs(UPLOADS_DIR, exist_ok=True)
                    fname = f"{a['id']}.pdf"
                    with open(os.path.join(UPLOADS_DIR, fname), "wb") as f:
                        f.write(up.getvalue())
                    with get_db() as db:
                        crud.update_agrement_datasheet(db, a["id"], fname)
                    st.rerun()

        with cols[5]:
            if st.button("🗑️", key=f"delag_{a['id']}"):
                with get_db() as db:
                    crud.delete_agrement(db, a["id"])
                st.rerun()

        st.markdown('<hr style="margin:2px 0;border-color:#f0f0f0">', unsafe_allow_html=True)
