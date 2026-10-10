#!/usr/bin/env bash
# ============================================
# build.sh — Script de build pour Render
# ============================================
# Ce script est exécuté à chaque déploiement.
# Il installe les dépendances, collecte les
# fichiers statiques et applique les migrations.
# ============================================

set -o errexit    # Stoppe le script en cas d'erreur
set -o pipefail   # Propage les erreurs dans les pipes
set -o nounset    # Stoppe si une variable non définie est utilisée

echo "🚀 Démarrage du build UniBus..."

# ============================================
# 1. Installer les dépendances Python
# ============================================
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# ============================================
# 2. Appliquer les migrations
# ============================================
echo "🔄 Application des migrations..."
python manage.py migrate --noinput

# ============================================
# 3. Collecter les fichiers statiques
# ============================================
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

# ============================================
# 4. Créer un superutilisateur (optionnel)
# ============================================
# Décommenter si tu veux créer un superuser
# automatiquement au premier déploiement.
#
# if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && \
#    [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && \
#    [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
#     echo "👤 Création du superutilisateur..."
#     python manage.py createsuperuser --noinput || true
# fi

echo "✅ Build terminé avec succès !"