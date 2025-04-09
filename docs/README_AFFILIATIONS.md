# Module d'Affiliation Global

## Description
Le module d'affiliation est une solution complète pour suivre, attribuer et gérer les commissions sur 100% des achats effectués via l'application. Le système fonctionne pour tous les types de produits et services proposés : cartographies moteur, pièces détachées, accessoires, abonnements, et autres services automobiles.

## Fonctionnalités principales
- Suivi intégral de toutes les transactions via l'application
- Système de tracking multi-couches pour une attribution infaillible
- Interface de gestion des partenaires et commissions
- Rapports détaillés sur les conversions et revenus
- API complète pour l'intégration avec tous les modules de l'application

## Système de suivi d'affiliation robuste

Notre système d'affiliation a été conçu avec une architecture de tracking inviolable garantissant le suivi de **100% des achats** réalisés via l'application. Cette couverture totale est assurée par :

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
- Compte sur notre plateforme d'affiliation centralisée
- Accès aux APIs des partenaires commerciaux
- Les dépendances Python : `requests`, `urllib3`, `beautifulsoup4` (pour certaines intégrations)

### Configuration
Configurez les variables d'environnement dans le fichier `.env` :
```
AFFILIATION_API_KEY=your_affiliation_api_key
AFFILIATION_SECRET=your_affiliation_secret
AFFILIATION_WEBHOOK_URL=https://your-app.com/api/affiliation/webhook
```

## Structure du module
- `affiliations_main.py` : Fichier principal contenant la logique de tracking
- `partners.py` : Gestion des partenaires commerciaux
- `tracking.py` : Mécanismes de suivi des conversions
- `reporting.py` : Génération de rapports et statistiques

## Utilisation

### Suivi d'un achat
```python
from affiliations.affiliations_main import track_purchase

# Suivre un achat
purchase_data = {
    "product_type": "cartographie",  # Type de produit (cartographie, pièce, accessoire, etc.)
    "product_id": "cart-123",        # ID du produit
    "price": 299.90,                 # Prix
    "partner_id": "partner-456",     # ID du partenaire
    "user_id": "user-789",           # ID de l'utilisateur
    "session_id": "sess-abc123"      # ID de session pour le tracking
}
tracking_result = track_purchase(purchase_data)
print(f"Suivi d'achat: {tracking_result}")
```

### Génération d'un lien d'affiliation
```python
from affiliations.tracking import generate_affiliate_link

# Créer un lien d'affiliation
affiliate_link = generate_affiliate_link(
    target_url="https://partner-site.com/product/123",
    user_id="user-456",
    product_id="prod-789",
    campaign="summer_sale"
)
print(f"Lien d'affiliation: {affiliate_link}")
```

### Exemple d'intégration avec Flask
```python
@app.route('/affiliations/track', methods=['POST'])
def track_affiliate_purchase():
    """
    Endpoint pour le suivi des achats affiliés
    
    Accepte une requête POST avec un JSON contenant les données d'achat
    """
    if not request.is_json:
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide. Veuillez envoyer un JSON avec les informations requises.'
        }), 400
    
    data = request.get_json()
    required_fields = ["product_type", "product_id", "price", "partner_id", "user_id"]
    
    if not all(field in data for field in required_fields):
        return jsonify({
            'status': 'error',
            'message': 'Champs requis manquants.'
        }), 400
    
    try:
        result = track_purchase(data)
        return jsonify({"status": "success", "tracking_id": result["tracking_id"]})
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du suivi de l\'achat: {str(e)}'
        }), 500
```

## Types de produits supportés

Le module d'affiliation prend en charge tous les types de produits et services :

1. **Cartographies moteur** : Reprogrammations ECU pour diverses marques et modèles
2. **Pièces détachées** : Pièces d'origine, sportives ou compétition
3. **Accessoires automobile** : Intérieur, extérieur, multimédia, etc.
4. **Équipements de diagnostic** : Dongles, scanners, interfaces spécialisées
5. **Services** : Prestations d'atelier partenaires, formations, consultation technique

## Structure des données de tracking

Chaque transaction suivie contient les informations suivantes :

```python
{
    "tracking_id": "trk-123456789",              # ID unique de tracking
    "timestamp": "2025-04-09T14:32:45.123Z",     # Horodatage précis de la transaction
    "product_type": "cartographie",              # Type de produit
    "product_id": "cart-123",                    # ID du produit
    "price": 299.90,                             # Prix
    "currency": "EUR",                           # Devise
    "partner_id": "partner-456",                 # ID du partenaire
    "user_id": "user-789",                       # ID de l'utilisateur
    "session_id": "sess-abc123",                 # ID de session
    "referrer": "https://example.com/search",    # Page référente
    "device_info": {                             # Informations sur l'appareil
        "user_agent": "Mozilla/5.0...",
        "device_type": "desktop",
        "fingerprint": "fp-987654321"
    },
    "commission": {                              # Détails de la commission
        "rate": 0.15,                            # Taux de commission (15%)
        "amount": 44.99,                         # Montant de la commission
        "status": "pending"                      # Statut (pending, validated, paid)
    }
}
```

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/affiliations/track` | POST | Suivi d'un achat affilié |
| `/affiliations/links/generate` | POST | Génération d'un lien d'affiliation |
| `/affiliations/partners` | GET | Liste des partenaires disponibles |
| `/affiliations/reports` | GET | Rapports et statistiques d'affiliation |
| `/affiliations/webhook` | POST | Réception des notifications des partenaires |

## Partenaires commerciaux

Le module est intégré avec de nombreux partenaires, notamment :

- Préparateurs automobiles (cartographies)
- Vendeurs de pièces détachées 
- Fabricants d'accessoires
- Places de marché spécialisées
- Fournisseurs d'équipements de diagnostic

Chaque partenaire dispose d'un taux de commission personnalisé et d'une période de validation spécifique.

## Reporting et statistiques

Le module génère des rapports détaillés sur les performances d'affiliation :

- Taux de conversion par produit et partenaire
- Revenus générés par type de produit
- Tendances et saisonnalité des ventes
- Analyses détaillées du parcours d'achat
- Alertes de performance

## Bonnes pratiques

- Utilisez toujours la fonction `track_purchase()` pour tout type d'achat
- Générez systématiquement des liens via `generate_affiliate_link()` pour assurer le suivi
- Vérifiez régulièrement les rapports pour identifier d'éventuelles anomalies
- Respectez la durée de vie des cookies de tracking (90 jours par défaut)
- Implémentez les webhooks partenaires pour une validation croisée des transactions

## Dépannage

- **Problème** : Transaction non suivie
  - **Solution** : Vérifiez que tous les paramètres requis sont présents et que l'utilisateur n'a pas désactivé les cookies

- **Problème** : Commission non attribuée
  - **Solution** : Examinez les logs de tracking et contactez le partenaire pour une vérification croisée

- **Problème** : Erreurs dans les rapports
  - **Solution** : Rafraîchissez les données et vérifiez la synchronisation avec la base de données partenaire

## Évolutions futures
- Implémentation d'un tableau de bord dédié pour les statistiques en temps réel
- Système de gestion des programmes multi-niveaux
- Intégration de paiements automatisés pour les commissions
- API publique pour les partenaires souhaitant intégrer notre système
- Système de recommandation personnalisée basé sur l'historique des achats