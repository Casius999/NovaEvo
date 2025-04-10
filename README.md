# NovaEvo

## Description
NovaEvo est une plateforme complète pour les passionnés et professionnels de l'automobile, intégrant des fonctionnalités avancées d'OCR, de diagnostic OBD-II, de traitement du langage naturel, de reconnaissance d'images, de reprogrammation ECU et de recherche de pièces détachées. La plateforme propose désormais un système d'abonnement et un service d'affiliation global pour tous les achats effectués via l'application.

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
- **NOUVEAU** : Intégrer des modules contextuels avec synchronisation en temps réel
- **NOUVEAU** : Planifier automatiquement des rendez-vous avec des professionnels qualifiés
- **NOUVEAU** : Garantir une intégrité et une traçabilité totale des données via notre architecture hiérarchique

## Structure du dépôt
- `/ocr` - Module de scan OCR pour la carte grise
- `/obd2` - Module de connexion avec le dongle OBD-II
- `/nlp` - Module de traitement du langage naturel (chat et commandes vocales)
- `/image_recognition` - Reconnaissance d'image pour le diagnostic visuel
- `/ecu_flash` - Module de reprogrammation ECU (tuning & flash)
- `/parts_finder` - Recherche de pièces détachées et planification de rendez-vous
- `/frontend` - Interface utilisateur (Web/Mobile)
- `/docs` - Documentation complète du projet
- `/tests` - Tests unitaires et d'intégration
- `/subscriptions` - Système de gestion des abonnements avec Stripe
- `/mapping_affiliations` - Module d'affiliation global pour tous les achats
- `/utils` - Utilitaires pour la gestion des contextes, métriques et sécurité

## Nouveautés - Version 3.0

### Modules Contextuels et Synchronisation
NovaEvo intègre désormais une architecture de synchronisation avec des serveurs dédiés pour enrichir l'expérience utilisateur avec des données contextuelles en temps réel :

- **Données Contextuelles** : Enrichissement des informations véhicules, codes d'erreur, pièces détachées et compatibilité ECU
- **Synchronisation Temps Réel** : Communication automatisée avec des serveurs tiers pour des données toujours à jour
- **Sécurité Renforcée** : Vérification cryptographique des sources de données et protection contre les altérations
- **Analyse de Performance** : Suivi et optimisation des performances pour une expérience fluide

### Planification Intelligente
Le nouveau système de planification automatique permet :

- **Création Dynamique de Créneaux** : Génération automatique de créneaux d'urgence basée sur la demande
- **Géolocalisation des Professionnels** : Identification des garages et techniciens à proximité
- **Priorisation des Urgences** : Traitement accéléré des interventions critiques
- **Suivi des Rendez-vous** : Notifications et rappels pour une gestion optimale

### Documentation Stratégique et Financière
- [Vision Stratégique](docs/NOVAEVO_VISION.md) - Vision globale et proposition de valeur
- [Plan Financier](docs/FINANCIAL_PLAN.md) - Plan financier prévisionnel sur 3 ans
- [Stratégie d'Optimisation des Coûts](docs/COST_OPTIMIZATION_SUMMARY.md) - Approche d'optimisation financière
- [Architecture Serverless](docs/ARCHITECTURE_SERVERLESS.md) - Solution technique optimisée
- [Modèle d'Affiliation](docs/AFFILIATION_FINANCES.md) - Projections du système d'affiliation
- [Stratégie d'Investissement](docs/INVESTMENT_STRATEGY.md) - Plan de financement et valorisation

### Documentation Architecture et Processus
- [Architecture Hiérarchique](docs/ARCHITECTURE_HIERARCHIQUE.md) - Architecture stratifiée à plusieurs niveaux
- [Architecture Modulaire](docs/ARCHITECTURE_MODULAIRE.md) - Structure modulaire bidimensionnelle
- [Processus Opérationnels](docs/PROCESSUS_OPERATIONNELS.md) - Workflows et mécanismes d'automatisation
- [Pipeline CI/CD](docs/PIPELINE_CICD.md) - Intégration continue et déploiement automatisé
- [Sécurité et Conformité](docs/SECURITE_CONFORMITE.md) - Stratégie de sécurité et gestion des risques
- [Système de Monitoring](docs/SYSTEME_MONITORING.md) - Surveillance temps réel multi-niveaux
- [Engagement Utilisateur](docs/ENGAGEMENT_UTILISATEUR.md) - Stratégies d'engagement et amélioration continue
- [Gouvernance Collaborative](docs/GOUVERNANCE_COLLABORATIVE.md) - **NOUVEAU** : Organisation, rôles et processus de collaboration

## Installation

### Prérequis
- Python 3.10+
- Node.js 18+
- Docker et Docker Compose
- Accès à un dongle OBD-II compatible (optionnel pour le développement)
- Interface de flashage ECU (ex: Tactrix Openport) pour le module de reprogrammation
- Clés API pour Google Cloud Vision (OCR) et OpenAI (NLP)
- Compte Stripe pour le système d'abonnement
- Clés API pour les services d'affiliation
- **NOUVEAU** : Accès aux serveurs de contexte (optionnel pour le développement)

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

NovaEvo est construit selon une architecture hiérarchique et modulaire innovante qui garantit robustesse, flexibilité et évolutivité. Cette architecture stratifiée opère sur quatre niveaux clés permettant une gestion optimale de l'ensemble de l'écosystème:

- **Niveau Stratégique**: Intelligence décisionnelle, gouvernance systémique et optimisation stratégique
- **Niveau Tactique**: Orchestration des services, analyse contextuelle et synchronisation multicanale
- **Niveau Opérationnel**: Exécution des modules, monitoring temps réel et intégration continue
- **Niveau Fondamental**: Infrastructure technique, sécurité & conformité et persistance des données

Cette structure bidimensionnelle intègre à la fois des modules verticaux (fonctionnalités métier) et des composants horizontaux (services partagés) pour une cohérence globale et une gestion efficiente des ressources. Pour une compréhension approfondie, consultez notre [documentation d'architecture hiérarchique](docs/ARCHITECTURE_HIERARCHIQUE.md) et [architecture modulaire](docs/ARCHITECTURE_MODULAIRE.md).

## Modules Contextuels et Synchronisation

### Configuration des Serveurs Contextuels
Pour utiliser les modules contextuels, configurez les variables d'environnement suivantes :
```
CONTEXT_SERVERS=https://api.example.com/dtc_database,https://api.example.com/vehicles_data
SYNC_INTERVAL=300  # En secondes (5 minutes par défaut)
API_KEY_DTC_DATABASE=your_api_key_for_dtc_database
API_KEY_VEHICLES_DATA=your_api_key_for_vehicles_data
```

### Types de Contextes Disponibles
- **DTC Database** : Informations détaillées sur les codes d'erreur (DTC)
- **Vehicles Data** : Données techniques des véhicules (modèles, moteurs, etc.)
- **Parts Database** : Catalogue et compatibilité des pièces détachées
- **Repair Shops** : Réseau de professionnels et ateliers partenaires
- **ECU Compatibility** : Matrices de compatibilité pour le flashage ECU

### Mécanismes de Synchronisation
Le système implémente une synchronisation intelligente avec vérification cryptographique des sources:
- Synchronisation périodique configurable
- Synchronisation à la demande pour données critiques
- Vérification d'intégrité des données
- Persistance locale pour mode hors ligne
- Résolution automatique des conflits

## Planification Automatique et Gestion des Ressources

NovaEvo intègre un système avancé de planification intelligente et d'allocation dynamique des ressources:

### Planification de Rendez-vous
1. **Recherche par proximité** : Identification géolocalisée des professionnels qualifiés
2. **Priorisation intelligente** : Gestion des urgences avec créneaux prioritaires selon criticité
3. **Création dynamique de disponibilités** : Allocation adaptative lors des pics de demande
4. **Optimisation logistique** : Coordination entre disponibilité des pièces et des techniciens
5. **Confirmation multicanale** : Suivi automatisé des rendez-vous avec rappels intelligents

### Allocation Dynamique des Ressources
- **Monitoring continu** : Surveillance permanente de tous les composants du système
- **Allocation proactive** : Anticipation des besoins avant saturation des ressources
- **Priorisation contextuelle** : Distribution intelligente selon criticité et impact
- **Escalade automatique** : Mécanismes de transfert vers niveaux d'expertise supérieurs

Pour utiliser cette fonctionnalité, configurez les variables suivantes :
```
APPOINTMENT_API_ENABLED=True
APPOINTMENT_API_URL=https://api.scheduling.example.com
EMERGENCY_SLOTS_THRESHOLD=3  # Nombre minimum de créneaux d'urgence à maintenir
DYNAMIC_ALLOCATION=True       # Active l'allocation dynamique des agents
```

## Intégration Continue et Déploiement Automatisé

NovaEvo implémente un pipeline CI/CD robuste basé sur GitHub Actions et intégré avec Google Cloud Platform. Ce pipeline garantit qualité, fiabilité et déploiement continu:

### Phases du Pipeline
1. **Développement** : Commit, revue de code, analyse statique
2. **Build** : Compilation, construction de conteneurs, scan de sécurité
3. **Test** : Tests unitaires, d'intégration, fonctionnels, de performance et sécurité
4. **Staging** : Déploiement automatique, validation sur environnement préproduction
5. **Production** : Déploiement graduel (Blue/Green) avec vérification post-déploiement

### Approche de Test
NovaEvo suit une stratégie de test pyramidale:
- **Tests Unitaires** : >80% de couverture de code
- **Tests d'Intégration** : >70% des flux critiques
- **Tests Fonctionnels** : 100% des user stories
- **Tests de Performance** : Temps de réponse <200ms au P95
- **Tests de Sécurité** : 100% des API exposées

Pour plus de détails, consultez notre [documentation CI/CD complète](docs/PIPELINE_CICD.md).

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

### Planification de Rendez-vous (NOUVEAU)
Module pour trouver et planifier des rendez-vous avec des professionnels à proximité.
```python
from parts_finder.appointment_scheduler import scheduler

# Trouver des créneaux disponibles
location = {"latitude": 48.8566, "longitude": 2.3522}  # Paris
slots = scheduler.find_available_slots(location=location, radius=30.0)

# Trouver des créneaux d'urgence
emergency_slots = scheduler.find_emergency_slots(location=location, urgency_level="high")

# Planifier un rendez-vous
appointment = scheduler.schedule_appointment(
    slot_id=slots[0]["id"],
    vehicle_id="vehicle-123",
    service_type="diagnostic",
    user_id="user-456"
)
```

### Module de Contexte (NOUVEAU)
Utiliser les données contextuelles pour enrichir l'expérience utilisateur.
```python
from utils.context_sync import context_manager

# Récupérer des données contextuelles
dtc_data = context_manager.get_context_data("dtc_database", "codes.P0300")
vehicle_data = context_manager.get_context_data("vehicles_data", "vehicles.model-123")

# Synchroniser manuellement un module
context_manager.sync_module("dtc_database")

# Vérifier le statut des modules
status = context_manager.get_all_modules_status()
```

### Subscriptions - Gestion des abonnements
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

### Affiliations - Système d'affiliation global
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
- `POST /subscribe` - Souscription à un abonnement Stripe
- `GET /subscribe/plans` - Récupère les plans d'abonnement disponibles
- `POST /subscribe/webhook` - Gestion des webhooks Stripe
- `POST /mapping_affiliations/track` - Suivi d'achat pour l'affiliation
- `GET /context_modules` - Liste les modules contextuels disponibles
- `GET /context_modules/<module_id>` - Récupère les données d'un module contextuel
- `POST /context_modules/<module_id>/sync` - Force la synchronisation d'un module

Consultez la documentation complète de l'API dans le fichier [api.md](docs/api.md).

## Internationalisation

NovaEvo prend en charge plusieurs langues. Pour contribuer aux traductions ou ajouter une nouvelle langue, consultez notre [guide d'internationalisation](docs/INTERNATIONALIZATION.md).

## Fonctionnalités commerciales

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
- [Module Subscriptions](docs/README_SUBSCRIPTIONS.md)
- [Module Affiliations](docs/README_MAPPING_AFFILIATIONS.md)
- [Module Contexte](docs/README_CONTEXT.md) - **NOUVEAU**
- [Planification Automatique](docs/README_SCHEDULING.md) - **NOUVEAU**
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