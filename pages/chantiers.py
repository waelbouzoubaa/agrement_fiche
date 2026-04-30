import streamlit as st
from lib.db import init_db, get_db
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
        ' <span class="accent">·</span> Chantiers</p>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Nouveau chantier ──────────────────────────────────────────────────────────
with st.expander("➕ Nouveau chantier", expanded=False):
    with st.form("form_new_project", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        name       = c1.text_input("Nom du chantier *",
                                   placeholder="ROSAY (76) - Aménagements de sécurité RD154")
        conducteur = c2.text_input("Conducteur de travaux", value="BRUNEL E")
        if st.form_submit_button("Créer le chantier", type="primary"):
            if name.strip():
                with get_db() as db:
                    crud.create_project(db, name.strip(), conducteur.strip())
                st.success("✅ Chantier créé !")
                st.rerun()
            else:
                st.error("Le nom du chantier est obligatoire.")

# ── Liste des chantiers ───────────────────────────────────────────────────────
with get_db() as db:
    projects = crud.get_projects(db)

st.markdown(
    f'<p style="font-family:\'Lexend\',sans-serif;font-weight:600;color:#003D7C;">'
    f'Chantiers ({len(projects)})</p>',
    unsafe_allow_html=True,
)

if not projects:
    st.info("Aucun chantier pour l'instant. Créez-en un ci-dessus.")
else:
    for p in projects:
        with st.container():
            cols = st.columns([6, 1, 1])
            with cols[0]:
                st.markdown(
                    f"<b style='color:#003D7C;font-family:Lexend,sans-serif'>{p['name']}</b><br>"
                    f"<span style='color:#4A4A49;font-size:0.85rem'>"
                    f"{p['agrement_count']} fiche(s) &nbsp;·&nbsp; "
                    f"Conducteur : {p['conducteur']}"
                    f"</span>",
                    unsafe_allow_html=True,
                )
            with cols[1]:
                if st.button("Ouvrir →", key=f"open_{p['id']}", use_container_width=True,
                             type="primary"):
                    st.session_state["project_id"] = p["id"]
                    st.switch_page("pages/projet.py")
            with cols[2]:
                if st.button("🗑️", key=f"del_{p['id']}", help="Supprimer le chantier"):
                    with get_db() as db:
                        crud.delete_project(db, p["id"])
                    st.rerun()
            st.markdown('<hr style="margin:8px 0;border-color:#EEF3FA">', unsafe_allow_html=True)
