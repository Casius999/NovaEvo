# Assistant Auto Ultime

## Description
Assistant Auto Ultime est une plateforme complète pour les passionnés et professionnels de l'automobile, intégrant des fonctionnalités avancées d'OCR, de diagnostic OBD-II, de traitement du langage naturel, de reconnaissance d'images, de reprogrammation ECU et de recherche de pièces détachées.

## Objectifs
- Simplifier le diagnostic automobile via une interface intuitive
- Automatiser la reconnaissance des informations de carte grise
- Fournir un accès direct aux données OBD-II du véhicule
- Permettre l'interaction par commandes vocales naturelles
- Offrir un diagnostic visuel via reconnaissance d'images
- Faciliter la reprogrammation ECU pour l'optimisation des performances
- Proposer un catalogue complet de pièces détachées (origine, sport, compétition)

## Structure du dépôt
- `/ocr` - Module de scan OCR pour la carte grise
- `/obd2` - Module de connexion avec le dongle OBD-II
- `/nlp` - Module de traitement du langage naturel (chat et commandes vocales)
- `/image_recognition` - Reconnaissance d'image pour le diagnostic visuel
- `/ecu_flash` - Module de reprogrammation ECU (tuning & flash)
- `/parts_finder` - Recherche de pièces détachées (OEM, sport, compétition)
- `/frontend` - Interface utilisateur (Web/Mobile)
- `/docs` - Documentation complète du projet
- `/tests` - Tests unitaires et d'intégration

## Installation

### Prérequis
- Python 3.8+
- Node.js 14+
- Docker
- Accès à un dongle OBD-II compatible

### Installation rapide
```bash
# Cloner le dépôt
git clone https://github.com/Casius999/assistant-auto-ultime.git
cd assistant-auto-ultime

# Installer les dépendances
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Lancer l'application en mode développement
docker-compose up
```

## Contribution
Veuillez consulter le fichier [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails sur notre code de conduite et le processus de soumission des pull requests.

## Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.