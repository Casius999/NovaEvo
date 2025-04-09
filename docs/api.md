# API Reference - Assistant Auto Ultime

## Introduction

L'API Assistant Auto Ultime permet d'accéder à toutes les fonctionnalités du système via des endpoints REST. Cette documentation fournit les détails sur chaque endpoint, les paramètres requis et les exemples de requêtes et réponses.

## Base URL

```
http://localhost:5000/
```

## Authentification

Pour le moment, l'API ne nécessite pas d'authentification en mode développement. Une authentification par token JWT sera implémentée pour la production.

## Format des réponses

Toutes les réponses sont renvoyées au format JSON avec la structure suivante :

```json
{
  "status": "success|error",
  "message": "Message descriptif (optionnel)",
  "data": { ... } // Données spécifiques à l'endpoint
}
```

## Endpoints

### 1. Status de l'API

```
GET /
```

Vérifie si l'API est opérationnelle.

**Réponse**

```json
{
  "status": "success",
  "message": "API Assistant Auto Ultime opérationnelle",
  "modules": [
    "/ocr", "/obd2", "/nlp", "/image_recognition", 
    "/ecu_flash", "/parts_finder"
  ]
}
```

### 2. Module OCR

```
POST /ocr
```

Analyse une image pour en extraire les informations textuelles (carte grise).

**Paramètres**

| Nom | Type | Description |
|-----|------|-------------|
| image | File | L'image à analyser (formats supportés: JPG, PNG, PDF) |

**Réponse**

```json
{
  "status": "success",
  "data": {
    "full_text": "Texte extrait complet...",
    "vehicle_info": {
      "registration": "AB-123-CD",
      "make": "RENAULT",
      "model": "CLIO",
      "vin": "VF1234567890",
      "first_registration_date": "01/01/2020",
      "owner": "DOE JOHN"
    }
  }
}
```

### 3. Module OBD-II

```
GET /obd2
```

Récupère les données en temps réel du véhicule connecté.

**Paramètres**

| Nom | Type | Description |
|-----|------|-------------|
| command | String | (Optionnel) Commande OBD spécifique (RPM, SPEED, etc.) |

**Réponse**

```json
{
  "status": "success",
  "data": {
    "rpm": {
      "value": 1500,
      "unit": "rpm"
    },
    "speed": {
      "value": 60,
      "unit": "kph"
    },
    "coolant_temp": {
      "value": 90,
      "unit": "C"
    }
  }
}
```

### 4. Module NLP

```
POST /nlp
```

Interprète une commande en langage naturel.

**Paramètres**

| Nom | Type | Description |
|-----|------|-------------|
| query | String | La question ou commande en langage naturel |

**Réponse**

```json
{
  "status": "success",
  "data": {
    "interpretation": {
      "category": "diagnostic",
      "intent": "error_code_lookup",
      "entities": {
        "code": "P0300"
      },
      "response": "Le code P0300 indique des ratés d'allumage détectés sur plusieurs cylindres."
    }
  }
}
```

### 5. Module Image Recognition

```
POST /image_recognition
```

Analyse une image pour identifier des composants ou problèmes automobiles.

**Paramètres**

| Nom | Type | Description |
|-----|------|-------------|
| image | File | L'image à analyser |

**Réponse**

```json
{
  "status": "success",
  "data": {
    "detections": [
      {
        "class": "disc_brake",
        "confidence": 0.94,
        "bounding_box": [10, 20, 100, 200]
      },
      {
        "class": "caliper",
        "confidence": 0.87,
        "bounding_box": [30, 40, 120, 220]
      }
    ],
    "diagnosis": [
      "Les plaquettes de frein montrent des signes d'usure avancée",
      "Le disque semble en bon état"
    ]
  }
}
```

### 6. Module ECU Flash

```
GET /ecu_flash
```

Récupère les cartographies disponibles pour le véhicule connecté.

**Réponse**

```json
{
  "status": "success",
  "data": {
    "maps": [
      {
        "name": "ignition_advance",
        "description": "Avance à l'allumage",
        "type": "2D",
        "category": "ignition"
      },
      {
        "name": "fuel_injection",
        "description": "Injection de carburant",
        "type": "3D",
        "category": "fuel"
      }
    ]
  }
}
```

### 7. Module Parts Finder

```
GET /parts_finder
```

Recherche des pièces détachées pour un véhicule.

**Paramètres**

| Nom | Type | Description |
|-----|------|-------------|
| make | String | (Optionnel) Marque du véhicule |
| model | String | (Optionnel) Modèle du véhicule |
| category | String | (Optionnel) Catégorie de pièce |
| part_type | String | (Optionnel) Type de pièce (origine, sport, competition) |
| keyword | String | (Optionnel) Mot-clé de recherche |

**Réponse**

```json
{
  "status": "success",
  "data": {
    "count": 2,
    "results": [
      {
        "id": 1,
        "reference": "F-001",
        "name": "Plaquettes de frein avant",
        "category": "Freinage",
        "part_type": "origine",
        "description": "Plaquettes de frein avant d'origine",
        "price": 45.99,
        "stock": 25
      },
      {
        "id": 2,
        "reference": "F-002",
        "name": "Plaquettes de frein avant sport",
        "category": "Freinage",
        "part_type": "sport",
        "description": "Plaquettes de frein avant haute performance",
        "price": 89.99,
        "stock": 12
      }
    ]
  }
}
```

## Gestion des erreurs

En cas d'erreur, l'API renvoie un code HTTP approprié et un message décrivant le problème :

```json
{
  "status": "error",
  "message": "Description détaillée de l'erreur",
  "code": "ERROR_CODE"
}
```

## Codes d'erreur communs

| HTTP Code | Message | Description |
|-----------|---------|-------------|
| 400 | Bad Request | La requête est mal formée |
| 401 | Unauthorized | Authentification requise |
| 403 | Forbidden | Accès non autorisé |
| 404 | Not Found | Ressource non trouvée |
| 500 | Internal Server Error | Erreur interne du serveur |

## Exemples d'utilisation

### Python

```python
import requests

# Exemple d'utilisation du module OCR
files = {'image': open('carte_grise.jpg', 'rb')}
response = requests.post('http://localhost:5000/ocr', files=files)
print(response.json())

# Exemple d'utilisation du module NLP
data = {'query': 'Que signifie le code erreur P0300 ?'}
response = requests.post('http://localhost:5000/nlp', json=data)
print(response.json())
```

### JavaScript

```javascript
// Exemple d'utilisation du module OCR
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:5000/ocr', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

// Exemple d'utilisation du module NLP
fetch('http://localhost:5000/nlp', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'Que signifie le code erreur P0300 ?'
  })
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```
