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
| type | String | (Optionnel) Type d'analyse à effectuer ('standard' ou 'advanced') |

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

#### 6.1. Flasher l'ECU

```
POST /ecu_flash
```

Flash l'ECU avec les paramètres de tuning spécifiés.

**Paramètres**

Le corps de la requête doit contenir un objet JSON avec les paramètres de tuning:

```json
{
  "cartographie_injection": 105,
  "boost_turbo": 1.1,
  "avance_allumage": 12
}
```

**Réponse (succès)**

```json
{
  "status": "success",
  "message": "Flash de l'ECU réussi.",
  "new_configuration": {
    "cartographie_injection": 105,
    "boost_turbo": 1.1,
    "avance_allumage": 12
  }
}
```

**Réponse (échec)**

```json
{
  "status": "error",
  "message": "Valeur '1.3' pour 'boost_turbo' hors limite (min: 0.8, max: 1.2)."
}
```

#### 6.2. Connexion à l'ECU

```
POST /ecu_flash/connect
```

Établit une connexion avec l'ECU du véhicule.

**Paramètres**

Aucun paramètre requis.

**Réponse**

```json
{
  "success": true,
  "message": "Connecté à l'ECU",
  "device_id": "OP-23456",
  "protocol": "CAN",
  "interface": "Tactrix Openport 2.0"
}
```

#### 6.3. Lecture de l'ECU

```
GET /ecu_flash/read
```

Lit la configuration actuelle de l'ECU.

**Paramètres**

Aucun paramètre requis.

**Réponse**

```json
{
  "success": true,
  "message": "Lecture de l'ECU réussie",
  "vehicle": {
    "make": "Volkswagen",
    "model": "Golf GTI",
    "year": "2023"
  },
  "parameters_count": 24,
  "maps_count": 8
}
```

#### 6.4. Obtenir les limites des paramètres

```
GET /ecu_flash/parameters
```

Récupère les limites sécurisées pour tous les paramètres de tuning disponibles.

**Paramètres**

Aucun paramètre requis.

**Réponse**

```json
{
  "status": "success",
  "parameters": {
    "cartographie_injection": {"default": 100, "min": 90, "max": 115},
    "boost_turbo": {"default": 1.0, "min": 0.8, "max": 1.2},
    "avance_allumage": {"default": 10, "min": 5, "max": 15},
    "limiteur_regime": {"default": 6500, "min": 6000, "max": 7500},
    "richesse_melange": {"default": 1.0, "min": 0.9, "max": 1.1}
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

# Exemple d'utilisation du module ECU Flash
# 1. Connexion à l'ECU
response = requests.post('http://localhost:5000/ecu_flash/connect')
print(response.json())

# 2. Flashage avec paramètres personnalisés
tuning_params = {
    "cartographie_injection": 105,
    "boost_turbo": 1.1
}
response = requests.post('http://localhost:5000/ecu_flash', json=tuning_params)
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

// Exemple d'utilisation du module ECU Flash
// 1. Connexion à l'ECU
fetch('http://localhost:5000/ecu_flash/connect', {
  method: 'POST'
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // 2. Flashage avec paramètres personnalisés
      return fetch('http://localhost:5000/ecu_flash', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cartographie_injection: 105,
          boost_turbo: 1.1
        })
      });
    }
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```
