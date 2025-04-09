# Guide d'Internationalisation (i18n)

Ce document explique comment contribuer à l'internationalisation de l'Assistant Auto Ultime, permettant ainsi à l'application d'être utilisée dans différentes langues et régions.

## Introduction

L'Assistant Auto Ultime utilise la bibliothèque `react-i18next` pour le frontend et des fichiers de traduction basés sur JSON pour le backend. Ce système permet de prendre en charge plusieurs langues tout en maintenant une base de code unique.

## Structure des fichiers de traduction

### Frontend (React)

Les fichiers de traduction du frontend sont situés dans :

```
frontend/src/locales/{code_langue}/translation.json
```

Où `{code_langue}` est le code de langue ISO-639-1 à deux lettres (ex : `fr` pour français, `en` pour anglais, `de` pour allemand).

Exemple de structure pour le français (`frontend/src/locales/fr/translation.json`) :

```json
{
  "common": {
    "welcome": "Bienvenue sur Assistant Auto Ultime",
    "loading": "Chargement en cours...",
    "error": "Une erreur est survenue"
  },
  "nav": {
    "home": "Accueil",
    "ocr": "Scanner carte grise",
    "obd": "Diagnostic OBD-II",
    "ecu": "Reprogrammation ECU",
    "parts": "Pièces détachées",
    "subscriptions": "Abonnements",
    "mappings": "Cartographies moteur"
  },
  "ocr": {
    "title": "Scanner de carte grise",
    "instruction": "Prenez en photo votre carte grise",
    "scan": "Scanner",
    "processing": "Analyse en cours..."
  }
}
```

### Backend (Python Flask)

Les fichiers de traduction du backend sont situés dans :

```
locales/{code_langue}/messages.json
```

Exemple pour le français (`locales/fr/messages.json`) :

```json
{
  "error_messages": {
    "invalid_request": "Requête invalide",
    "not_found": "Ressource non trouvée",
    "server_error": "Erreur serveur interne"
  },
  "obd": {
    "connection_error": "Erreur de connexion au véhicule",
    "dtc_codes": "Codes défaut détectés",
    "no_dtc": "Aucun code défaut détecté"
  }
}
```

## Ajout d'une nouvelle langue

### 1. Créer les fichiers de traduction

Pour ajouter une nouvelle langue (par exemple l'espagnol) :

1. **Frontend** : 
   - Créez le dossier `frontend/src/locales/es/`
   - Copiez `translation.json` depuis une langue existante (ex : `fr`) et traduisez son contenu

2. **Backend** : 
   - Créez le dossier `locales/es/`
   - Copiez `messages.json` depuis une langue existante et traduisez son contenu

### 2. Enregistrer la nouvelle langue dans l'application

#### Pour le frontend :

Modifiez le fichier `frontend/src/i18n.js` pour ajouter la nouvelle langue :

```javascript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import des ressources de traduction
import translationEN from './locales/en/translation.json';
import translationFR from './locales/fr/translation.json';
import translationES from './locales/es/translation.json'; // Nouvelle langue

const resources = {
  en: {
    translation: translationEN
  },
  fr: {
    translation: translationFR
  },
  es: {                      // Ajout de l'espagnol
    translation: translationES
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'fr',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
```

#### Pour le backend :

Modifiez le fichier `app.py` pour prendre en charge la nouvelle langue :

```python
# Liste des langues supportées
SUPPORTED_LANGUAGES = ['en', 'fr', 'es']  # Ajout de 'es'
```

### 3. Mettre à jour le sélecteur de langue

Assurez-vous que la nouvelle langue apparaît dans le sélecteur de langue de l'interface utilisateur.

## Utilisation des traductions

### Dans le code React (Frontend)

```javascript
import React from 'react';
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t, i18n } = useTranslation();

  // Changer de langue
  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div>
      <h1>{t('common.welcome')}</h1>
      <p>{t('ocr.instruction')}</p>
      
      <div>
        <button onClick={() => changeLanguage('fr')}>Français</button>
        <button onClick={() => changeLanguage('en')}>English</button>
        <button onClick={() => changeLanguage('es')}>Español</button>
      </div>
    </div>
  );
}
```

### Dans le code Python (Backend)

```python
from flask import request, jsonify, g

# Fonction auxiliaire pour obtenir les traductions
def get_translation(key, language=None):
    if language is None:
        language = request.headers.get('Accept-Language', 'fr').split(',')[0][:2]
    
    if language not in SUPPORTED_LANGUAGES:
        language = 'fr'  # Langue par défaut
    
    # Charger le fichier de traduction
    with open(f'locales/{language}/messages.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    # Accéder à la clé de traduction (format: "section.key")
    keys = key.split('.')
    result = translations
    for k in keys:
        if k in result:
            result = result[k]
        else:
            return key  # Clé non trouvée, retourner la clé d'origine
    
    return result

# Exemple d'utilisation
@app.route('/api/error')
def error_example():
    error_message = get_translation('error_messages.not_found')
    return jsonify({'error': error_message})
```

## Bonnes pratiques pour l'internationalisation

1. **Utilisez des clés hiérarchiques** : Organisez vos traductions avec une structure hiérarchique pour éviter les conflits de noms et faciliter la maintenance.

2. **Évitez les chaînes codées en dur** : Toutes les chaînes visibles par l'utilisateur doivent provenir des fichiers de traduction.

3. **Gérez le pluriel correctement** : Utilisez des fonctions spécifiques pour gérer les formes plurielles, qui peuvent varier considérablement selon les langues.
   ```javascript
   // Exemple avec react-i18next
   t('cart.items', { count: itemCount })
   ```

4. **Tenez compte des différences culturelles** : 
   - Formats de date et d'heure (MM/JJ/AAAA vs JJ/MM/AAAA)
   - Formats numériques (1,000.00 vs 1.000,00)
   - Unités de mesure (miles vs kilomètres)

5. **Testez dans toutes les langues** : Vérifiez que l'interface s'affiche correctement dans toutes les langues supportées (problèmes de mise en page avec des textes plus longs).

## Workflow de traduction

1. **Extraction** : Extraire les nouvelles chaînes à traduire à chaque mise à jour significative
2. **Traduction** : Traduire les nouvelles chaînes dans toutes les langues supportées
3. **Intégration** : Intégrer les nouvelles traductions dans le projet
4. **Vérification** : Tester l'application dans toutes les langues pour s'assurer que tout s'affiche correctement

## Outils utiles

- **i18next-scanner** : Pour extraire automatiquement les chaînes traduisibles du code source
- **Weblate** ou **Crowdin** : Plateformes de traduction collaborative
- **react-i18next-extract** : Pour générer automatiquement des fichiers de traduction à partir du code React

## Ressources

- [Documentation de react-i18next](https://react.i18next.com/)
- [Guide des meilleures pratiques i18n](https://phrase.com/blog/posts/i18n-best-practices/)
- [ISO-639-1 Codes de langue](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)