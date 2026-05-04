import os
from datetime import date, datetime

import streamlit as st
from lib.db import get_db, UPLOADS_DIR, init_db
from lib import crud, storage
from lib.pdf import generate_doe

init_db()

# ── Reset formulaire (doit s'exécuter AVANT l'instanciation des widgets) ──────
if st.session_state.get("ag_reset_form"):
    for k in ["ag_des_select", "ag_supplier", "ag_category",
              "ag_des_manual", "ag_submitted_by", "show_add_form"]:
        st.session_state.pop(k, None)
    st.session_state.pop("ag_reset_form", None)

# ── Guard ─────────────────────────────────────────────────────────────────────
if "project_id" not in st.session_state:
    st.info("👈 Ouvrez un chantier depuis la page **Chantiers** pour accéder à cette page.")
    st.stop()

project_id = st.session_state["project_id"]

with get_db() as db:
    project   = crud.get_project(db, project_id)
    agrements = crud.get_agrements(db, project_id)
    products  = crud.get_products(db)

if not project:
    st.error("Chantier introuvable.")
    st.switch_page("pages/chantiers.py")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
col_logo, col_back, col_title = st.columns([1, 1, 8])
with col_logo:
    try:
        st.image("logo.png", width=110)
    except Exception:
        pass
with col_back:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Chantiers"):
        st.session_state.pop("project_id", None)
        st.switch_page("pages/chantiers.py")
with col_title:
    st.markdown(
        f'<p class="ramery-page-title">📋 {project["name"]}</p>',
        unsafe_allow_html=True,
    )
    st.caption(f"Conducteur : {project['conducteur']} · {len(agrements)} fiche(s)")

st.markdown("---")

# ── Actions barre ─────────────────────────────────────────────────────────────
col_add, col_doe, col_del = st.columns([2, 2, 1])

with col_add:
    show_form = st.toggle("➕ Ajouter une fiche", key="show_add_form")

with col_doe:
    if st.button("⬇️ Générer le DOE PDF", disabled=len(agrements) == 0,
                 type="primary", use_container_width=True):
        with st.spinner("Génération du PDF..."):
            pdf_bytes = generate_doe(project, agrements, UPLOADS_DIR, products)
        safe = "".join(c for c in project["name"] if c.isalnum() or c in " _-")[:40]
        st.download_button("📥 Télécharger le DOE", data=pdf_bytes,
                           file_name=f"DOE_{safe}.pdf", mime="application/pdf",
                           key="dl_doe")

with col_del:
    if st.button("🗑️ Supprimer chantier", use_container_width=True):
        st.session_state["confirm_delete"] = True

if st.session_state.get("confirm_delete"):
    st.warning(f"⚠️ Supprimer **{project['name']}** et toutes ses fiches ?")
    c1, c2 = st.columns(2)
    if c1.button("Oui, supprimer", type="primary"):
        with get_db() as db:
            crud.delete_project(db, project_id)
        st.session_state.pop("project_id", None)
        st.session_state.pop("confirm_delete", None)
        st.switch_page("pages/chantiers.py")
    if c2.button("Annuler"):
        st.session_state.pop("confirm_delete", None)
        st.rerun()

# ── Formulaire ajout fiche ────────────────────────────────────────────────────
if show_form:
    st.markdown(
        '<p style="font-family:Lexend,sans-serif;font-weight:700;color:#003D7C;font-size:1.1rem;">'
        "Nouvelle fiche d'agrément</p>",
        unsafe_allow_html=True,
    )

    # Initialisation OBLIGATOIRE avant les widgets (évite le KeyError)
    if "ag_des_select" not in st.session_state:
        st.session_state["ag_des_select"] = "— Nouveau produit —"
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
        # Accès sécurisé avec .get() au cas où la clé serait absente
        sel = st.session_state.get("ag_des_select", "— Nouveau produit —")
        if sel == "— Nouveau produit —":
            st.session_state["ag_supplier"] = ""
            st.session_state["ag_category"] = ""
            return
        matched = next((p for p in products if p["designation"] == sel), None)
        if matched:
            st.session_state["ag_supplier"] = matched["supplier_name"]
            st.session_state["ag_category"] = matched.get("category") or ""

    st.selectbox(
        "Désignation *",
        des_options,
        key="ag_des_select",
        on_change=on_designation_change,
        help="Sélectionnez un produit → fournisseur et catégorie se remplissent automatiquement",
    )

    if st.session_state["ag_des_select"] == "— Nouveau produit —":
        designation_manuelle = st.text_input(
            "Nom du produit *", placeholder="Tampon EP d800 d400kn", key="ag_des_manual"
        )
    else:
        designation_manuelle = None
        st.caption(f"✅ **{st.session_state['ag_des_select']}**")

    # Fournisseur — autofillé et modifiable
    st.text_input(
        "Fournisseur / Provenance *",
        key="ag_supplier",
        placeholder="ALKERN / NORMANDY TUB",
    )

    c1, c2 = st.columns(2)
    c1.text_input("Catégorie / Utilisation", key="ag_category",
                  placeholder="assainissement des EP")
    c2.text_input("Conducteur de travaux", key="ag_submitted_by")

    st.markdown("")
    btn_save, btn_cancel, _ = st.columns([1, 1, 4])

    if btn_save.button("💾 Enregistrer", type="primary", use_container_width=True):
        sel = st.session_state.get("ag_des_select", "— Nouveau produit —")
        if sel == "— Nouveau produit —":
            final_des = (designation_manuelle or "").strip()
        else:
            final_des = sel

        final_sup = st.session_state.get("ag_supplier", "").strip()
        final_cat = st.session_state.get("ag_category", "").strip()
        final_by  = st.session_state.get("ag_submitted_by", "").strip()

        if not final_des:
            st.error("La désignation est obligatoire.")
        elif not final_sup:
            st.error("Le fournisseur est obligatoire.")
        else:
            dt = datetime.combine(submitted_at, datetime.min.time())
            with get_db() as db:
                crud.create_agrement(db, project_id, int(number), final_des,
                                     final_sup, final_cat, final_by, dt)
            st.session_state["ag_reset_form"] = True
            st.success(f"Fiche n°{number} — **{final_des}** ajoutée !")
            st.rerun()

    if btn_cancel.button("Annuler", use_container_width=True):
        st.session_state["ag_reset_form"] = True
        st.rerun()

    st.markdown("---")

# ── Tableau des agréments ─────────────────────────────────────────────────────
if not agrements:
    st.info("Aucune fiche. Activez '➕ Ajouter une fiche' ci-dessus.")
else:
    st.markdown(
        f'<p style="font-family:Lexend,sans-serif;font-weight:700;color:#003D7C;font-size:1.1rem;">'
        f"Fiches ({len(agrements)})</p>",
        unsafe_allow_html=True,
    )
    hcols = st.columns([1, 3, 3, 2, 3, 1])
    for col, label in zip(hcols, ["**N°**", "**Désignation**", "**Fournisseur**",
                                   "**Catégorie**", "**Fiche technique**", ""]):
        col.markdown(label)
    st.markdown('<hr style="margin:4px 0">', unsafe_allow_html=True)

    for a in agrements:
        cols = st.columns([1, 3, 3, 2, 3, 1])
        cols[0].markdown(f"**{a['number']}**")
        cols[1].write(a["designation"])
        cols[2].write(a["supplier_name"])
        cols[3].write(a["category"] or "—")

        with cols[4]:
            # Cherche la fiche technique : d'abord sur le produit, sinon sur l'agrément
            matched_product = next(
                (p for p in products if p["designation"] == a["designation"]), None
            )
            blob = (matched_product or {}).get("datasheet_url") or a.get("datasheet_url")
            if blob:
                try:
                    pdf_bytes = storage.download_datasheet(blob)
                    safe_name = f"FT_{a['number']}_{a['designation'][:20]}.pdf".replace(" ", "_")
                    st.download_button("📄 Fiche technique", data=pdf_bytes,
                                       file_name=safe_name, mime="application/pdf",
                                       key=f"dl_{a['id']}")
                except Exception as e:
                    st.warning(f"Fichier indisponible : {e}")
            else:
                st.caption("— Aller dans **Produits** pour uploader la fiche technique")

        with cols[5]:
            if st.button("🗑️", key=f"delag_{a['id']}"):
                with get_db() as db:
                    crud.delete_agrement(db, a["id"])
                st.rerun()

        st.markdown('<hr style="margin:2px 0;border-color:#f0f0f0">', unsafe_allow_html=True)
