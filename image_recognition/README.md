# Module de Reconnaissance d'Image

Ce module permet à l'Assistant Auto Ultime d'analyser des images de véhicules ou de pièces automobiles pour y détecter des labels (mots-clés), identifier des composants et diagnostiquer d'éventuelles anomalies.

## Fonctionnalités

- Détection de labels grâce à l'API Google Cloud Vision
- Analyse d'images pour identifier des pièces automobiles
- Détection d'anomalies (dommages, usure, problèmes)
- Diagnostic visuel préliminaire
- Analyse basique avec OpenCV (contours, couleurs)
- Analyse avancée avec des modèles ML personnalisés (si configurés)

## Structure du module

```
/image_recognition/
  ├── __init__.py          # Fichier d'initialisation du package
  ├── image_recognition_main.py  # Module principal
  └── README.md            # Documentation sommaire
```

## Implémentation

Le module propose deux approches complémentaires :

1. **Fonction autonome `detect_labels()`**
   - Utilise l'API Google Cloud Vision pour analyser une image
   - Retourne les labels détectés avec leur score de confiance
   - Détecte les anomalies potentielles
   - Simple d'utilisation pour les cas basiques

2. **Classe `ImageRecognitionEngine`**
   - Offre des fonctionnalités plus avancées
   - Intègre OpenCV pour l'analyse d'image (contours, couleurs)
   - Prend en charge des modèles ML personnalisés (si configurés)
   - Inclut la détection de labels via Google Cloud Vision
   - Génère des diagnostics visuels basés sur les éléments détectés

## API REST

Le module est accessible via l'endpoint `/image_recognition` de l'API REST, qui accepte une image et retourne l'analyse des labels détectés.

### Options

- Analyse standard : `/image_recognition` (détection simple de labels)
- Analyse avancée : `/image_recognition?type=advanced` (utilise toutes les fonctionnalités de l'engine)

## Configuration

Le module nécessite une clé d'API Google Cloud Vision. Configurez la variable d'environnement `GOOGLE_APPLICATION_CREDENTIALS` pour qu'elle pointe vers votre fichier de clé JSON.

## Exemples d'utilisation

```python
# Utilisation simple
from image_recognition.image_recognition_main import detect_labels

results = detect_labels('/chemin/vers/image.jpg')
print(results)

# Utilisation avancée
from image_recognition.image_recognition_main import ImageRecognitionEngine

engine = ImageRecognitionEngine()
results = engine.detect_labels('/chemin/vers/image.jpg')
print(results)
```

## Documentation détaillée

Une documentation complète est disponible dans le fichier [docs/README_Image_Recognition.md](../docs/README_Image_Recognition.md), qui inclut :

- Guide d'installation et de configuration
- Détails sur l'API Google Cloud Vision
- Exemples d'utilisation avancés
- Limitations et performances
- Dépannage et bonnes pratiques

## Tests

Des tests unitaires pour le module se trouvent dans [tests/test_image_recognition.py](../tests/test_image_recognition.py) et peuvent être exécutés avec pytest :

```bash
pytest tests/test_image_recognition.py -v
```
