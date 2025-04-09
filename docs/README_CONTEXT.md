# NovaEvo - Module de Contexte et Synchronisation

Le module de contexte permet à NovaEvo d'enrichir les données et fonctionnalités de base en se connectant à des serveurs de données spécialisés. Cette documentation explique comment configurer, utiliser et étendre le système de contexte.

## Table des matières

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [Types de Contextes](#types-de-contextes)
5. [Utilisation du Module](#utilisation-du-module)
6. [Sécurité](#sécurité)
7. [Développement et Extension](#développement-et-extension)
8. [Métriques et Performance](#métriques-et-performance)
9. [Dépannage](#dépannage)

## Introduction

Le système de contexte est conçu pour permettre à NovaEvo d'accéder à des informations externes actualisées sans nécessiter de mises à jour de l'application elle-même. Il s'agit d'une architecture client-serveur où l'application NovaEvo agit comme un client qui interroge des serveurs spécialisés pour obtenir des données contextuelles.

Les avantages de cette approche sont:
- Données toujours à jour sans mise à jour de l'application
- Enrichissement continu de l'expérience utilisateur
- Séparation des préoccupations entre l'application et les données
- Possibilité d'ajouter de nouveaux types de contextes sans modifier l'application

## Architecture

Le système de contexte s'articule autour de trois composants principaux:

1. **Gestionnaire de Contexte**: Coordonne la communication avec les serveurs, gère le cache et expose les API pour accéder aux données.
2. **Modules Contextuels**: Représentent les différentes sources de données (codes DTC, données véhicules, etc.)
3. **Vérificateur de Sécurité**: Assure l'authenticité et l'intégrité des données reçues.

Le flux de données est le suivant:
1. L'application demande des données au gestionnaire de contexte
2. Le gestionnaire vérifie si les données sont disponibles en cache et à jour
3. Si nécessaire, il contacte le serveur contextuel approprié
4. Le vérificateur de sécurité valide l'authenticité des données
5. Les données sont mises en cache et retournées à l'application

## Configuration

### Variables d'environnement

Configurez les serveurs contextuels dans votre fichier `.env`:

```
# Liste des serveurs de contexte séparés par des virgules
CONTEXT_SERVERS=https://api.example.com/dtc_database,https://api.example.com/vehicles_data

# Intervalle de synchronisation en secondes (défaut: 300s = 5 minutes)
SYNC_INTERVAL=300

# Clés API pour chaque serveur (remplacez MODULE_ID par l'identifiant du module)
API_KEY_DTC_DATABASE=your_api_key_for_dtc_database
API_KEY_VEHICLES_DATA=your_api_key_for_vehicles_data
```

### Activation de la synchronisation automatique

La synchronisation automatique est activée par défaut si des serveurs sont définis. Pour la désactiver:

```python
# Dans votre code d'initialisation de l'application
from utils.context_sync import context_manager
context_manager.stop_background_sync()
```

## Types de Contextes

NovaEvo prend en charge les types de contexte suivants:

### DTC Database
Base de données des codes d'erreur (Diagnostic Trouble Codes) avec:
- Descriptions détaillées
- Causes possibles
- Étapes de résolution
- Niveaux de sévérité

### Vehicles Data
Informations techniques sur les véhicules:
- Spécifications des modèles
- Compatibilité des pièces
- Références constructeur
- Informations de maintenance

### Parts Database
Catalogue de pièces détachées:
- Références et équivalences
- Prix recommandés
- Disponibilité
- Compatibilité inter-marques

### Repair Shops
Réseau de professionnels et ateliers:
- Coordonnées et spécialités
- Disponibilités et créneaux
- Évaluations et certifications
- Tarifs standards

### ECU Compatibility
Matrices de compatibilité pour le flashage ECU:
- Limites sécurisées par modèle
- Compatibilités matérielles
- Versions de firmware
- Précautions spécifiques

## Utilisation du Module

### Import et initialisation

```python
from utils.context_sync import context_manager

# Vérifier si un module est disponible
if "dtc_database" in context_manager.modules:
    # Utiliser le module
    pass
```

### Récupération des données contextuelles

```python
# Format simple
dtc_info = context_manager.get_context_data("dtc_database", "codes.P0300")

# Utilisation dans une fonction
def get_dtc_description(code):
    return context_manager.get_context_data("dtc_database", f"codes.{code}.description")

# Récupération de toutes les données d'un module
all_vehicle_data = context_manager.get_context_data("vehicles_data")
```

### Synchronisation manuelle

```python
# Synchroniser un module spécifique
context_manager.sync_module("dtc_database")

# Synchroniser tous les modules
results = context_manager.sync_all_modules()
print(f"Résultats: {results}")

# Forcer la synchronisation même si récemment synchronisé
context_manager.sync_module("vehicles_data", force=True)
```

### Vérification de l'état

```python
# Obtenir l'état d'un module
status = context_manager.get_module_status("dtc_database")
print(f"Status: {status['status']}, Dernière synchronisation: {status['last_sync']}")

# Obtenir l'état de tous les modules
all_status = context_manager.get_all_modules_status()
```

## Sécurité

### Vérification des sources

Le système vérifie l'authenticité des serveurs de contexte en utilisant:
- Validation des certificats TLS
- Vérification des empreintes cryptographiques
- Authentification par clé API
- Signatures des données

### Blacklisting

Les serveurs suspects sont automatiquement mis sur liste noire:
```python
from utils.security_check import security_checker

# Vérifier manuellement un serveur
result = security_checker.verify_server("https://api.example.com/dtc_database")
if result["overall_status"] != "passed":
    print(f"Attention! Serveur suspect: {result['checks']}")

# Mettre manuellement un serveur sur liste noire
security_checker.blacklist_server("https://malicious-server.com", "Source non fiable")
```

## Développement et Extension

### Ajout d'un nouveau type de contexte

1. Implémentez un serveur API conforme aux spécifications
2. Ajoutez l'URL du serveur à la liste CONTEXT_SERVERS
3. Ajoutez la clé API correspondante (si nécessaire)
4. Redémarrez l'application ou appelez context_manager.sync_all_modules()

### Création d'un serveur de contexte compatible

Un serveur de contexte doit exposer les endpoints suivants:
- `GET /api/data`: Retourne toutes les données contextuelles au format JSON
- `GET /api/fingerprint`: Retourne l'empreinte cryptographique du serveur
- `GET /api/security-check`: Retourne les informations de sécurité du serveur
- `GET /api/health`: Endpoint de vérification de l'état du serveur

## Métriques et Performance

### Monitoring

Le système enregistre automatiquement des métriques de performance:
- Temps de réponse des serveurs
- Taux de succès des synchronisations
- Volume de données transférées
- Utilisation du cache

### Optimisation

Pour optimiser les performances:
- Augmentez l'intervalle de synchronisation pour les données rarement modifiées
- Utilisez des chemins spécifiques pour récupérer uniquement les données nécessaires
- Activez la compression des réponses au niveau du serveur

## Dépannage

### Problèmes courants

1. **Données non disponibles**
   - Vérifiez que le module est enregistré et synchronisé
   - Vérifiez le chemin d'accès aux données
   - Consultez les logs pour les erreurs de synchronisation

2. **Erreurs de synchronisation**
   - Vérifiez la connectivité réseau
   - Vérifiez que les clés API sont correctes
   - Consultez les logs pour les messages d'erreur détaillés

3. **Performance lente**
   - Réduisez le nombre de serveurs contextuels
   - Augmentez l'intervalle de synchronisation
   - Utilisez des chemins spécifiques plutôt que de récupérer toutes les données

### Logs

Les logs du système de contexte sont disponibles dans le fichier de log principal avec le préfixe "novaevo.context_sync".
