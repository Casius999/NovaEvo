# Module de Gestion des Abonnements

## Description
Le module de gestion des abonnements permet d'intégrer un système d'abonnement complet à l'application Assistant Auto Ultime. Il gère l'inscription des utilisateurs, la création d'abonnements via Stripe et le suivi des statuts d'abonnement.

## Fonctionnalités principales
- Inscription et authentification des utilisateurs
- Gestion des abonnements via Stripe (19,90€/mois avec dongle OBD-II offert)
- Webhooks pour suivre les événements d'abonnement (paiements, annulations, etc.)
- Interface utilisateur pour la gestion des abonnements

## Installation et configuration

### Prérequis
- Compte Stripe avec API configurée
- Base de données SQLite (ou PostgreSQL/MySQL pour la production)
- Les dépendances Python: `flask`, `flask-login`, `flask-sqlalchemy`, `stripe`

### Configuration
1. Créer un compte Stripe et configurer les webhooks
2. Créer un produit et un plan d'abonnement dans Stripe (19,90€/mois)
3. Obtenir les clés API Stripe (secrète et publique)
4. Configurer les variables d'environnement dans le fichier `.env` :
   ```
   STRIPE_API_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_signing_secret
   STRIPE_PRICE_ID_BASIC=price_basic  # ID du plan d'abonnement standard
   STRIPE_PRICE_ID_PREMIUM=price_premium  # ID du plan d'abonnement premium
   ```

## Structure du module
- `subscriptions_main.py` : Le fichier principal contenant la logique d'abonnement
- Modèle `User` : Stocke les informations utilisateur et les détails d'abonnement
- Intégrations API avec Stripe

## Utilisation

### Initialisation du module
```python
from subscriptions.subscriptions_main import app as subscriptions_app

# Fusionner l'application Flask du module avec l'application principale
# (voir app.py pour l'implémentation complète)
```

### Inscription et création d'un abonnement
```python
from subscriptions.subscriptions_main import process_subscription

# Données utilisateur et abonnement
user_data = {
    "email": "utilisateur@example.com",
    "password": "motdepasse123",
    "name": "John Doe",
    "plan_id": "price_basic"  # ID du plan Stripe (19,90€/mois)
}

# Traiter l'inscription et l'abonnement
result = process_subscription(user_data)

# Vérifier le résultat
if result["status"] == "success":
    print(f"Abonnement créé avec succès! ID: {result['subscription_id']}")
else:
    print(f"Erreur: {result['message']}")
```

### Gestion des webhooks Stripe
```python
from subscriptions.subscriptions_main import webhook_handler

# Dans la route Flask pour le webhook
@app.route('/subscribe/webhook', methods=['POST'])
def subscribe_webhook_endpoint():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    if not sig_header:
        return jsonify({
            'status': 'error',
            'message': 'En-tête Stripe-Signature manquant'
        }), 400
    
    result = webhook_handler(payload, sig_header)
    return jsonify(result)
```

### Récupération des plans d'abonnement
```python
@app.route('/subscribe/plans', methods=['GET'])
def subscription_plans_endpoint():
    plans = [
        {
            "id": "price_basic",
            "name": "Formule Standard",
            "price": 19.90,
            "currency": "EUR",
            "interval": "month",
            "description": "Abonnement mensuel à 19,90€ avec dongle OBD-II offert",
            "features": [
                "Diagnostic OBD-II en temps réel",
                "Reconnaissance de pièces par image",
                "Assistant NLP automobile",
                "Recherche de pièces détachées",
                "OCR pour cartes grises",
                "Cartographies moteur standard",
                "Dongle OBD-II inclus"
            ]
        },
        # Autres plans...
    ]
    
    return jsonify({
        "status": "success",
        "plans": plans
    })
```

## Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/subscribe` | POST | Inscription utilisateur et création d'abonnement |
| `/subscribe/webhook` | POST | Gestion des webhooks Stripe |
| `/subscribe/plans` | GET | Récupération des plans d'abonnement disponibles |

## Modèle de données
Le module utilise un modèle utilisateur avec les champs suivants :
- `id` : Identifiant unique de l'utilisateur (clé primaire)
- `email` : Email de l'utilisateur (unique)
- `password_hash` : Mot de passe crypté
- `name` : Nom de l'utilisateur
- `stripe_customer_id` : Identifiant du client Stripe
- `subscription_id` : Identifiant de l'abonnement Stripe
- `subscription_status` : Statut de l'abonnement (`active`, `trialing`, `canceled`, etc.)
- `created_at` : Date de création du compte
- `updated_at` : Date de dernière mise à jour

## Gestion des abonnements côté frontend
Le module inclut un composant React (`Subscriptions.js`) qui permet de :
- Afficher les différents plans d'abonnement
- Gérer le formulaire d'inscription
- Traiter le paiement via Stripe
- Afficher le statut de l'abonnement

## Sécurité et bonnes pratiques
- Les mots de passe sont hachés avec `werkzeug.security`
- Les clés API Stripe ne sont jamais exposées côté client
- Les webhooks sont vérifiés avec la signature Stripe pour éviter les falsifications
- Les données sensibles sont exclues des réponses JSON

## Dépannage
- **Problème** : Erreur "Invalid API Key" dans Stripe
  - **Solution** : Vérifier que la variable d'environnement `STRIPE_API_KEY` est correctement configurée

- **Problème** : Erreur lors du webhook Stripe
  - **Solution** : Vérifier que l'URL du webhook est correctement configurée dans le dashboard Stripe et que le secret est à jour

- **Problème** : Échec de création de l'abonnement
  - **Solution** : Vérifier que l'ID du plan est correct et que le client Stripe est bien créé

## Limitations
- Le module ne gère pas encore le changement de plan d'abonnement
- Les remboursements doivent être traités manuellement via le dashboard Stripe
- L'expédition du dongle OBD-II doit être gérée séparément
