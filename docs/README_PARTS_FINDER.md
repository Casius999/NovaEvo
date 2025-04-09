# Module Parts Finder

## Objectif global

Le module Parts Finder est conçu pour rechercher des pièces détachées automobiles à partir de différentes sources, permettant aux utilisateurs de trouver rapidement les meilleures offres pour des pièces spécifiques. Le module combine à la fois des recherches dans des API officielles de partenaires et du scraping web pour offrir une vision complète du marché.

## Sources de données

### 1. API Officielles

Le module se connecte aux API des partenaires suivants :
- **Oscaro** : Fournisseur majeur de pièces détachées avec une large gamme de produits
- **Mister Auto** : Alternative compétitive avec des pièces de qualité
- **Amazon** : Marketplace généraliste avec une section automobile
- **eBay Motors** : Spécialiste des pièces neuves et d'occasion

La connexion à ces API nécessite des clés d'API valides configurées dans les variables d'environnement :
```
OSCARO_API_KEY=votre_clé_api
MISTER_AUTO_API_KEY=votre_clé_api
AMAZON_API_KEY=votre_clé_api
EBAY_API_KEY=votre_clé_api
```

### 2. Facebook Marketplace

Le module utilise des techniques de scraping web pour extraire des annonces pertinentes depuis Facebook Marketplace. Cette source est particulièrement utile pour trouver des pièces d'occasion à prix avantageux.

**Remarque** : L'accès à certaines fonctionnalités de Facebook peut nécessiter une authentification.

### 3. Leboncoin

Site d'annonces français incontournable, Leboncoin est une excellente source pour les pièces d'occasion. Le module scrape les résultats de recherche pour trouver des offres correspondant aux critères spécifiés.

### 4. Groupes Facebook spécialisés

Les groupes Facebook dédiés aux pièces détachées automobiles sont une mine d'or pour les pièces rares ou spécifiques. Le module peut explorer ces groupes pour en extraire les annonces pertinentes.

**Remarque** : L'accès aux groupes Facebook nécessite généralement une authentification.

### 5. Base de données locale

Une base de données locale (SQLite par défaut) stocke un catalogue de pièces avec des informations sur la compatibilité avec différents modèles de véhicules. Cette base peut servir de référence ou de fallback quand les APIs ou le scraping ne donnent pas de résultats satisfaisants.

## Configuration requise

### Bibliothèques Python

```
pip install requests beautifulsoup4 selenium dotenv sqlite3
```

### Pilotes pour Selenium (optionnel pour le scraping avancé)

Pour le scraping de contenus dynamiques (notamment sur Facebook), il est recommandé d'installer un WebDriver :
- Chrome : [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/)
- Firefox : [GeckoDriver](https://github.com/mozilla/geckodriver/releases)

## Structure du code

Le module Parts Finder est organisé de la manière suivante :

```
parts_finder/
├── __init__.py
├── parts_finder_main.py    # Fichier principal avec toutes les fonctions
└── README.md               # Documentation spécifique au module
```

## Fonctions principales

### 1. `search_parts(reference: str, type_piece: str) -> list`

Fonction principale qui agrège les résultats de recherche de toutes les sources disponibles.

**Paramètres :**
- `reference` : Référence de la pièce à rechercher
- `type_piece` : Type de pièce, doit être l'un des suivants : "origine", "sport", "competition"

**Retour :**
- Liste d'objets représentant les pièces trouvées, triées par prix croissant

### 2. `search_official(reference: str, type_piece: str) -> list`

Recherche des pièces via les API officielles des partenaires.

### 3. `search_facebook_marketplace(reference: str, type_piece: str) -> list`

Recherche des pièces sur Facebook Marketplace via scraping.

### 4. `search_leboncoin(reference: str, type_piece: str) -> list`

Recherche des pièces sur Leboncoin via scraping.

### 5. `search_facebook_groups(reference: str, type_piece: str) -> list`

Recherche des pièces dans les groupes Facebook spécialisés.

### 6. `PartsFinderManager`

Classe qui gère la recherche dans la base de données locale et fournit des méthodes comme :
- `search_parts_local` : Recherche des pièces dans la base locale
- `get_part_details` : Obtient les détails complets d'une pièce

## Intégration dans l'API

Le module est intégré dans l'application principale via l'endpoint `/parts_finder` qui accepte une requête POST avec les paramètres de recherche :

```json
{
  "reference": "F-001",
  "type": "sport"
}
```

## Exemples d'utilisation

### Recherche simple

```python
from parts_finder.parts_finder_main import search_parts

results = search_parts("F-001", "sport")
for result in results:
    print(f"{result['name']} - {result['price']} {result['currency']} - {result['source']}")
```

### Recherche avec filtres additionnels

```python
from parts_finder.parts_finder_main import PartsFinderManager

finder = PartsFinderManager()
results = finder.search_parts_local(
    manufacturer="Peugeot",
    model="208",
    category="Freinage",
    part_type="sport",
    keyword="performance"
)

for part in results["results"]:
    print(f"{part['name']} - {part['price']} €")
```

### Obtenir les détails d'une pièce

```python
from parts_finder.parts_finder_main import PartsFinderManager

finder = PartsFinderManager()
part = finder.get_part_details(reference="F-002")

if "success" in part and part["success"]:
    part_info = part["part"]
    print(f"Nom: {part_info['name']}")
    print(f"Prix: {part_info['price']} {part_info['currency']}")
    print(f"Description: {part_info['description']}")
    print("Modèles compatibles:")
    for model in part_info["compatible_models"]:
        print(f"  - {model['manufacturer']} {model['name']} ({model['years']})")
```

## Notes importantes

1. **Limites du scraping web** : Le scraping de sites comme Facebook ou Leboncoin peut être sujet à des changements dans la structure HTML, ce qui peut causer des erreurs. Il est recommandé de vérifier régulièrement que les sélecteurs CSS sont toujours valides.

2. **Authentification** : L'accès à certaines fonctionnalités de Facebook (groupes, marketplace) peut nécessiter une authentification. Dans un environnement de production, il faudrait gérer les sessions de manière sécurisée.

3. **Respect des TOS** : Assurez-vous de respecter les conditions d'utilisation des sites que vous scrapez, notamment en ce qui concerne la fréquence des requêtes.

4. **Simulateur de résultats** : En cas d'échec de connexion aux API ou de scraping, le module peut générer des résultats simulés pour les démonstrations.

## Tests

Des tests unitaires sont disponibles dans `/tests/test_parts_finder.py` et peuvent être exécutés avec pytest :

```
pytest tests/test_parts_finder.py
```

Ces tests couvrent les fonctionnalités principales du module, y compris la recherche locale et les interactions avec les API externes (avec mocks).