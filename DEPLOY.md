# Déploiement — Fiches d'Agrément Ramery

## Prérequis VPS

- Ubuntu 22.04+
- Docker + Docker Compose installés
- Git installé
- Port **8502** ouvert dans le firewall

### Installer Docker (si pas encore fait)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

---

## 1. Cloner le projet

```bash
cd /opt
sudo git clone https://github.com/waelbouzoubaa/agrement_fiche.git
cd agrement_fiche
```

---

## 2. Copier la clé GCP

Depuis ton PC (PowerShell) :

```powershell
scp NOM_FICHIER_CLE.json user@IP_VPS:/tmp/gcp-key.json
```

Sur le VPS :

```bash
sudo mv /tmp/gcp-key.json /opt/agrement_fiche/gcp-key.json
```

> Le fichier doit s'appeler `gcp-key.json` dans le dossier du projet — il est monté automatiquement dans le container Docker.

---

## 3. Configurer le `.env`

```bash
sudo nano /opt/agrement_fiche/.env
```

Contenu :

```env
DATABASE_URL=postgresql://postgres:ramery2024@db:5432/agrement
UPLOADS_DIR=/app/uploads
GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcp-key.json
GCS_BUCKET=NOM_DU_BUCKET_GCS
```

> **Bucket GCS** : vérifier le vrai nom sur GCP Console → Cloud Storage → Buckets (projet `ramery-ai-features`).
> En local le bucket s'appelle `ramery-ai-features-fiches-produit-fournisseur`.

---

## 4. Lancer l'application

```bash
cd /opt/agrement_fiche
sudo docker compose up -d --build
```

L'app est accessible sur : **http://IP_VPS:8502**

---

## 5. Mettre à jour après un push Git

```bash
cd /opt/agrement_fiche
sudo git pull
sudo docker compose up -d --build
```

---

## Commandes utiles

```bash
# Voir les logs en direct
sudo docker compose logs -f app

# Statut des containers
sudo docker compose ps

# Redémarrer l'app
sudo docker compose restart app

# Arrêter tout
sudo docker compose down

# Accéder à la base PostgreSQL
sudo docker exec -it agrement_fiche-db-1 psql -U postgres -d agrement

# Vérifier les variables d'environnement du container
sudo docker exec agrement_fiche-app-1 env | grep GCS
sudo docker exec agrement_fiche-app-1 env | grep GOOGLE

# Tester l'accès au bucket GCS depuis le container
sudo docker exec agrement_fiche-app-1 python3 -c "
from google.cloud import storage
c = storage.Client.from_service_account_json('/run/secrets/gcp-key.json')
b = c.bucket('NOM_DU_BUCKET')
print('Bucket existe:', b.exists())
"
```

---

## Architecture

```
VPS
├── Docker : app Streamlit         → port 8502
├── Docker : PostgreSQL            → port 5432 (interne)
└── GCS Bucket : fiches techniques → ramery-ai-features-fiches-produit-fournisseur

Local (dev)
├── Streamlit direct               → python -m streamlit run app.py
└── SQLite                         → agrement.db
```

---

## Schéma base de données

```
projects         agrements                products          suppliers
─────────        ──────────────────────   ────────────────  ─────────
id (PK)          id (PK)                  id (PK)           id (PK)
name             number                   designation       name
conducteur       project_id → projects    supplier_name
created_at       designation              category
                 supplier_name            datasheet_url ──→ GCS
                 category
                 submitted_by
                 submitted_at
                 status
```

- `products.datasheet_url` : blob GCS de la fiche technique (ex: `datasheets/product_xxx.pdf`)
- La fiche technique est liée au **produit**, pas à l'agrément — elle s'applique à tous les chantiers

---

## Stack technique

| Composant | Technologie |
|---|---|
| Frontend / Backend | Streamlit |
| Base de données (prod) | PostgreSQL 16 |
| Base de données (dev) | SQLite |
| ORM | SQLAlchemy 2.x |
| Stockage fiches techniques | Google Cloud Storage |
| Génération PDF (DOE) | reportlab + pypdf |
| Conteneurisation | Docker + Docker Compose |
| Repo | github.com/waelbouzoubaa/agrement_fiche |

---

## Workflow quotidien

```
Développement local          VPS production
──────────────────           ──────────────
python -m streamlit          
  run app.py          →push→  git pull
SQLite (agrement.db)          docker compose up -d --build
GCS bucket (même)             PostgreSQL + GCS bucket (même)
```
