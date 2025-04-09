# Module OCR - Documentation

## Introduction

Le module OCR (Reconnaissance Optique de Caractères) est conçu pour analyser les images de cartes grises, extraire les informations pertinentes et les structurer dans un format JSON. Il utilise Google Cloud Vision API comme moteur principal de reconnaissance, avec une solution de repli vers Tesseract OCR si nécessaire.

Ce document détaille l'architecture, les fonctionnalités, la configuration et l'utilisation du module OCR.

## Fonctionnalités

- Capture d'images de carte grise via l'appareil photo du téléphone ou de la webcam
- Analyse OCR des images pour extraire le texte
- Algorithmes spécialisés pour détecter les informations de carte grise :
  - Numéro d'immatriculation
  - Marque et modèle du véhicule
  - Numéro VIN (Numéro d'identification du véhicule)
  - Date de première immatriculation
  - Informations du propriétaire
  - Puissance du véhicule
  - Autres informations techniques
- Interface avec Google Cloud Vision API
- Solution de repli vers Tesseract OCR si Google Cloud Vision n'est pas disponible
- Validation des formats d'immatriculation
- Mesure de la qualité de l'extraction d'informations

## Architecture

Le module OCR est composé des éléments suivants :

```
ocr/
├── __init__.py        # Initialisation du package
├── ocr_main.py        # Code principal du module OCR
```

### Frontend

Le frontend intègre un composant React `OCRCapture.js` qui permet :
- D'accéder à la caméra du périphérique
- De capturer une image
- D'envoyer l'image au backend pour analyse
- D'afficher les résultats de l'analyse

### Backend

Le backend expose un endpoint `/ocr` qui :
- Reçoit les images depuis le frontend
- Les traite avec le module OCR
- Retourne les informations extraites au format JSON

## Configuration

### Prérequis

- Python 3.8+
- Google Cloud Vision API ou Tesseract OCR
- Bibliothèques Python : `google-cloud-vision`, `pillow`, `pytesseract` (optionnel)
- Un navigateur moderne supportant l'API MediaDevices pour l'accès à la caméra

### Configuration de Google Cloud Vision API

1. Créez un compte Google Cloud Platform (GCP) si vous n'en avez pas déjà un
2. Créez un nouveau projet GCP
3. Activez l'API Cloud Vision pour ce projet
4. Créez une clé d'API de compte de service :
   - Allez dans "IAM & Admin" > "Comptes de service"
   - Créez un nouveau compte de service
   - Attribuez-lui le rôle "Cloud Vision API User"
   - Créez une nouvelle clé au format JSON
   - Téléchargez la clé JSON
5. Définissez la variable d'environnement `GOOGLE_APPLICATION_CREDENTIALS` pour pointer vers le fichier de clé JSON :

```bash
# Linux/macOS
export GOOGLE_APPLICATION_CREDENTIALS="/chemin/vers/votre-fichier-de-cle.json"

# Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\chemin\vers\votre-fichier-de-cle.json"
```

Alternativement, vous pouvez ajouter cette ligne dans votre fichier `.env` :

```
GOOGLE_APPLICATION_CREDENTIALS=/chemin/vers/votre-fichier-de-cle.json
```

### Configuration de Tesseract OCR (fallback)

Si vous ne souhaitez pas utiliser Google Cloud Vision API ou si vous voulez disposer d'une solution de repli, vous pouvez configurer Tesseract OCR :

1. Installez Tesseract OCR sur votre système :

```bash
# Ubuntu
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-fra  # Pour le français

# macOS
brew install tesseract
brew install tesseract-lang  # Pour les langues supplémentaires

# Windows
# Téléchargez l'installateur depuis https://github.com/UB-Mannheim/tesseract/wiki
```

2. Installez la bibliothèque Python :

```bash
pip install pytesseract
```

3. Si nécessaire, configurez le chemin vers l'exécutable Tesseract dans votre fichier `.env` :

```
TESSERACT_CMD=/usr/bin/tesseract  # Exemple pour Linux
```

## Utilisation

### Depuis le Frontend

1. Accédez à la page OCR via l'interface de l'application
2. Cliquez sur le bouton pour activer la caméra
3. Positionnez la carte grise dans le cadre
4. Prenez la photo
5. Cliquez sur "Analyser" pour lancer le traitement OCR
6. Les résultats s'afficheront sous la photo

### Appel direct de l'API

Vous pouvez appeler directement l'endpoint OCR avec une requête HTTP :

```javascript
// Exemple avec fetch
async function analyzeImage(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const response = await fetch('/ocr', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

### Utilisation programmatique (Python)

```python
from ocr.ocr_main import extraire_infos_carte_grise

# Analyser une image de carte grise
result = extraire_infos_carte_grise("chemin/vers/image.jpg")
print(result)
```

## Format des résultats

Le module OCR retourne un objet JSON avec la structure suivante :

```json
{
  "success": true,
  "vehicle_info": {
    "registration": "AB-123-CD",
    "make": "Renault",
    "model": "Clio",
    "vin": "VF123456789012345",
    "first_registration_date": "01/01/2020",
    "owner": "DUPONT JEAN",
    "type_variant_version": "M10ABCDE1234",
    "power": "100 CV"
  },
  "raw_text": "Texte brut extrait de l'image...",
  "confidence": "haute",
  "extraction_quality": "85.71%"
}
```

En cas d'erreur, la réponse aura ce format :

```json
{
  "error": "Description détaillée de l'erreur",
  "status": "error"
}
```

## Conseils pour une meilleure reconnaissance

Pour améliorer la qualité de la reconnaissance OCR :

1. **Éclairage** : Assurez-vous que la carte grise est bien éclairée
2. **Cadrage** : Capturez l'intégralité de la carte grise dans l'image
3. **Netteté** : Évitez les images floues, tenez l'appareil stable
4. **Contraste** : Évitez les reflets ou les ombres sur le document
5. **Orientation** : Essayez de prendre la photo à angle droit, sans inclinaison

## Dépannage

### Problèmes d'accès à la caméra

Si le navigateur ne peut pas accéder à la caméra :
- Vérifiez que vous utilisez HTTPS ou localhost (requis pour l'API MediaDevices)
- Assurez-vous d'avoir accordé les permissions d'accès à la caméra dans le navigateur
- Vérifiez que votre caméra fonctionne avec d'autres applications

### Erreurs d'analyse OCR

Si l'analyse OCR échoue ou donne des résultats incorrects :
- Vérifiez que les clés API Google Cloud Vision sont correctement configurées
- Vérifiez que l'image est de bonne qualité (lumière, netteté, angle)
- Vérifiez que vous utilisez une version récente du navigateur

### Accès aux logs

Pour plus d'informations en cas d'erreur, consultez les logs :

- **Frontend** : Console du navigateur (F12)
- **Backend** : Logs du serveur Flask

## Considérations sur la sécurité et la confidentialité

- Les images de cartes grises contiennent des données personnelles sensibles
- Les images sont temporairement stockées sur le serveur pour traitement, puis supprimées
- Aucune donnée n'est conservée à long terme sans le consentement de l'utilisateur
- Les API tierces (Google Cloud Vision) ont leurs propres politiques de confidentialité

## Tests

Des tests automatisés sont disponibles pour vérifier le bon fonctionnement du module OCR :

```bash
# Lancer les tests unitaires
pytest tests/test_ocr.py
```

## Limitations connues

- La qualité de la reconnaissance dépend fortement de la qualité de l'image
- Certains formats de carte grise anciens ou étrangers peuvent ne pas être bien reconnus
- La solution de repli Tesseract OCR est généralement moins précise que Google Cloud Vision
- La reconnaissance du propriétaire peut être imprécise en raison de la diversité des formats
