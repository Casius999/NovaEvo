# Module d'Affiliation de Cartographies

## Description
Le module d'affiliation de cartographies est une solution pour connecter les utilisateurs avec des préparateurs automobiles proposant des services de reprogrammation moteur. Le module effectue des recherches multi-sources (API partenaires, Facebook Marketplace, Leboncoin, groupes Facebook) pour proposer des offres personnalisées et générer des revenus par affiliation.

## Fonctionnalités principales
- Recherche de cartographies par modèle de véhicule et catégorie
- Agrégation de résultats depuis différentes sources
- Filtrage et tri des offres (prix, note, catégorie)
- Génération de liens d'affiliation pour le suivi des conversions
- Interface utilisateur responsive pour la présentation des offres

## Système de suivi d'affiliation robuste

Notre système d'affiliation global a été conçu avec une architecture de tracking inviolable garantissant le suivi de **100% des achats** réalisés via l'application, qu'il s'agisse de cartographies moteur, de pièces détachées ou de tout autre produit ou service proposé. Cette couverture totale est assurée par :

- **Redirections sécurisées** : Toutes les redirections sont effectuées via notre serveur de tracking avant d'atteindre le site du partenaire
- **Cookies persistants multi-domaines** avec durée de vie prolongée (90 jours) 
- **Paramètres de suivi UTM** automatiquement ajoutés à toutes les URL (source, medium, campaign, content, term)
- **Double tracking client/serveur** pour assurer une redondance en cas de blocage des cookies
- **Identifiants de session uniques** liés au compte utilisateur et à l'appareil
- **Webhook de confirmation** avec les partenaires pour validation croisée des transactions
- **Fingerprinting d'appareil** comme méthode de secours pour associer les conversions

Grâce à ces mécanismes combinés, le système garantit qu'aucune transaction affiliée ne manque d'être suivie, quelle que soit sa nature, et nous bénéficions de la totalité des commissions sur chaque achat effectué via notre plateforme.

## Installation et configuration

### Prérequis
- Comptes API chez les partenaires de cartographie
- Accès aux APIs de médias sociaux (Facebook API, si applicable)
- Les dépendances Python: `requests`, `beautifulsoup4`, `selenium` (pour le scraping)

### Configuration
Configurez les variables d'environnement dans le fichier `.env` :
```
MAPPING_API_KEY=your_mapping_api_key
MAPPING_API_URL=https://api.tuners.example.com/mappings
MAPPING_AFFILIATE_ID=your_affiliate_id
```

## Structure du module
- `mapping_affiliations_main.py` : Fichier principal contenant la logique de recherche
- Fonctions de recherche par source (API officielle, Facebook, Leboncoin, etc.)
- Système de données de démonstration pour le développement

## Utilisation

### Recherche de cartographies
```python
from mapping_affiliations.mapping_affiliations_main import search_mapping_offers

# Rechercher des cartographies pour un véhicule spécifique
results = search_mapping_offers(query="cartographie golf 7 gti", category="sport")

# Afficher les résultats
for offer in results:
    print(f"Préparateur: {offer['preparateur']}")
    print(f"Description: {offer['description']}")
    print(f"Prix: {offer['price']}")
    print(f"Catégorie: {offer['category']}")
    print(f"Source: {offer['source']}")
    print(f"Lien d'affiliation: {offer['affiliate_link']}")
    print("---")
```

### Recherche par source spécifique
```python
from mapping_affiliations.mapping_affiliations_main import search_facebook_marketplace_mapping

# Rechercher uniquement sur Facebook Marketplace
facebook_results = search_facebook_marketplace_mapping(
    query="reprogrammation bmw 320d", 
    category="origine"
)

# Afficher les résultats
for offer in facebook_results:
    print(f"Offre Facebook: {offer['description']} - {offer['price']}")
```

### Exemple d'utilisation avec Flask
```python
@app.route('/mapping_affiliations', methods=['POST'])
def mapping_affiliations_endpoint():
    """
    Endpoint pour le module d'affiliation cartographies
    
    Accepte une requête POST avec un JSON contenant "query" et optionnellement "category"
    """
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide. Veuillez envoyer un JSON avec les informations requises.'
        }), 400
    
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({
            'status': 'error',
            'message': 'Le paramètre "query" est obligatoire.'
        }), 400
    
    query = data["query"]
    category = data.get("category")
    
    try:
        offers = search_mapping_offers(query, category)
        return jsonify({"offers": offers})
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la recherche de cartographies: {str(e)}'
        }), 500
```

## Catégories de cartographies

Le module prend en charge trois catégories principales de cartographies :

1. **Origine / Éco** : Cartographies visant l'optimisation de la consommation et le respect des normes d'émission tout en offrant un gain modéré en performances.

2. **Sport** : Cartographies équilibrées offrant des gains significatifs en puissance et couple tout en conservant une fiabilité moteur élevée.

3. **Compétition** : Cartographies à hautes performances destinées à un usage circuit ou compétition, avec des gains maximisés mais une fiabilité parfois réduite.

## Structure des données de résultats

Chaque offre de cartographie est représentée par un dictionnaire avec les champs suivants :

```python
{
    "preparateur": "Nom du préparateur ou vendeur",
    "description": "Description complète de la cartographie",
    "price": "249.90€",  # Prix formaté avec devise
    "affiliate_link": "https://exemple.com/cartographie?ref=assistant-auto-ultime",
    "category": "sport",  # origine, sport ou competition
    "source": "API Partenaire",  # Source de l'offre
    
    # Champs optionnels selon la source
    "rating": 4.5,  # Note sur 5 si disponible
    "gains": {
        "puissance": "+15%",
        "couple": "+20%",
        "consommation": "-10%"
    },
    "compatibility": ["Golf 7 GTI", "Golf 7 R"],
    "location": "Paris",  # Pour les offres de marketplace
    "urgent": True,  # Flag d'urgence pour Leboncoin
    "pro": True  # Vendeur professionnel
}
```

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/mapping_affiliations` | POST | Recherche de cartographies affiliées |

## Interface utilisateur
Le module inclut un composant React (`MappingAffiliations.js`) qui permet de :
- Rechercher des cartographies avec filtres
- Afficher les résultats avec tri personnalisable
- Filtrer par fourchette de prix
- Rediriger vers les liens d'affiliation

## Limitations actuelles
- Le scraping de Facebook Marketplace peut nécessiter des ajustements fréquents en fonction des changements de structure HTML
- La fonction démo (`get_demo_data`) est utilisée en développement pour simuler les résultats

## Bonnes pratiques pour le scraping
- Respectez les conditions d'utilisation des sites sources
- Implémentez une stratégie de backoff exponentiel pour éviter le blocage
- Utilisez des headers réalistes et variez les User-Agents
- Limitez la fréquence des requêtes
- Mettez en cache les résultats pour éviter les requêtes répétées

## Dépannage

- **Problème** : Aucun résultat retourné
  - **Solution** : Vérifiez que les APIs partenaires sont accessibles et que les clés API sont valides

- **Problème** : Erreur lors du scraping
  - **Solution** : Vérifiez que la structure HTML des sites cibles n'a pas changé et mettez à jour les sélecteurs

- **Problème** : Temps de réponse lent
  - **Solution** : Implémentez un système de mise en cache des résultats fréquents et optimisez les requêtes

## Évolutions futures
- Implémentation d'une authentification OAuth pour l'accès aux API Facebook
- Système de notation des préparateurs par les utilisateurs
- Intégration de nouvelles sources de cartographies
- Système de recommandation basé sur le profil du véhicule de l'utilisateur