# Documentation Frontend - Assistant Auto Ultime

## Introduction

Cette documentation décrit l'interface utilisateur de l'application "Assistant Auto Ultime", une plateforme complète pour les passionnés d'automobile intégrant des fonctionnalités avancées d'OCR, de diagnostic OBD-II, de traitement du langage naturel, de reconnaissance d'images, de reprogrammation ECU et de recherche de pièces détachées.

## Structure du Frontend

L'interface utilisateur est développée avec React et utilise les technologies suivantes :
- **React** : bibliothèque JavaScript pour la construction de l'interface utilisateur
- **React Router** : pour la navigation entre les différentes sections de l'application
- **React Bootstrap** : pour les composants UI et le responsive design
- **Axios** : pour les requêtes HTTP vers le backend

## Composants principaux

L'application est organisée en plusieurs composants React :

1. **App.js** : Composant principal qui gère le routage et la structure globale de l'application
2. **Auth.js** : Gestion de l'authentification (connexion, inscription, affichage des abonnements)
3. **OCRCapture.js** : Scan de carte grise avec capture depuis la caméra
4. **OBD2Dashboard.js** : Affichage des données du véhicule en temps réel
5. **NLPAssistant.js** : Interface conversationnelle pour les requêtes en langage naturel
6. **ImageRecognition.js** : Analyse visuelle de problèmes automobiles
7. **ECUFlash.js** : Interface de reprogrammation de l'ECU
8. **PartsFinder.js** : Recherche et comparaison de pièces détachées

## Installation et lancement

### Prérequis

- Node.js 18+ (LTS recommandé)
- npm 8+ ou yarn 1.22+
- Backend "Assistant Auto Ultime" en fonctionnement (sur le port 5000 par défaut)

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/Casius999/assistant-auto-ultime.git
cd assistant-auto-ultime/frontend

# Installer les dépendances
npm install
# ou avec yarn
yarn install
```

### Configuration

L'application utilise un fichier `package.json` pour configurer le proxy vers le backend. Par défaut, le proxy est configuré pour pointer vers l'URL `http://app:5000`, ce qui correspond à la configuration Docker. Si vous développez en local sans Docker, modifiez cette valeur :

```json
{
  "proxy": "http://localhost:5000"
}
```

### Lancement en développement

```bash
npm start
# ou avec yarn
yarn start
```

L'application sera accessible à l'adresse [http://localhost:3000](http://localhost:3000).

### Construction pour la production

```bash
npm run build
# ou avec yarn
yarn build
```

Les fichiers statiques seront générés dans le dossier `build` et pourront être servis par n'importe quel serveur web statique.

## Endpoints API utilisés

L'interface communique avec les endpoints suivants du backend :

| Module | Endpoint | Méthode | Description |
|--------|----------|---------|-------------|
| OCR | `/ocr` | POST | Analyse d'image de carte grise via OCR |
| OBD-II | `/obd2` | GET | Récupération des données véhicule en temps réel |
| NLP | `/nlp` | POST | Traitement des requêtes en langage naturel |
| Reconnaissance d'image | `/image_recognition` | POST | Analyse d'images pour diagnostic visuel |
| ECU Flash | `/ecu_flash` | POST | Flashage de l'ECU avec des paramètres personnalisés |
| ECU Flash | `/ecu_flash/connect` | POST | Connexion à l'ECU |
| ECU Flash | `/ecu_flash/read` | GET | Lecture des paramètres actuels de l'ECU |
| ECU Flash | `/ecu_flash/parameters` | GET | Récupération des limites sécurisées des paramètres |
| Parts Finder | `/parts_finder` | POST | Recherche de pièces détachées |

## Système d'authentification

L'application utilise un système d'authentification simulé basé sur le stockage local (localStorage) pour la démonstration. En production, ce système devrait être remplacé par une authentification sécurisée basée sur JWT ou OAuth.

### Fonctionnement actuel

1. **Connexion** : Un utilisateur peut se connecter avec des identifiants de démonstration (email: demo@example.com, mot de passe: password)
2. **Stockage** : Lors de la connexion réussie, un token et les informations utilisateur sont stockés dans le localStorage
3. **Protection des routes** : Les routes d'accès aux différents modules sont protégées et redirigent vers la page d'authentification si l'utilisateur n'est pas connecté
4. **Déconnexion** : La déconnexion supprime le token et les informations utilisateur du localStorage

### Configuration pour la production

Pour un environnement de production, il est recommandé de :

1. Implémenter une authentification sécurisée côté serveur avec JWT
2. Configurer des refresh tokens pour maintenir les sessions
3. Sécuriser tous les endpoints avec une vérification d'authentification
4. Implémenter un système de gestion des abonnements réel (avec intégration à une passerelle de paiement)

## CORS et sécurité

Pour que le frontend puisse communiquer avec le backend, les CORS (Cross-Origin Resource Sharing) doivent être correctement configurés sur le serveur backend.

Dans le fichier `app.py` du backend, cette configuration est déjà en place avec la ligne :
```python
CORS(app)  # Activer CORS pour toutes les routes
```

En production, il est recommandé de restreindre les CORS uniquement aux origines spécifiques de votre application.

## Personnalisation et extension

### Ajout d'un nouveau module

Pour ajouter un nouveau module à l'interface :

1. Créer un nouveau composant React dans le dossier `/frontend/src/components/`
2. Ajouter le composant aux imports dans `App.js`
3. Ajouter une nouvelle route dans le système de routage de `App.js`
4. Ajouter un lien vers le nouveau module dans la barre de navigation et sur la page d'accueil

### Personnalisation du style

Le style global peut être modifié via :
- Le fichier `/frontend/src/App.css` pour les styles personnalisés
- Les variables Bootstrap pour les couleurs et le thème général
- Les propriétés spécifiques de chaque composant React Bootstrap

## Dépannage et problèmes courants

### Problèmes de connexion avec le backend
- Vérifiez que le backend est en cours d'exécution et accessible
- Assurez-vous que le proxy est correctement configuré dans `package.json`
- Vérifiez les erreurs CORS dans la console du navigateur

### Problèmes de caméra (module OCR)
- Assurez-vous que le navigateur a les permissions d'accès à la caméra
- Vérifiez que vous utilisez un navigateur moderne (Chrome, Firefox, Edge) qui supporte les API WebRTC
- Testez sur HTTPS, car certains navigateurs restreignent l'accès à la caméra sur HTTP

### Erreurs lors des requêtes API
- Consultez la console du navigateur pour obtenir des détails sur les erreurs
- Vérifiez que les formats de données envoyés correspondent à ceux attendus par l'API
- Assurez-vous que l'authentification fonctionne correctement (si requise)