# Tests

Ce dossier contient tous les tests unitaires, d'intégration et de bout en bout pour l'Assistant Auto Ultime.

## Structure des tests

### Tests unitaires
- `/unit` - Tests unitaires pour chaque module
  - `/ocr` - Tests pour le module OCR
  - `/obd2` - Tests pour le module OBD-II
  - `/nlp` - Tests pour le module NLP
  - `/image_recognition` - Tests pour le module de reconnaissance d'image
  - `/ecu_flash` - Tests pour le module de reprogrammation ECU
  - `/parts_finder` - Tests pour le module de recherche de pièces
  - `/frontend` - Tests unitaires pour l'interface utilisateur

### Tests d'intégration
- `/integration` - Tests d'intégration entre modules
  - `/api` - Tests des API entre modules
  - `/frontend-backend` - Tests d'intégration entre frontend et backend
  - `/data-flow` - Tests de flux de données entre modules

### Tests end-to-end
- `/e2e` - Tests de bout en bout
  - `/scenarios` - Scénarios de test utilisateur
  - `/performance` - Tests de performance

### Tests de sécurité
- `/security` - Tests de sécurité
  - `/penetration` - Tests de pénétration
  - `/vulnerability` - Tests de vulnérabilité
  - `/data-protection` - Tests de protection des données

## Exécution des tests

### Tests unitaires
```bash
# Exécuter tous les tests unitaires
npm run test:unit

# Exécuter les tests unitaires pour un module spécifique
npm run test:unit:ocr
npm run test:unit:obd2
# etc.
```

### Tests d'intégration
```bash
# Exécuter tous les tests d'intégration
npm run test:integration

# Exécuter les tests d'intégration pour un aspect spécifique
npm run test:integration:api
```

### Tests end-to-end
```bash
# Exécuter tous les tests end-to-end
npm run test:e2e
```

## Couverture de code

Pour générer un rapport de couverture de code :
```bash
npm run test:coverage
```

Le rapport sera disponible dans `coverage/lcov-report/index.html`.

## Bonnes pratiques

- Créez un test pour chaque nouvelle fonctionnalité
- Assurez-vous que les tests sont indépendants
- Utilisez des mocks pour simuler les dépendances externes
- Maintenez une couverture de code d'au moins 80%
- Exécutez les tests avant chaque commit