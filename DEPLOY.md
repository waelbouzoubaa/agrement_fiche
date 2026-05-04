# Déploiement — Fiches d'Agrément Ramery

## Prérequis VPS

- Ubuntu 22.04+
- Docker + Docker Compose installés
- Git installé
- Port 8502 ouvert dans le firewall

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
scp ramery-ai-features-4f8f53eb767a.json user@IP_VPS:/tmp/gcp-key.json
```

Sur le VPS :

```bash
sudo mv /tmp/gcp-key.json /opt/agrement_fiche/gcp-key.json
```

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
GCS_BUCKET=ramery-ai-features-4f8f53eb767a
```

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
```

---

## Architecture

```
VPS
├── Docker : app Streamlit         → port 8502
├── Docker : PostgreSQL            → port 5432 (interne)
└── GCS Bucket : fiches techniques → ramery-ai-features-4f8f53eb767a

Local (dev)
├── Streamlit direct               → python -m streamlit run app.py
└── SQLite                         → agrement.db
```

## Stack technique

| Composant | Technologie |
|---|---|
| Frontend / Backend | Streamlit |
| Base de données (prod) | PostgreSQL 16 |
| Base de données (dev) | SQLite |
| ORM | SQLAlchemy 2.x |
| Stockage fichiers | Google Cloud Storage |
| PDF | reportlab + pypdf |
| Conteneurisation | Docker + Docker Compose |
