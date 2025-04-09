# Module de Gestion des Abonnements

## Description
Le module de gestion des abonnements constitue la base de notre modèle économique. Ce système gère l'ensemble du cycle de vie des abonnements, de l'acquisition au renouvellement, en passant par la facturation et la rétention, avec une expérience utilisateur fluide et une architecture technique adaptée à notre phase de pré-développement.

## Fonctionnalités Prévues

- **Inscription multi-méthodes** : Email, OAuth 2.0 (Google, Apple, Facebook)
- **Système de paiement** : Support des principales devises et méthodes de paiement
- **Gestion des abonnements** :
  - Formule Standard (19,90€/mois)
  - Formule Premium (29,90€/mois)
  - Options de facturation mensuelle et annuelle avec remise 10%
  - Période d'essai de 14 jours
- **Intégration Stripe** : Webhooks pour gestion automatisée des événements de paiement
- **Tableau de bord utilisateur** : Historique, factures, gestion autonome
- **Système de rétention** : Détection des risques de churn et communications ciblées

## Architecture Technique

### Infrastructure
- **Architecture serverless** : Déploiement simplifié et coûts optimisés
- **Base de données** : Stockage sécurisé des données d'abonnement
- **APIs RESTful** : Interfaces standardisées pour les interactions
- **Scaling progressif** : Structure prévue pour l'évolution du nombre d'utilisateurs

### Sécurité et Conformité
- **Chiffrement des données sensibles** : Protection des informations de paiement
- **Authentification sécurisée** : Protection des comptes utilisateurs
- **Conformité RGPD** : Respect des normes de protection des données
- **Journalisation** : Suivi des transactions et accès

## Options d'Abonnement

### Formule Standard (19,90€/mois)
- Diagnostic OBD-II en temps réel et historique
- Reconnaissance de pièces par image
- Assistant NLP automobile
- Recherche de pièces détachées avec comparateur de prix
- OCR pour documents véhicule
- Dongle OBD-II standard inclus

### Formule Premium (29,90€/mois)
- Tout le contenu Standard +
- Diagnostic avancé
- Reconnaissance de pièces illimitée
- Cartographies personnalisées
- Rapports détaillés exportables
- Support premium prioritaire
- Dongle OBD-II Pro haute fréquence inclus

## Métriques de Performance Visées

| Métrique | Cible Année 1 | Cible Année 2 | Cible Année 3 |
|----------|---------------|---------------|---------------|
| Taux conversion essai → payant | 3.5% | 4.2% | 5.0% |
| Taux de churn mensuel Standard | 4.5% | 4.0% | 3.5% |
| Taux de churn mensuel Premium | 4.0% | 3.5% | 3.0% |
| Taux de conversion Standard → Premium | 3.5%/trimestre | 4.5%/trimestre | 5.5%/trimestre |
| Durée moyenne d'abonnement (mois) | 10.5 | 12.8 | 15.0 |
| LTV Standard | 295€ | 320€ | 345€ |
| LTV Premium | 510€ | 550€ | 590€ |

## Intégration Technique

### APIs Principales
- **API Authentication**: `POST /api/v1/auth/token`
- **API Abonnements**: `GET|POST|PUT /api/v1/subscriptions`
- **API Paiements**: `GET|POST /api/v1/payments`
- **API Webhooks**: `POST /api/v1/webhooks/callbacks`
- **API Utilisateurs**: `GET|POST|PUT /api/v1/users`

### Exemples d'Utilisation

#### Inscription et Création d'Abonnement
```javascript
// Requête d'inscription/abonnement
const response = await fetch('/api/v1/subscriptions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`
  },
  body: JSON.stringify({
    user: {
      email: 'utilisateur@example.com',
      name: 'John Doe',
      locale: 'fr_FR',
      referral_source: 'google_ads'
    },
    subscription: {
      plan_id: 'price_standard_monthly',
      payment_method: 'card',
      billing_cycle: 'monthly',
      trial_days: 14
    }
  })
});

// Traitement de la réponse
const result = await response.json();
if (result.status === 'success') {
  console.log(`Abonnement créé avec succès! ID: ${result.subscription.id}`);
  // Redirection vers onboarding
} else {
  console.error(`Erreur: ${result.message}`);
  // Afficher erreur et suggestions
}
```

#### Webhooks de Gestion d'Événements
```javascript
// Dans la route Express pour le webhook
app.post('/api/v1/webhooks/stripe', express.raw({type: 'application/json'}), async (req, res) => {
  const signature = req.headers['stripe-signature'];
  
  try {
    // Vérification de l'authenticité du webhook
    const event = stripe.webhooks.constructEvent(
      req.body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET
    );
    
    // Traitement basé sur le type d'événement
    switch (event.type) {
      case 'invoice.payment_succeeded':
        await handleSuccessfulPayment(event.data.object);
        break;
      case 'customer.subscription.updated':
        await handleSubscriptionUpdate(event.data.object);
        break;
      case 'customer.subscription.deleted':
        await handleSubscriptionCancellation(event.data.object);
        break;
      // Autres cas...
    }
    
    res.status(200).json({received: true});
  } catch (err) {
    console.error(`Webhook error: ${err.message}`);
    res.status(400).send(`Webhook Error: ${err.message}`);
  }
});

// Fonction de traitement du paiement réussi
async function handleSuccessfulPayment(invoice) {
  const subscription = await db.subscriptions.findOne({
    where: { stripe_subscription_id: invoice.subscription }
  });
  
  if (subscription) {
    // Mise à jour du statut et date d'expiration
    await subscription.update({
      status: 'active',
      current_period_end: new Date(invoice.lines.data[0].period.end * 1000),
      latest_invoice_id: invoice.id,
      updated_at: new Date()
    });
    
    // Déclencher actions post-paiement
    await triggerPostPaymentActions(subscription.user_id, invoice);
  }
}
```

## Système de Rétention

Le module intègre un système de rétention qui vise à :

1. **Détecter les signaux de désengagement**:
   - Baisse de fréquence d'utilisation
   - Utilisation limitée des fonctionnalités

2. **Déclencher des communications ciblées**:
   - Emails personnalisés avec conseils d'utilisation
   - Notifications sur les fonctionnalités non explorées
   - Rappels avant la fin de période d'essai

3. **Optimiser via tests**:
   - Tests A/B sur les messages et offres
   - Ajustement du timing des communications
   - Personnalisation par segment d'utilisateurs

## Expansion Internationale Planifiée

Le module de gestion des abonnements est conçu pour soutenir l'expansion internationale avec :

- Support multi-devises
- Options de paiement adaptées aux marchés locaux
- Gestion fiscale par pays (TVA, taxes locales)
- Localisation (langues, formats)

Notre plan prévoit un déploiement progressif dans les principaux marchés européens après la validation du modèle en France.

## Tableau de Bord Admin

L'interface d'administration comprendra :

- **Vue d'ensemble** :
  - Nombre d'abonnés par formule
  - Taux de conversion et de churn
  - Revenus mensuels récurrents (MRR)

- **Analyses** :
  - Cohortes d'utilisateurs
  - Performances par canal d'acquisition
  - Comportements d'usage

- **Outils de gestion** :
  - Gestion des comptes utilisateurs
  - Administration des formules d'abonnement
  - Suivi des paiements et factures

## Évolutions Futures Envisagées

| Phase | Fonctionnalité | Bénéfice Attendu |
|-------|----------------|------------------|
| Phase 2 | Offres promotionnelles personnalisées | +15% taux de conversion |
| Phase 2 | Paiements via Apple Pay/Google Pay | Réduction friction inscription |
| Phase 3 | Programme de fidélité | -20% taux de churn |
| Phase 3 | Options de facturation flexibles | Adaptation à plus de marchés |

---

*Document mis à jour le 9 avril 2025*  
*Prochaine révision planifiée: Après développement du MVP*