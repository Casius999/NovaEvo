# Guide de démarrage rapide - NovaEvo

Ce guide est conçu pour vous aider à démarrer rapidement avec le projet NovaEvo en tant que nouveau développeur ou contributeur. Il vous guidera à travers les étapes essentielles pour configurer votre environnement de développement et comprendre la structure du projet.

## 1. Prérequis

Avant de commencer, assurez-vous d'avoir installé les logiciels suivants :

- **Git** - Pour la gestion de version
- **Python 3.10+** - Pour le backend
- **Node.js 18+** - Pour le frontend
- **Docker et Docker Compose** (optionnel) - Pour l'environnement conteneurisé

## 2. Mise en place de l'environnement de développement

### Cloner le dépôt

```bash
git clone https://github.com/Casius999/NovaEvo.git
cd NovaEvo
```

### Configurer l'environnement Python

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
## Sur Windows
venv\\Scripts\\activate
## Sur macOS/Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Configurer le frontend

```bash
cd frontend
npm install
cd ..
```

### Configurer les variables d'environnement

```bash
cp .env.example .env
```

Ouvrez le fichier `.env` dans un éditeur de texte et configurez les variables nécessaires :

- `GOOGLE_APPLICATION_CREDENTIALS` - Chemin vers votre fichier de clés Google Cloud
- `OPENAI_API_KEY` - Votre clé API OpenAI pour le NLP
- `STRIPE_API_KEY` - Votre clé API Stripe pour les abonnements

**Note** : Pour une liste complète et détaillée de tous les credentials nécessaires, consultez notre [Guide des Credentials](CREDENTIALS_GUIDE.md) qui fournit une documentation exhaustive de toutes les clés API, tokens et secrets requis par chaque module, ainsi que les plans de secours en cas d'indisponibilité.

## 3. Premiers pas avec le code

### Structure des modules

L'application est divisée en modules fonctionnels :

- **OCR** (`/ocr`) - Reconnaissance de cartes grises
- **OBD-II** (`/obd2`) - Diagnostic du véhicule
- **NLP** (`/nlp`) - Traitement du langage naturel
- **Image Recognition** (`/image_recognition`) - Analyse d'images
- **ECU Flash** (`/ecu_flash`) - Reprogrammation de l'ECU
- **Parts Finder** (`/parts_finder`) - Recherche de pièces
- **Subscriptions** (`/subscriptions`) - Gestion des abonnements
- **Mapping Affiliations** (`/mapping_affiliations`) - Affiliation de cartographies
- **Frontend** (`/frontend`) - Interface utilisateur

### Lancer l'application

```bash
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm start
```

L'application sera disponible sur :
- Backend : http://localhost:5000
- Frontend : http://localhost:3000

## 4. Workflow de développement

### Processus de contribution

1. **Créer une branche** pour votre fonctionnalité ou correctif
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```

2. **Effectuer vos modifications** dans cette branche

3. **Exécuter les tests** pour vérifier que vos modifications n'ont pas cassé quelque chose
   ```bash
   pytest
   ```

4. **Soumettre une Pull Request** sur GitHub

### Conseils de développement

- Consultez la [documentation d'architecture hiérarchique](ARCHITECTURE_HIERARCHIQUE.md) et [architecture modulaire](ARCHITECTURE_MODULAIRE.md) pour comprendre les interactions entre les modules
- Chaque module a sa propre documentation détaillée dans le dossier `/docs`
- Utilisez les tests existants comme référence pour comprendre le comportement attendu des modules
- Pour les nouvelles fonctionnalités, ajoutez toujours des tests unitaires correspondants

## 5. Tests et débogage

### Exécuter les tests

```bash
# Exécuter tous les tests
pytest

# Exécuter les tests d'un module spécifique
pytest tests/test_ocr.py
```

### Débogage

Pour le débogage, vous pouvez utiliser :

- `print()` pour les logs rapides
- `pdb` pour le débogage interactif en Python
- Les outils de développement du navigateur pour le frontend
- Des outils comme Postman pour tester l'API

## 6. Développement avec Docker

Si vous préférez utiliser Docker :

```bash
# Construire et démarrer les conteneurs
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les conteneurs
docker-compose down
```

## 7. Accès et Credentials

Pour accéder à tous les services et API nécessaires au développement :

1. Consultez le [Guide des Credentials](CREDENTIALS_GUIDE.md) pour une liste exhaustive de tous les accès requis
2. Demandez les credentials de développement à l'administrateur du projet
3. Stockez les credentials de manière sécurisée, sans jamais les inclure dans le code source
4. Utilisez Google Cloud Secret Manager ou AWS Secrets Manager pour la gestion des secrets en production

### Rotation des Credentials

- Tous les credentials de développement sont régulièrement renouvelés (tous les 90 jours)
- Suivez les procédures documentées dans le Guide des Credentials pour la mise à jour

## 8. Références utiles

- [Documentation complète du projet](README.md)
- [Architecture Hiérarchique](ARCHITECTURE_HIERARCHIQUE.md)
- [Processus Opérationnels](PROCESSUS_OPERATIONNELS.md)
- [Pipeline CI/CD](PIPELINE_CICD.md)
- [Sécurité et Conformité](SECURITE_CONFORMITE.md)
- [Guide de Développement Complet](GUIDE_DEVELOPPEMENT_COMPLET.md)

## 9. Besoin d'aide ?

Si vous avez des questions ou rencontrez des difficultés :

- Consultez la documentation existante
- Vérifiez les issues GitHub (ouvertes et fermées)
- Contactez l'équipe via les canaux de communication internes

Bonne contribution au projet NovaEvo !