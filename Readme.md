

# 🚌 UniBus — Suivi Transport Universitaire

Application SaaS de suivi en temps réel des bus universitaires.

## Stack technique

- **Backend** : Django 5+ + Django Channels (ASGI)
- **Temps réel** : Redis + WebSockets
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **PWA** : Manifest + Service Worker + Pop-up d'installation
- **Frontend** : TailwindCSS + DaisyUI + Alpine.js + Font Awesome

## 🚀 Développement local

### 1. Prérequis

- Python 3.12+
- Redis (via WSL2, Memurai ou Docker)
- Git

### 2. Installation

```bash
# Cloner le repo
git clone https://github.com/ton-user/unibus.git
cd unibus

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier .env.example vers .env
cp .env.example .env
# Puis éditer .env avec tes vraies valeurs