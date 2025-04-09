# Module de Reconnaissance d'Image - Documentation

## Description

Le module de Reconnaissance d'Image de l'Assistant Auto Ultime permet d'analyser des images de véhicules ou de pièces automobiles pour y détecter des labels (mots-clés), identifier des composants et diagnostiquer d'éventuelles anomalies. Il utilise l'API Google Cloud Vision pour une détection de labels précise et avancée.

## Objectifs

- Analyser des images de véhicules et de pièces automobiles
- Identifier les composants et objets présents dans l'image
- Détecter d'éventuelles anomalies (dommages, usure, problèmes)
- Fournir un diagnostic visuel préliminaire
- Aider au diagnostic automobile basé sur des images

## Prérequis

### API Google Cloud Vision

Pour utiliser ce module, vous devez disposer d'un compte Google Cloud Platform (GCP) et activer l'API Vision. Suivez ces étapes :

1. Créez un compte GCP ou connectez-vous à votre compte existant
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API Cloud Vision dans la console GCP
4. Créez une clé de compte de service avec les permissions nécessaires
5. Téléchargez le fichier de clé JSON

### Configuration des Credentials

Une fois la clé JSON obtenue, vous devez la configurer pour l'utilisation avec l'application :

1. Placez le fichier de clé JSON dans un emplacement sécurisé (de préférence hors du répertoire du projet)
2. Configurez la variable d'environnement `GOOGLE_APPLICATION_CREDENTIALS` pour qu'elle pointe vers ce fichier

Exemple de configuration dans le fichier `.env` :

```
GOOGLE_APPLICATION_CREDENTIALS=/chemin/vers/votre-cle.json
```

### Dépendances

- Python 3.7+
- Bibliothèque `google-cloud-vision` (`pip install google-cloud-vision`)
- OpenCV (`pip install opencv-python`)
- NumPy (`pip install numpy`)

## Installation

1. Installez les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

2. Créez un fichier `.env` à la racine du projet et ajoutez vos clés API :

```
GOOGLE_APPLICATION_CREDENTIALS=/chemin/vers/votre-cle.json
```

3. Testez l'installation en exécutant le script de test :

```bash
python -m image_recognition.image_recognition_main
```

## Utilisation

### Via l'API REST

Le module de reconnaissance d'image est accessible via l'endpoint REST `/image_recognition` de l'API. Vous pouvez envoyer une requête POST contenant une image :

```bash
curl -X POST http://localhost:5000/image_recognition \
  -F "image=@/chemin/vers/votre/image.jpg"
```

Si vous souhaitez une analyse plus approfondie (utilisant à la fois OpenCV et Google Cloud Vision), vous pouvez spécifier le paramètre `type=advanced` :

```bash
curl -X POST http://localhost:5000/image_recognition?type=advanced \
  -F "image=@/chemin/vers/votre/image.jpg"
```

Réponse typique :

```json
{
  "success": true,
  "labels": {
    "car": 0.95,
    "wheel": 0.92,
    "brake": 0.87,
    "rust": 0.76
  },
  "anomalies_detected": true,
  "anomalies": [
    {
      "type": "rust",
      "label": "rust",
      "score": 0.76
    }
  ],
  "car_related": true
}
```

### En tant que module Python

Vous pouvez également utiliser le module directement dans votre code Python :

```python
from image_recognition.image_recognition_main import detect_labels

# Analyser une image avec la fonction autonome
results = detect_labels('/chemin/vers/image.jpg')
print(results)

# Ou utiliser la classe complète
from image_recognition.image_recognition_main import ImageRecognitionEngine

engine = ImageRecognitionEngine()
results = engine.detect_labels('/chemin/vers/image.jpg')
print(results)
```

## Fonctionnalités

### Fonction `detect_labels()`

Cette fonction utilise l'API Google Cloud Vision pour analyser une image et retourner :

- Une liste de labels (mots-clés) avec leur score de confiance
- La détection d'anomalies potentielles (dommages, fissures, rouille, etc.)
- L'identification si l'image est liée à une automobile

### Classe `ImageRecognitionEngine`

Cette classe offre des fonctionnalités plus avancées :

- Analyse basique avec OpenCV (contours, couleurs)
- Analyse avancée avec des modèles ML personnalisés (si configurés)
- Détection de labels via Google Cloud Vision
- Diagnostics visuels basés sur les éléments détectés

## Exemples d'utilisation

### Analyse d'un composant endommagé

```python
from image_recognition.image_recognition_main import detect_labels

# Analyser une image d'un composant potentiellement endommagé
result = detect_labels('images/brake_rust.jpg')

# Vérifier la présence d'anomalies
if result['anomalies_detected']:
    print("Anomalies détectées:")
    for anomaly in result['anomalies']:
        print(f"- {anomaly['type']} (confiance: {anomaly['score']:.2f})")
```

### Analyse complète d'une pièce automobile

```python
from image_recognition.image_recognition_main import ImageRecognitionEngine

engine = ImageRecognitionEngine()

# Analyser une image avec l'engine complet
result = engine.analyze_image(image_path='images/engine_part.jpg')

# Afficher les résultats
if result['success']:
    if 'detections' in result:
        print("Objets détectés:")
        for detection in result['detections']:
            print(f"- {detection['class']} (confiance: {detection['confidence']:.2f})")
    
    if 'possible_diagnoses' in result:
        print("\nDiagnostics possibles:")
        for diagnosis in result['possible_diagnoses']:
            print(f"- {diagnosis}")
```

## Limitation et performances

### Performances et coûts

L'API Google Cloud Vision est un service payant au-delà du quota gratuit. Pour optimiser les coûts :

- N'envoyez que des images pertinentes et de taille raisonnable (< 4 Mo)
- Compressez les images avant envoi si nécessaire
- Utilisez le type d'analyse standard pour la plupart des cas

### Quota gratuit

Google Cloud Vision offre un quota gratuit mensuel :
- 1000 unités par mois (1 unité = 1 image analysée avec feature de base)

### Limites connues

- Fonctionne mieux avec des images bien éclairées et nettes
- Certains labels spécifiques aux pièces automobiles peuvent ne pas être reconnus précisément
- La détection d'anomalies est basée sur les mots-clés et peut manquer de précision

## Tests

Des tests unitaires sont disponibles pour le module de reconnaissance d'image. Vous pouvez les exécuter avec :

```bash
python -m unittest tests.test_image_recognition
```

ou avec pytest :

```bash
pytest tests/test_image_recognition.py -v
```

Les tests utilisent des mocks pour simuler les appels à l'API Google Cloud Vision, donc aucun quota d'API n'est consommé pendant les tests.

## Dépannage

### Problèmes courants

1. **Erreur d'authentification**
   - Vérifiez que la variable d'environnement `GOOGLE_APPLICATION_CREDENTIALS` est correctement configurée
   - Assurez-vous que le fichier de clé JSON est accessible et valide
   - Vérifiez que les permissions de l'API Vision sont activées dans votre projet GCP

2. **Quota dépassé**
   - Vérifiez votre quota restant dans la console GCP
   - Considérez l'utilisation d'une analyse basique avec OpenCV pour certains cas

3. **Images non reconnues**
   - Assurez-vous que l'image est de bonne qualité et bien éclairée
   - Vérifiez que l'image est dans un format supporté (JPG, PNG)
   - Essayez de recadrer l'image pour mieux isoler l'objet d'intérêt

### Vérification de la configuration

Pour vérifier que votre configuration fonctionne correctement :

```python
from google.cloud import vision

try:
    client = vision.ImageAnnotatorClient()
    print("Client Google Cloud Vision initialisé avec succès!")
except Exception as e:
    print(f"Erreur lors de l'initialisation du client: {str(e)}")
```

## Extensions futures

- Intégration de modèles personnalisés entraînés spécifiquement pour les pièces automobiles
- Utilisation d'autres API Vision pour la détection d'objets et la segmentation d'image
- Amélioration du diagnostic basé sur l'IA pour identifier les problèmes plus précisément
- Module de comparaison avant/après pour suivre l'évolution d'un problème

## Licence

Ce module est distribué sous la même licence que le projet Assistant Auto Ultime.
