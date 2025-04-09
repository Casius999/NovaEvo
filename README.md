# Assistant Auto Ultime

## Description
Assistant Auto Ultime est une plateforme complète pour les passionnés et professionnels de l'automobile, intégrant des fonctionnalités avancées d'OCR, de diagnostic OBD-II, de traitement du langage naturel, de reconnaissance d'images, de reprogrammation ECU et de recherche de pièces détachées. La plateforme propose désormais un système d'abonnement et un service d'affiliation global pour tous les achats effectués via l'application.

## Objectifs
- Simplifier le diagnostic automobile via une interface intuitive
- Automatiser la reconnaissance des informations de carte grise
- Fournir un accès direct aux données OBD-II du véhicule
- Permettre l'interaction par commandes vocales naturelles
- Offrir un diagnostic visuel via reconnaissance d'images
- Faciliter la reprogrammation ECU pour l'optimisation des performances
- Proposer un catalogue complet de pièces détachées (origine, sport, compétition)
- **NOUVEAU** : Offrir un service d'abonnement avec dongle OBD-II inclus
- **NOUVEAU** : Implémenter un système d'affiliation global assurant le suivi de 100% des achats réalisés via l'application

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
- `/subscriptions` - **NOUVEAU** : Système de gestion des abonnements avec Stripe
- `/mapping_affiliations` - **NOUVEAU** : Module d'affiliation global pour tous les achats

## Documentation Stratégique et Financière
- [Plan Financier](docs/FINANCIAL_PLAN.md) - Plan financier prévisionnel sur 3 ans
- [Stratégie d'Optimisation des Coûts](docs/COST_OPTIMIZATION_SUMMARY.md) - Approche d'optimisation financière
- [Architecture Serverless](docs/ARCHITECTURE_SERVERLESS.md) - Solution technique optimisée
- [Modèle d'Affiliation](docs/AFFILIATION_FINANCES.md) - Projections du système d'affiliation
- [Stratégie d'Investissement](docs/INVESTMENT_STRATEGY.md) - Plan de financement et valorisation

## Installation

### Prérequis
- Python 3.10+
- Node.js 18+
- Docker et Docker Compose
- Accès à un dongle OBD-II compatible (optionnel pour le développement)
- Interface de flashage ECU (ex: Tactrix Openport) pour le module de reprogrammation
- Clés API pour Google Cloud Vision (OCR) et OpenAI (NLP)
- **NOUVEAU** : Compte Stripe pour le système d'abonnement
- **NOUVEAU** : Clés API pour les services d'affiliation

### Installation avec environnement virtuel Python

1. **Cloner le dépôt**
```bash
git clone https://github.com/Casius999/assistant-auto-ultime.git
cd assistant-auto-ultime
```

2. **Créer et activer un environnement virtuel**
```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\\Scripts\\activate
```

3. **Installer les dépendances backend**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditez le fichier .env avec vos clés API et configurations
```

5. **Installer les dépendances frontend**
```bash
cd frontend
npm install
cd ..
```

6. **Démarrer l'application en mode développement**
```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend
cd frontend
npm start
```

### Installation avec Docker

Pour un déploiement complet avec Docker :

1. **Cloner le dépôt**
```bash
git clone https://github.com/Casius999/assistant-auto-ultime.git
cd assistant-auto-ultime
```

2. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditez le fichier .env avec vos clés API et configurations
```

3. **Lancer avec Docker Compose**
```bash
docker-compose up -d
```

L'application sera disponible sur :
- Backend API: http://localhost:5000
- Frontend: http://localhost:3000

## Guide de démarrage rapide

Pour les nouveaux développeurs ou contributeurs, nous avons préparé un [guide de démarrage rapide](docs/GETTING_STARTED.md) détaillé qui vous guidera pas à pas dans la mise en place de votre environnement de développement et la prise en main du projet.

## Architecture du système

L'application est construite selon une architecture modulaire qui facilite la maintenance et l'évolution. Pour une compréhension approfondie des interactions entre les différents modules, veuillez consulter notre [documentation d'architecture](docs/ARCHITECTURE.md).

## Déploiement en production

Pour déployer l'application en environnement de production, suivez ces étapes :

### 1. Configuration HTTPS

La sécurité en production est essentielle, surtout pour les fonctionnalités comme l'accès à la caméra (OCR) et l'authentification des utilisateurs.

1. **Acquérir un certificat SSL**
   - Utilisez Let's Encrypt pour un certificat gratuit ou achetez-en un auprès d'une autorité de certification
   - Placez les fichiers de certificat (cert.pem, key.pem) dans un répertoire sécurisé

2. **Configuration du serveur web**
   - **Avec Nginx** :
     ```
     server {
         listen 443 ssl;
         server_name votre-domaine.com;
         
         ssl_certificate /chemin/vers/cert.pem;
         ssl_certificate_key /chemin/vers/key.pem;
         
         # Redirection du frontend
         location / {
             proxy_pass http://localhost:3000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
         
         # Redirection de l'API
         location /api/ {
             proxy_pass http://localhost:5000/;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
     }
     
     # Redirection HTTP vers HTTPS
     server {
         listen 80;
         server_name votre-domaine.com;
         return 301 https://$host$request_uri;
     }
     ```

### 2. Variables d'environnement sécurisées

En production, ne stockez jamais les variables d'environnement directement dans des fichiers :

1. **Serveur dédié ou VPS**
   - Utilisez des variables d'environnement système
   - Configurez-les dans le fichier de service systemd

2. **Conteneurs Docker**
   - Utilisez Docker Secrets ou un service de gestion de secrets (HashiCorp Vault, AWS Secrets Manager)
   - Exemple avec Docker Compose et secrets :
     ```yaml
     version: '3.8'
     services:
       app:
         image: assistant-auto-ultime-backend
         secrets:
           - google_api_key
           - openai_api_key
           - stripe_api_key
         environment:
           - GOOGLE_API_KEY_FILE=/run/secrets/google_api_key
           - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key
           - STRIPE_API_KEY_FILE=/run/secrets/stripe_api_key
     
     secrets:
       google_api_key:
         file: ./secrets/google_api_key.txt
       openai_api_key:
         file: ./secrets/openai_api_key.txt
       stripe_api_key:
         file: ./secrets/stripe_api_key.txt
     ```

Pour des instructions plus détaillées sur le déploiement, consultez notre [guide de déploiement](docs/DEPLOYMENT.md).

## Utilisation des modules

### OCR - Reconnaissance de Carte Grise
Ce module utilise Google Cloud Vision pour scanner et extraire les informations d'une carte grise.
```python
from ocr import OCRProcessor

# Initialiser le module OCR
ocr = OCRProcessor()

# Traiter une image
result = ocr.process_image(image_path="path/to/image.jpg")
vehicle_info = ocr.extract_vehicle_info(result)
print(vehicle_info)
```

### OBD-II - Diagnostic Véhicule
Module de connexion avec un dongle OBD-II pour obtenir des informations en temps réel du véhicule.
```python
from obd2 import OBDManager

# Initialiser le gestionnaire OBD
obd_manager = OBDManager()

# Se connecter au véhicule
obd_manager.connect()

# Obtenir le RPM actuel
rpm = obd_manager.get_rpm()
print(f"RPM actuel: {rpm}")

# Lire les codes d'erreur
codes = obd_manager.get_dtc_codes()
print(f"Codes d'erreur: {codes}")
```

### NLP - Assistant Langage Naturel
Module de traitement du langage naturel permettant d'interpréter des questions et commandes en langage courant.
```python
from nlp import AutoAssistantNLP

# Initialiser l'assistant NLP
nlp = AutoAssistantNLP()

# Interpréter une requête
result = nlp.interpret_command("Que signifie le code erreur P0300 ?")
print(result)
```

### ECU Flash - Reprogrammation de l'ECU
Module permettant la lecture et la modification des paramètres de l'ECU pour l'optimisation des performances moteur.
```python
from ecu_flash.ecu_flash_main import flash_ecu, ECUFlashManager

# Initialiser le gestionnaire ECU
ecu_manager = ECUFlashManager()

# Connexion à l'ECU
connect_result = ecu_manager.connect_ecu()
print(f"Connexion: {connect_result['message']}")

# Flasher l'ECU avec des paramètres personnalisés
params = {
    "cartographie_injection": 105,  # 5% d'augmentation
    "boost_turbo": 1.1  # 10% d'augmentation
}
result = flash_ecu(params)
print(f"Résultat: {result['message']}")
```

### Parts Finder - Recherche de pièces détachées
Module pour rechercher des pièces détachées via différentes sources (API officielles et scraping).
```python
from parts_finder.parts_finder_main import search_parts

# Rechercher des pièces
results = search_parts(reference="F-001", type_piece="sport")
for result in results:
    print(f"{result['name']} - {result['price']} {result['currency']} - {result['source']}")
```

### Subscriptions - Gestion des abonnements (NOUVEAU)
Module de gestion des abonnements utilisant Stripe pour les paiements récurrents.
```python
from subscriptions.subscriptions_main import process_subscription

# Créer un abonnement pour un utilisateur
user_data = {
    "email": "utilisateur@example.com",
    "password": "motdepasse123",
    "name": "John Doe",
    "plan_id": "price_basic"  # Plan à 19,90€/mois
}
result = process_subscription(user_data)
print(f"Abonnement créé: {result}")
```

### Affiliations - Système d'affiliation global (NOUVEAU)
Module d'affiliation pour tous les achats réalisés via l'application.
```python
from mapping_affiliations.affiliations_main import track_purchase

# Exemple de suivi d'achat
purchase_data = {
    "product_type": "cartographie",  # Type de produit (cartographie, pièce, accessoire, etc.)
    "product_id": "cart-123",        # ID du produit
    "price": 299.90,                 # Prix
    "partner_id": "partner-456",     # ID du partenaire
    "user_id": "user-789",           # ID de l'utilisateur
    "session_id": "sess-abc123"      # ID de session pour le tracking
}
tracking_result = track_purchase(purchase_data)
print(f"Suivi d'achat: {tracking_result}")
```

### Tests unitaires
Pour exécuter les tests unitaires :
```bash
# Installer pytest
pip install pytest

# Lancer tous les tests
pytest

# Lancer les tests d'un module spécifique
pytest tests/test_ecu_flash.py
```

## API Rest

L'application expose les endpoints principaux suivants :

- `GET /` - Page d'accueil / Statut de l'API
- `POST /ocr` - Analyse OCR d'une image
- `GET /obd2` - Récupère les données OBD-II
- `POST /nlp` - Interprète une requête en langage naturel
- `POST /image_recognition` - Analyse une image pour diagnostic
- `POST /ecu_flash` - Flash l'ECU avec des paramètres spécifiques
- `POST /ecu_flash/connect` - Établit une connexion avec l'ECU
- `GET /ecu_flash/read` - Lit la configuration actuelle de l'ECU
- `GET /ecu_flash/parameters` - Récupère les limites de paramètres disponibles
- `POST /parts_finder` - Recherche de pièces détachées
- `POST /subscribe` - **NOUVEAU** : Souscription à un abonnement Stripe
- `GET /subscribe/plans` - **NOUVEAU** : Récupère les plans d'abonnement disponibles
- `POST /subscribe/webhook` - **NOUVEAU** : Gestion des webhooks Stripe
- `POST /affiliations/track` - **NOUVEAU** : Suivi d'achat pour l'affiliation

Consultez la documentation complète de l'API dans le fichier [api.md](docs/api.md).

## Internationalisation

L'Assistant Auto Ultime prend en charge plusieurs langues. Pour contribuer aux traductions ou ajouter une nouvelle langue, consultez notre [guide d'internationalisation](docs/INTERNATIONALIZATION.md).

## Fonctionnalités commerciales (NOUVEAU)

### Abonnements
Le service propose désormais un modèle commercial basé sur l'abonnement :

- **Abonnement Standard** : 19,90€/mois
  - Dongle OBD-II offert à l'inscription
  - Accès à toutes les fonctionnalités de diagnostic
  - Support technique par email

- **Abonnement Premium** : 29,90€/mois
  - Toutes les fonctionnalités de l'abonnement Standard
  - Dongle OBD-II Pro offert à l'inscription
  - Cartographies moteur avancées
  - Flash ECU illimité
  - Support technique prioritaire

### Système d'affiliation global
L'application intègre un système d'affiliation pour tous les produits et services proposés :

- **Tracking robuste** pour le suivi des achats effectués via l'application
- Infrastructure de redirections sécurisées, cookies et fingerprinting d'appareil
- Attribution des commissions sur les transactions
- S'applique à l'ensemble des produits : cartographies moteur, pièces détachées, accessoires, etc.
- Sources multiples : API partenaires, marketplaces, boutiques en ligne spécialisées

## Documentation détaillée des modules

Des guides d'utilisation complets sont disponibles pour chaque module :

- [Module OCR](docs/README_OCR.md)
- [Module OBD-II](docs/README_OBD.md)
- [Module NLP](docs/README_NLP.md)
- [Module Image Recognition](docs/README_Image_Recognition.md)
- [Module ECU Flash](docs/README_ECU_FLASH.md)
- [Module Parts Finder](docs/README_PARTS_FINDER.md)
- [Module Subscriptions](docs/README_SUBSCRIPTIONS.md) - **NOUVEAU**
- [Module Affiliations](docs/README_MAPPING_AFFILIATIONS.md) - **NOUVEAU**
- [Frontend](docs/README_FRONTEND.md)

## Précautions d'utilisation

⚠️ **ATTENTION** ⚠️

La modification des paramètres de l'ECU via le module ECU Flash peut :
- Affecter les performances et la fiabilité du véhicule
- Augmenter l'usure du moteur et des composants connexes
- Annuler la garantie du constructeur
- Rendre le véhicule non conforme aux réglementations environnementales

Utilisez ces fonctionnalités uniquement si vous comprenez les risques associés.

## Contribution
Veuillez consulter le fichier [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails sur notre code de conduite et le processus de soumission des pull requests.

Pour les nouveaux contributeurs, nous recommandons de commencer par la consultation du [guide de démarrage rapide](docs/GETTING_STARTED.md).

## Feuille de route
Pour connaître les prochaines étapes du développement, consultez notre [ROADMAP.md](ROADMAP.md) détaillée.

## Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.