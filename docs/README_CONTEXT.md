# Module de Contexte NovaEvo

Le module de contexte est une composante essentielle de NovaEvo qui permet d'enrichir l'expérience utilisateur en intégrant des données contextuelles depuis des serveurs dédiés. Ces données sont utilisées pour fournir des informations précises et pertinentes sur les véhicules, les pièces, les codes d'erreur et autres éléments liés à l'automobile.

## Architecture

Le système de modules contextuels repose sur une architecture client-serveur sécurisée :

```
+---------------------+      HTTPS      +----------------------+
| NovaEvo Application | <-------------> | Serveurs Contextuels |
+---------------------+                 +----------------------+
        |                                         |
        | Cache local                             | API REST sécurisée
        |                                         |
+---------------------+                 +----------------------+
| Données persistantes| <---- Sync ---> | Bases de données     |
+---------------------+                 | spécialisées         |
                                        +----------------------+
```

## Modules Contextuels Disponibles

NovaEvo intègre plusieurs modules contextuels spécialisés :

| Module ID | Description | Données fournies |
|-----------|-------------|------------------|
| `dtc_database` | Base de données des codes d'erreur (DTC) | Descriptions détaillées, causes possibles, solutions recommandées pour les codes d'erreur |
| `vehicles_data` | Spécifications techniques des véhicules | Modèles, moteurs, spécifications, compatibilité des pièces |
| `parts_database` | Catalogue de pièces détachées | Références, compatibilité, prix de référence, alternatives |
| `repair_shops` | Réseau d'ateliers et professionnels | Coordonnées, spécialités, horaires, évaluations |
| `ecu_compatibility` | Matrice de compatibilité ECU | Compatibilité des reprogrammations ECU, limites sécurisées |

## Fonctionnalités principales

### Synchronisation sécurisée

Le module utilise des mécanismes de synchronisation avancés pour garantir l'intégrité et la disponibilité des données :

- Communication HTTPS avec vérification des certificats SSL
- Authentification par API key
- Vérification cryptographique de l'intégrité des données
- Mécanisme de cache local avec validation de fraîcheur
- Données de secours en cas d'indisponibilité du serveur
- Mécanisme de reprise sur erreur

### Synchronisation adaptative et priorisation

Le système optimise la synchronisation en fonction de l'importance et de la fréquence de mise à jour des données :

- Ajustement dynamique des priorités des modules
- Synchronisation plus fréquente des modules à haute priorité
- Détection des changements pour optimiser les ressources réseau
- Métriques de performance pour analyser le comportement

### Intégration avec les autres modules

Les données contextuelles sont utilisées par les autres modules de NovaEvo :

- **Module OBD-II** : Enrichissement des codes d'erreur avec descriptions détaillées et solutions
- **Module ECU Flash** : Vérification de la compatibilité et des limites sécurisées pour la reprogrammation
- **Module Parts Finder** : Enrichissement des résultats de recherche avec compatibilité et alternatives
- **Module Scheduling** : Accès aux données des ateliers et professionnels pour la planification des rendez-vous

## Configuration

### Variables d'environnement

Les modules contextuels sont configurés via des variables d'environnement dans le fichier `.env` :

```
# Serveurs contextuels
CONTEXT_SERVERS=https://api.example.com/dtc_database,https://api.example.com/vehicles_data
SYNC_INTERVAL=300  # En secondes (5 minutes par défaut)

# Clés API pour l'authentification
API_KEY_DTC_DATABASE=your_api_key_for_dtc_database
API_KEY_VEHICLES_DATA=your_api_key_for_vehicles_data

# Synchronisation adaptative
ADAPTIVE_SYNC=True  # Active l'adaptation dynamique des priorités
```

### Activation et désactivation des modules

Vous pouvez activer ou désactiver des modules contextuels spécifiques en ajoutant ou supprimant leur URL dans la variable `CONTEXT_SERVERS`.

## Utilisation dans le code

### Accès aux données contextuelles

```python
from utils.context_sync import context_manager

# Récupérer des données contextuelles
dtc_data = context_manager.get_context_data("dtc_database", "codes.P0300")
vehicle_data = context_manager.get_context_data("vehicles_data", "vehicles.model-123")

# Vérifier la disponibilité d'un module
if "repair_shops" in context_manager.modules:
    shops_near_me = context_manager.get_context_data("repair_shops", "locations.paris")
```

### Forcer la synchronisation manuelle

```python
# Synchroniser un module spécifique
context_manager.sync_module("dtc_database")

# Synchroniser tous les modules
sync_results = context_manager.sync_all_modules()
print(f"Synchronisation réussie: {sum(1 for r in sync_results.values() if r)}/{len(sync_results)}")
```

### Ajouter des écouteurs pour les mises à jour

```python
# Définir une fonction de callback
def on_dtc_database_updated(module_id, data):
    print(f"Module {module_id} mis à jour avec {len(data)} entrées")
    # Mettre à jour l'interface utilisateur, etc.

# Enregistrer l'écouteur
context_manager.register_listener(on_dtc_database_updated)
```

### Obtenir les métriques de performance

```python
# Récupérer les métriques de synchronisation
metrics = context_manager.get_sync_metrics()
print(f"Taux de succès global: {metrics['overall']['success_rate']:.2%}")

# Analyser les performances des modules
for module_id, module_metrics in metrics['modules'].items():
    print(f"Module {module_id}: {module_metrics['success_rate']:.2%}, priorité: {module_metrics['priority']}")
```

## Sécurité et Intégrité des Données

Le module implémente plusieurs mécanismes pour garantir la sécurité et l'intégrité des données :

1. **Vérification SSL** : Validation des certificats des serveurs contextuels
2. **Validation d'intégrité** : Vérification des hashes cryptographiques pour détecter toute altération
3. **Fallback sécurisé** : Utilisation de données de secours en cas de compromission
4. **Isolation des erreurs** : Confinement des erreurs pour éviter la propagation

## Monitoring et Diagnostic

Le module fournit des outils de surveillance pour diagnostiquer les problèmes :

```python
# Vérifier le statut de tous les modules
statuses = context_manager.get_all_modules_status()
for module_id, status in statuses.items():
    print(f"Module {module_id}: {status['status']}, dernière sync: {status['last_sync']}")

# Examiner les métriques d'un module spécifique
module_metrics = context_manager.metrics['module_metrics'].get('dtc_database', {})
avg_exec_time = module_metrics.get('avg_execution_time', 0)
print(f"Temps moyen d'exécution: {avg_exec_time:.2f}s")
```

## Bonnes pratiques

1. **Ne bloquez pas l'interface utilisateur** : Utilisez toujours les données en cache quand elles sont disponibles, même si elles ne sont pas à jour
2. **Gérez les données manquantes** : Prévoyez toujours le cas où les données contextuelles ne sont pas disponibles
3. **Priorité à l'expérience utilisateur** : La synchronisation adaptative ajuste automatiquement les priorités, mais vous pouvez les définir manuellement pour des cas spécifiques
4. **Respectez les limites** : Évitez de forcer trop de synchronisations manuelles pour ne pas surcharger les serveurs

## À venir

De nouveaux modules contextuels sont en cours de développement :

- Base de données des huiles et lubrifiants avec compatibilité par modèle
- Bibliothèque de schémas électriques et manuels techniques
- Données de prix du marché en temps réel pour l'évaluation des véhicules
- Base de données étendue des symptômes et diagnostics
