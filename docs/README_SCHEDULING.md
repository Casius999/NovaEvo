# NovaEvo - Module de Planification Automatique

Le module de planification automatique est une fonctionnalité clé de NovaEvo qui permet de trouver et réserver des créneaux avec des professionnels de l'automobile, en temps réel et selon les besoins de l'utilisateur. Cette documentation explique comment configurer et utiliser ce système.

## Table des matières

1. [Introduction](#introduction)
2. [Fonctionnalités](#fonctionnalités)
3. [Configuration](#configuration)
4. [Utilisation du module](#utilisation-du-module)
5. [Gestion des urgences](#gestion-des-urgences)
6. [Intégration avec le reste de l'application](#intégration-avec-le-reste-de-lapplication)
7. [API REST](#api-rest)
8. [Personnalisation](#personnalisation)
9. [Dépannage](#dépannage)

## Introduction

Le système de planification automatique permet aux utilisateurs de NovaEvo de trouver rapidement des créneaux disponibles chez des professionnels de l'automobile à proximité, en fonction de leurs besoins. Il prend en charge différents niveaux d'urgence et peut même créer dynamiquement des créneaux supplémentaires lors des périodes de forte demande.

Ce module s'intègre avec d'autres composants de NovaEvo, notamment:
- Le système de recherche de pièces détachées
- Les modules de diagnostic véhicule
- Les données contextuelles des professionnels partenaires

## Fonctionnalités

### Recherche géolocalisée

- Recherche des professionnels dans un rayon défini
- Filtrage par spécialités et services
- Tri par distance, disponibilité ou évaluations
- Affichage des informations détaillées (adresse, horaires, etc.)

### Gestion intelligente des créneaux

- Affichage en temps réel des disponibilités
- Création dynamique de créneaux lors des pics de demande
- Maintien d'un nombre minimal de créneaux d'urgence
- Optimisation du planning des professionnels

### Priorisation des urgences

- Traitement accéléré des demandes urgentes
- Classification automatique du niveau d'urgence
- Ajustement dynamique des plannings pour les cas critiques
- Alertes pour les professionnels partenaires

### Suivi et notifications

- Confirmations automatiques par email et SMS
- Rappels programmés avant les rendez-vous
- Notifications en cas de modification ou annulation
- Suivi post-intervention et demande de feedback

## Configuration

### Variables d'environnement

Configurez le planificateur dans votre fichier `.env`:

```
# Activation de l'API de planification
APPOINTMENT_API_ENABLED=True

# URL de l'API de planification (interne ou externe)
APPOINTMENT_API_URL=https://api.scheduling.example.com

# Clé API pour l'authentification
APPOINTMENT_API_KEY=your_scheduling_api_key

# Seuil minimum de créneaux d'urgence à maintenir
EMERGENCY_SLOTS_THRESHOLD=3
```

### Configuration pour le développement

En mode développement, vous pouvez utiliser le mode mock (simulation) qui ne nécessite pas de connexion à un serveur externe:

```python
# Dans votre code d'initialisation
from parts_finder.appointment_scheduler import scheduler

# Forcer le mode de simulation pour le développement
scheduler.set_mock_mode(True)
```

## Utilisation du module

### Recherche de créneaux disponibles

```python
from parts_finder.appointment_scheduler import scheduler

# Coordonnées géographiques (latitude, longitude)
location = {
    "latitude": 48.8566,
    "longitude": 2.3522
}

# Rechercher des créneaux dans un rayon de 30km
available_slots = scheduler.find_available_slots(
    location=location,
    radius=30.0,         # Rayon en km
    timeframe=7,         # Période en jours
    vehicle_type="diesel"  # Optionnel: type de véhicule pour filtrer les garages compétents
)

# Afficher les créneaux disponibles
for slot in available_slots:
    print(f"{slot['garage_name']} - {slot['start_time']} - {slot['service_types']}")
```

### Planification d'un rendez-vous

```python
# Sélectionner un créneau et réserver
appointment = scheduler.schedule_appointment(
    slot_id=available_slots[0]["id"],
    vehicle_id="vehicle-123",
    service_type="diagnostic",
    user_id="user-456",
    notes="Problème de démarrage à froid"
)

# Afficher les détails du rendez-vous
print(f"Rendez-vous confirmé: {appointment['confirmation_code']}")
print(f"Date: {appointment['start_time']}")
print(f"Garage: {appointment['garage_name']}")
print(f"Adresse: {appointment['garage_address']}")
print(f"Téléphone: {appointment['garage_phone']}")
```

## Gestion des urgences

### Identification des créneaux d'urgence

```python
# Rechercher des créneaux d'urgence
emergency_slots = scheduler.find_emergency_slots(
    location=location,
    urgency_level="high",   # Options: "high" ou "emergency"
    max_distance=20.0       # Distance maximale en km
)

# Afficher les créneaux d'urgence disponibles
for slot in emergency_slots:
    print(f"{slot['garage_name']} - Distance: {slot['distance']}km - {slot['start_time']}")
```

### Création dynamique de créneaux

Le système peut créer automatiquement des créneaux d'urgence lorsque le nombre disponible est inférieur au seuil défini. Pour déclencher cette création manuellement:

```python
# Forcer la création de créneaux d'urgence
success = scheduler._create_dynamic_emergency_slots(urgency_level="emergency")
if success:
    print("Nouveaux créneaux d'urgence créés avec succès")
else:
    print("Échec de la création de créneaux d'urgence")
```

## Intégration avec le reste de l'application

### Avec le module de recherche de pièces

Lorsqu'un utilisateur recherche une pièce, vous pouvez proposer automatiquement des créneaux pour l'installation:

```python
def suggest_installation_slots(part_search_results, user_location):
    """Suggère des créneaux d'installation après une recherche de pièces"""
    if part_search_results and len(part_search_results) > 0:
        # Déterminer si certaines pièces nécessitent une installation professionnelle
        requires_professional = any(result.get('requires_professional', False) 
                                   for result in part_search_results)
        
        if requires_professional:
            # Rechercher des créneaux à proximité
            slots = scheduler.find_available_slots(
                location=user_location,
                radius=30.0,
                timeframe=7
            )
            
            return {
                'parts': part_search_results,
                'installation_slots': slots[:3]  # Retourner les 3 premiers créneaux
            }
    
    return {'parts': part_search_results}
```

### Avec le module de diagnostic

Intégration avec le diagnostic véhicule pour proposer des rendez-vous en fonction des problèmes détectés:

```python
def process_diagnostic_results(diagnostic_results, user_location):
    """Traite les résultats de diagnostic et propose des rendez-vous si nécessaire"""
    
    # Vérifier si des codes d'erreur critiques sont présents
    critical_codes = ['P0101', 'P0102', 'P0103', 'P0171', 'P0300']
    has_critical = any(code in critical_codes for code in diagnostic_results.get('codes', []))
    
    # Déterminer le niveau d'urgence
    urgency_level = "emergency" if has_critical else "high"
    
    # Rechercher des créneaux adaptés
    if has_critical:
        slots = scheduler.find_emergency_slots(
            location=user_location,
            urgency_level=urgency_level
        )
    else:
        slots = scheduler.find_available_slots(
            location=user_location,
            radius=20.0
        )
    
    return {
        'diagnostic': diagnostic_results,
        'recommended_action': 'schedule_appointment' if has_critical else 'monitor',
        'available_slots': slots[:3]
    }
```

## API REST

Le module expose plusieurs endpoints REST pour l'intégration avec le frontend:

### Recherche de créneaux disponibles

```
GET /api/appointments/slots?lat=48.8566&lng=2.3522&radius=30&days=7
```

Paramètres:
- `lat`: Latitude
- `lng`: Longitude
- `radius`: Rayon de recherche en km
- `days`: Période de recherche en jours
- `vehicle_type` (optionnel): Type de véhicule

### Recherche de créneaux d'urgence

```
POST /api/appointments/emergency_slots
```

Corps de la requête:
```json
{
  "lat": 48.8566,
  "lng": 2.3522,
  "urgency_level": "high",
  "max_distance": 20
}
```

### Planification d'un rendez-vous

```
POST /api/appointments
```

Corps de la requête:
```json
{
  "slot_id": "slot-garage-1-20250410090000",
  "vehicle_id": "vehicle-123",
  "service_type": "diagnostic",
  "user_id": "user-456",
  "notes": "Problème de démarrage à froid"
}
```

## Personnalisation

### Modification des critères de recherche

Vous pouvez personnaliser les critères de recherche dans le fichier de configuration:

```python
# Configuration personnalisée
scheduler.set_search_config({
    'default_radius': 25.0,
    'default_timeframe': 5,
    'min_rating': 4.0,
    'preferred_service_types': ['diagnostic', 'repair', 'maintenance'],
    'exclude_weekends': False
})
```

### Ajout de nouveaux types de services

Pour ajouter de nouveaux types de services reconnus par le planificateur:

```python
# Ajouter un nouveau type de service
scheduler.add_service_type(
    code="ecu_flash",
    name="Reprogrammation ECU",
    duration_minutes=90,
    emergency_compatible=False,
    requires_specialist=True
)
```

## Dépannage

### Résolution des problèmes courants

1. **Aucun créneau trouvé**
   - Vérifiez que les coordonnées géographiques sont correctes
   - Augmentez le rayon de recherche
   - Élargissez la période de recherche (paramètre `timeframe`)

2. **Erreur de planification**
   - Vérifiez que l'ID du créneau est valide
   - Assurez-vous que le créneau est toujours disponible (il peut avoir été réservé)
   - Vérifiez que tous les paramètres requis sont fournis

3. **Temps de réponse lents**
   - Réduisez le rayon de recherche
   - Limitez le nombre de jours dans la période de recherche
   - Utilisez des filtres plus spécifiques

### Logs

Le planificateur enregistre ses activités dans le fichier de log avec le préfixe "novaevo.scheduler". Consultez ces logs pour identifier les problèmes potentiels.

```bash
grep "novaevo.scheduler" logs/novaevo.log
```
