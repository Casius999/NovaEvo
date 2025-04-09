# Module OCR

Ce module est responsable de la numérisation et de l'extraction des informations des cartes grises et autres documents automobiles.

## Fonctionnalités
- Reconnaissance optique des caractères pour les cartes grises
- Extraction automatique des informations du véhicule
- Validation des données extraites
- Stockage structuré des informations

## Technologies
- Tesseract OCR
- OpenCV pour le prétraitement d'images
- Algorithmes de validation spécifiques aux formats de documents automobiles

## Structure du module
- `/models` - Modèles d'OCR entraînés pour les documents automobiles
- `/preprocessing` - Scripts de prétraitement des images
- `/validation` - Validation et vérification des données extraites
- `/api` - Endpoints pour l'intégration avec d'autres modules