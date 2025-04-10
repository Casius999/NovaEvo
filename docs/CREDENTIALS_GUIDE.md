# 🔒 Guide Complet des Credentials NovaEvo

## Introduction

Ce document constitue la référence exhaustive et complète des credentials et accès obligatoires pour le projet NovaEvo. Il couvre l'ensemble des services, intégrations et API utilisés par la plateforme, aussi bien pour l'infrastructure cloud que pour les intégrations externes spécialisées dans le domaine automobile.

Chaque section présente :
- Le service principal recommandé
- Les credentials nécessaires et leur format
- Un plan de secours détaillé en cas d'indisponibilité du service principal
- Des liens vers la documentation officielle pour une vérifiabilité totale

## Table des Matières

1. [Infrastructure Cloud et Gestion des Secrets](#1-infrastructure-cloud-et-gestion-des-secrets)
2. [Bases de Données et Stockage](#2-bases-de-données-et-stockage)
3. [Intégrations et API Externes (Écosystème Automobile)](#3-intégrations-et-api-externes-écosystème-automobile)
4. [CI/CD et Gestion de Code Source](#4-cicd-et-gestion-de-code-source)
5. [Monitoring et Logging](#5-monitoring-et-logging)
6. [Messagerie et Notifications](#6-messagerie-et-notifications)
7. [Paiement et Monétisation](#7-paiement-et-monétisation)
8. [Authentification et Gestion des Utilisateurs](#8-authentification-et-gestion-des-utilisateurs)
9. [Analytics et Feedback](#9-analytics-et-feedback)
10. [Gestion des Secrets](#10-gestion-des-secrets)

## 1. Infrastructure Cloud et Gestion des Secrets

### Service Principal : Google Cloud Platform (GCP)

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Fichier JSON clé de compte service | Fichier JSON | Contient les informations d'authentification pour accéder aux services GCP | Google Cloud Secret Manager |
| Project ID | Chaîne (ex: `novaevo-production`) | Identifiant du projet GCP | Variables d'environnement |
| Accès cluster GKE | Fichiers kubeconfig et certificats | Credentials pour accéder au cluster Kubernetes | Stockage sécurisé local pour développeurs |

#### Configuration
```yaml
# Exemple de fichier JSON de clé de service (format)
{
  "type": "service_account",
  "project_id": "novaevo-production",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "novaevo-service@novaevo-production.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/novaevo-service%40novaevo-production.iam.gserviceaccount.com"
}
```

#### Variables d'environnement associées
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json
GOOGLE_CLOUD_PROJECT=novaevo-production
```

#### Plan de secours : Amazon Web Services (AWS)

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| AWS Access Key ID | Chaîne (ex: `AKIAIOSFODNN7EXAMPLE`) | Identifiant de clé d'accès | AWS Secrets Manager |
| AWS Secret Access Key | Chaîne | Clé d'accès secrète pour l'authentification | AWS Secrets Manager |
| AWS Region | Chaîne (ex: `eu-west-3`) | Région AWS utilisée | Variables d'environnement |
| EKS Cluster Access | Fichiers kubeconfig et certificats | Credentials pour accéder au cluster EKS | Stockage sécurisé local pour développeurs |

#### Documentation officielle
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)
- [GKE - Authentification et autorisation](https://cloud.google.com/kubernetes-engine/docs/concepts/access-control)
- [AWS IAM - Clés d'accès](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html)

## 2. Bases de Données et Stockage

### Service Principal : Google Cloud SQL

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Instance hostname | Chaîne (ex: `35.123.456.78`) | Adresse IP ou DNS de l'instance Cloud SQL | Variables d'environnement |
| Port | Nombre (ex: `5432`) | Port d'accès à la base de données | Variables d'environnement |
| Nom de la base | Chaîne (ex: `novaevo_prod`) | Nom de la base de données | Variables d'environnement |
| Nom d'utilisateur | Chaîne | Utilisateur de la base de données | Google Cloud Secret Manager |
| Mot de passe | Chaîne | Mot de passe d'accès à la base | Google Cloud Secret Manager |

#### Variables d'environnement associées
```
DB_TYPE=postgresql
DB_HOST=35.123.456.78
DB_PORT=5432
DB_NAME=novaevo_prod
DB_USER=novaevo_user
DB_PASSWORD=xxxxxxxxxxxxxxxx
```

### Service Principal : Google Cloud Storage

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Bucket Name | Chaîne (ex: `novaevo-assets`) | Nom du bucket pour le stockage d'objets | Variables d'environnement |
| Clé de service | Fichier JSON (même que GCP) | Authentification pour accéder au stockage | Google Cloud Secret Manager |

#### Variables d'environnement associées
```
CLOUD_STORAGE_ENABLED=True
CLOUD_STORAGE_PROVIDER=gcs
CLOUD_STORAGE_BUCKET=novaevo-assets
```

#### Plan de secours : Amazon RDS et S3

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| RDS Endpoint | Chaîne | Point de terminaison de l'instance RDS | Variables d'environnement |
| RDS Port | Nombre | Port d'accès à la base de données | Variables d'environnement |
| RDS DB Name | Chaîne | Nom de la base de données | Variables d'environnement |
| RDS Username | Chaîne | Utilisateur de la base de données | AWS Secrets Manager |
| RDS Password | Chaîne | Mot de passe d'accès | AWS Secrets Manager |
| S3 Bucket Name | Chaîne | Nom du bucket S3 | Variables d'environnement |
| AWS Access Key ID | Chaîne | Identifiant de clé d'accès | AWS Secrets Manager |
| AWS Secret Access Key | Chaîne | Clé d'accès secrète | AWS Secrets Manager |

#### Documentation officielle
- [Google Cloud SQL - Connexion à une instance](https://cloud.google.com/sql/docs/postgres/connect-overview)
- [Google Cloud Storage - Authentification](https://cloud.google.com/storage/docs/authentication)
- [Amazon RDS - Connection Parameters](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ConnectToInstance.html)
- [Amazon S3 - Authentification](https://docs.aws.amazon.com/AmazonS3/latest/userguide/authentication-and-access-control.html)

## 3. Intégrations et API Externes (Écosystème Automobile)

### 3.1 Diagnostic Véhicule

#### Service Principal : Otonomo

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| API Key | Chaîne (ex: `otm_api_12345abcdef`) | Clé d'API pour l'accès | Google Cloud Secret Manager |
| API Secret | Chaîne | Secret associé à la clé | Google Cloud Secret Manager |
| Client ID | Chaîne | Identifiant client OAuth | Google Cloud Secret Manager |
| Environment | Chaîne (ex: `production`, `sandbox`) | Environnement Otonomo | Variables d'environnement |

#### Variables d'environnement associées
```
OTONOMO_API_KEY=otm_api_12345abcdef
OTONOMO_API_SECRET=xxxxxxxxxxxxxxxx
OTONOMO_CLIENT_ID=ci_12345abcdef
OTONOMO_ENVIRONMENT=production
```

#### Plan de secours : CarAPI

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| API Key | Chaîne | Clé d'API CarAPI | Google Cloud Secret Manager |
| API Token | Chaîne | Token d'authentification | Google Cloud Secret Manager |
| Endpoint | URL | Endpoint de l'API | Variables d'environnement |

#### Documentation officielle
- [Otonomo API Documentation](https://developer.otonomo.io/docs)
- [CarAPI Documentation](https://www.car-api.com/documentation)

### 3.2 Recherche de Pièces & Affiliation

#### Service Principal : Parts Alliance / Marketparts API

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| API Key | Chaîne | Clé d'API | Google Cloud Secret Manager |
| Merchant ID | Chaîne | Identifiant marchand | Google Cloud Secret Manager |
| Environment | Chaîne | Environnement (production/test) | Variables d'environnement |

#### Variables d'environnement associées
```
PARTS_ALLIANCE_API_KEY=xxxxxxxxxxxxxxxx
PARTS_ALLIANCE_MERCHANT_ID=12345
PARTS_ALLIANCE_ENVIRONMENT=production
```

#### Service : Leboncoin via Lobstr.io

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| API Key | Chaîne | Clé d'API Lobstr | Google Cloud Secret Manager |
| Client ID | Chaîne | Identifiant client | Google Cloud Secret Manager |
| Client Secret | Chaîne | Secret client | Google Cloud Secret Manager |
| Redirect URI | URL | URI de redirection OAuth | Variables d'environnement |

#### Variables d'environnement associées
```
LOBSTR_API_KEY=xxxxxxxxxxxxxxxx
LOBSTR_CLIENT_ID=xxxxxxxxxxxxxxxx
LOBSTR_CLIENT_SECRET=xxxxxxxxxxxxxxxx
LOBSTR_REDIRECT_URI=https://novaevo.example.com/callback/lobstr
```

#### Service : Facebook Marketplace via API2Cart

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| API Key | Chaîne | Clé d'API API2Cart | Google Cloud Secret Manager |
| Store Key | Chaîne | Clé du magasin | Google Cloud Secret Manager |
| Facebook App ID | Chaîne | ID d'application Facebook | Google Cloud Secret Manager |
| Facebook App Secret | Chaîne | Secret d'application Facebook | Google Cloud Secret Manager |

#### Variables d'environnement associées
```
API2CART_API_KEY=xxxxxxxxxxxxxxxx
API2CART_STORE_KEY=xxxxxxxxxxxxxxxx
FACEBOOK_APP_ID=123456789012345
FACEBOOK_APP_SECRET=xxxxxxxxxxxxxxxx
```

#### Service : API-Car pour casses auto

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| API Key | Chaîne | Clé d'API API-Car | Google Cloud Secret Manager |
| Partner ID | Chaîne | Identifiant partenaire | Google Cloud Secret Manager |
| Authentication Token | Chaîne | Token d'authentification | Google Cloud Secret Manager |

#### Variables d'environnement associées
```
APICAR_API_KEY=xxxxxxxxxxxxxxxx
APICAR_PARTNER_ID=12345
APICAR_AUTH_TOKEN=xxxxxxxxxxxxxxxx
```

#### Plan de secours : Solutions de scraping

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| ScrapingBee API Key | Chaîne | Clé API pour le service de scraping | Google Cloud Secret Manager |
| Proxies | Liste d'URLs | Liste de proxies pour la rotation | Google Cloud Secret Manager |

#### Documentation officielle
- [Parts Alliance API Documentation](https://api.partsalliance.com/docs)
- [Lobstr.io Documentation](https://developers.lobstr.io/docs)
- [API2Cart Documentation](https://docs.api2cart.com)
- [API-Car Documentation](https://api-car.com/documentation)
- [ScrapingBee Documentation](https://www.scrapingbee.com/documentation)

## 4. CI/CD et Gestion de Code Source

### Service Principal : GitHub & GitHub Actions

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| GitHub Personal Access Token (PAT) | Chaîne | Token pour l'accès aux repos et Actions | Google Cloud Secret Manager |
| Deploy Keys | Paire de clés SSH | Clés pour l'accès déployement automatisé | Google Cloud Secret Manager |
| GitHub Actions Secrets | Valeurs dans l'interface | Variables utilisées dans les workflows | GitHub Actions Secrets |

#### Workflows GitHub Actions
```yaml
# Exemple de configuration de secrets dans un workflow GitHub Actions
name: NovaEvo CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and Test
        env:
          GCP_SA_KEY: ${{ secrets.GCP_SA_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          STRIPE_API_KEY: ${{ secrets.STRIPE_API_KEY }}
        run: |
          # Steps to build, test and deploy
```

#### Plan de secours : GitLab CI/CD

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| GitLab Access Token | Chaîne | Token pour l'accès aux repos et CI/CD | Google Cloud Secret Manager |
| GitLab CI Variables | Valeurs dans l'interface | Variables utilisées dans les pipelines | GitLab CI Variables |
| Deploy Keys | Paire de clés SSH | Clés pour l'accès déployement automatisé | Google Cloud Secret Manager |

#### Documentation officielle
- [GitHub Actions - Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitLab CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/)

## 5. Monitoring et Logging

### Service Principal : Prometheus & Grafana

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Prometheus Basic Auth | Username:Password | Authentification à l'interface | Google Cloud Secret Manager |
| Grafana Admin | Username:Password | Identifiants administrateur | Google Cloud Secret Manager |
| API Keys | Chaîne | Clés pour l'accès API | Google Cloud Secret Manager |
| Alertmanager Credentials | Token | Accès aux alertes | Google Cloud Secret Manager |

#### Configuration
```yaml
# Exemple de configuration d'authentification Prometheus
basic_auth_users:
  admin: $2y$10$...  # bcrypt hash du mot de passe

# Exemple de configuration des alertes
alertmanager:
  config:
    receivers:
      - name: 'ops-team'
        slack_configs:
          - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
            channel: '#alerts'
```

### Service Principal : Google Cloud Logging

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Service Account | Fichier JSON | Même compte service GCP | Google Cloud Secret Manager |
| Log Sink | Chaîne | Identifiant du sink de logs | Variables d'environnement |

#### Variables d'environnement associées
```
LOG_LEVEL=INFO
GCLOUD_LOG_SINK=novaevo-logs
```

#### Plan de secours : Datadog

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Datadog API Key | Chaîne | Clé d'API principale | Google Cloud Secret Manager |
| Datadog App Key | Chaîne | Clé d'application | Google Cloud Secret Manager |
| Datadog Site | Chaîne (ex: `datadoghq.eu`) | Région Datadog | Variables d'environnement |

#### Documentation officielle
- [Prometheus Authentication](https://prometheus.io/docs/guides/basic-auth/)
- [Grafana Authentication](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/configure-authentication/)
- [Google Cloud Logging](https://cloud.google.com/logging/docs)
- [Datadog API Keys](https://docs.datadoghq.com/account_management/api-app-keys/)

## 6. Messagerie et Notifications

### Service Principal : SendGrid / Mailgun

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| API Key | Chaîne | Clé d'API SendGrid/Mailgun | Google Cloud Secret Manager |
| Domain | Chaîne | Domaine configuré | Variables d'environnement |
| From Email | Email | Adresse d'expédition | Variables d'environnement |

#### Variables d'environnement associées
```
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxx
EMAIL_DOMAIN=mail.novaevo.example.com
EMAIL_FROM=notifications@novaevo.example.com
```

### Service Principal : Twilio (SMS/Push)

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Account SID | Chaîne | Identifiant du compte Twilio | Google Cloud Secret Manager |
| Auth Token | Chaîne | Token d'authentification | Google Cloud Secret Manager |
| Phone Number | Chaîne (ex: `+33612345678`) | Numéro d'expédition | Variables d'environnement |

#### Variables d'environnement associées
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+33612345678
```

#### Plan de secours : Mailjet pour email, Vonage (Nexmo) pour SMS

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Mailjet API Key | Chaîne | Clé d'API Mailjet | Google Cloud Secret Manager |
| Mailjet Secret Key | Chaîne | Clé secrète | Google Cloud Secret Manager |
| Vonage API Key | Chaîne | Clé d'API Vonage | Google Cloud Secret Manager |
| Vonage API Secret | Chaîne | Secret API | Google Cloud Secret Manager |

#### Documentation officielle
- [SendGrid API Keys](https://docs.sendgrid.com/ui/account-and-settings/api-keys)
- [Mailgun API Documentation](https://documentation.mailgun.com/en/latest/api-intro.html)
- [Twilio APIs](https://www.twilio.com/docs/usage/api)
- [Mailjet API Documentation](https://dev.mailjet.com/)
- [Vonage API Documentation](https://developer.vonage.com/en/messaging/sms/overview)

## 7. Paiement et Monétisation

### Service Principal : Stripe

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| API Key | Chaîne (`sk_live_...` ou `sk_test_...`) | Clé secrète Stripe | Google Cloud Secret Manager |
| Publishable Key | Chaîne (`pk_live_...` ou `pk_test_...`) | Clé publique pour le frontend | Variables d'environnement |
| Webhook Secret | Chaîne (`whsec_...`) | Secret pour vérifier les webhooks | Google Cloud Secret Manager |
| Price IDs | Chaînes | IDs des plans d'abonnement | Variables d'environnement |

#### Variables d'environnement associées
```
STRIPE_API_KEY=sk_live_xxxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
STRIPE_PRICE_ID_BASIC=price_basic
STRIPE_PRICE_ID_PREMIUM=price_premium
```

#### Plan de secours : Braintree/PayPal

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Merchant ID | Chaîne | Identifiant du marchand | Google Cloud Secret Manager |
| Public Key | Chaîne | Clé publique | Variables d'environnement |
| Private Key | Chaîne | Clé privée | Google Cloud Secret Manager |
| Webhook Secret | Chaîne | Secret pour vérifier les webhooks | Google Cloud Secret Manager |

#### Documentation officielle
- [Stripe API Keys](https://stripe.com/docs/keys)
- [Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Braintree Documentation](https://developer.paypal.com/braintree/docs)

## 8. Authentification et Gestion des Utilisateurs

### Service Principal : Firebase Authentication

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Firebase Config | Objet JSON | Configuration pour intégration côté client | Variables d'environnement/Fichier |
| Service Account | Fichier JSON | Compte de service pour accès admin | Google Cloud Secret Manager |
| API Key | Chaîne | Clé API Firebase | Variables d'environnement |
| Project ID | Chaîne | ID du projet Firebase | Variables d'environnement |

#### Configuration
```javascript
// Exemple de configuration Firebase côté client
const firebaseConfig = {
  apiKey: "AIzaSyC-xxxxxxxxxxxxxxxxxxxxxx",
  authDomain: "novaevo-xxx.firebaseapp.com",
  projectId: "novaevo-xxx",
  storageBucket: "novaevo-xxx.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef123456",
  measurementId: "G-XXXXXXXX"
};
```

#### Plan de secours : Auth0

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Domain | Chaîne (ex: `novaevo.eu.auth0.com`) | Domaine Auth0 | Variables d'environnement |
| Client ID | Chaîne | ID Client Auth0 | Variables d'environnement |
| Client Secret | Chaîne | Secret client | Google Cloud Secret Manager |
| API Identifier | Chaîne | Identifiant API | Variables d'environnement |

#### Documentation officielle
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Auth0 Documentation](https://auth0.com/docs)

## 9. Analytics et Feedback

### Service Principal : Google Analytics 4

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Measurement ID | Chaîne (ex: `G-XXXXXXXXXX`) | ID de mesure GA4 | Variables d'environnement |
| API Secret | Chaîne | Secret API pour serveur | Google Cloud Secret Manager |
| Stream ID | Chaîne | ID du flux de données | Variables d'environnement |

#### Variables d'environnement associées
```
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
GOOGLE_ANALYTICS_API_SECRET=xxxxxxxxxxxxxxxx
GOOGLE_ANALYTICS_STREAM_ID=1234567890
```

### Service Complémentaire : Mixpanel

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Project Token | Chaîne | Token du projet | Variables d'environnement |
| API Secret | Chaîne | Secret pour les API serveur | Google Cloud Secret Manager |

#### Variables d'environnement associées
```
MIXPANEL_TOKEN=xxxxxxxxxxxxxxxx
MIXPANEL_API_SECRET=xxxxxxxxxxxxxxxx
```

### Service pour Feedback : Hotjar/Zendesk

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Hotjar Site ID | Nombre | ID du site Hotjar | Variables d'environnement |
| Zendesk API Token | Chaîne | Token API Zendesk | Google Cloud Secret Manager |
| Zendesk Email | Email | Email associé au token | Variables d'environnement |
| Zendesk Subdomain | Chaîne | Sous-domaine Zendesk | Variables d'environnement |

#### Plan de secours : Amplitude/Plausible Analytics

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Amplitude API Key | Chaîne | Clé API Amplitude | Google Cloud Secret Manager |
| Plausible Site ID | Chaîne | ID du site Plausible | Variables d'environnement |
| Plausible API Key | Chaîne | Clé API pour les statistiques | Google Cloud Secret Manager |

#### Documentation officielle
- [Google Analytics 4 Setup](https://developers.google.com/analytics/devguides/collection/ga4)
- [Mixpanel Implementation](https://developer.mixpanel.com/docs)
- [Hotjar Documentation](https://help.hotjar.com/hc/en-us/categories/360003405933)
- [Zendesk API](https://developer.zendesk.com/api-reference/)

## 10. Gestion des Secrets

### Service Principal : Google Cloud Secret Manager

#### Credentials nécessaires
| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Service Account | Fichier JSON | Même compte service GCP | Google Cloud Secret Manager |
| Project ID | Chaîne | ID du projet GCP | Variables d'environnement |

#### Variables d'environnement associées
```
GCP_PROJECT_ID=novaevo-production
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google-credentials.json
```

#### Plan de secours : HashiCorp Vault

| Credential | Format | Description | Stockage recommandé |
|------------|--------|-------------|---------------------|
| Vault Token | Chaîne | Token d'accès Vault | Stockage sécurisé local pour développeurs |
| Vault Address | URL | Adresse du serveur Vault | Variables d'environnement |
| Vault Role ID | Chaîne | ID de rôle pour AppRole | Google Cloud Secret Manager |
| Vault Secret ID | Chaîne | Secret ID pour AppRole | Google Cloud Secret Manager |

#### Documentation officielle
- [Google Cloud Secret Manager](https://cloud.google.com/secret-manager/docs)
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs)

---

## Bonnes Pratiques pour la Gestion des Credentials

1. **Rotation régulière** : Tous les tokens, clés et secrets doivent être changés selon un calendrier régulier
   - Clés critiques : rotation tous les 30 jours
   - Clés standard : rotation tous les 90 jours
   - Mots de passe : rotation tous les 60 jours

2. **Principe du moindre privilège** : Chaque credential doit avoir le minimum de permissions nécessaires
   - Création de comptes de service dédiés par fonctionnalité
   - Limitation des scopes d'accès pour les API externes
   - Séparation des environnements (développement, test, production)

3. **Documentation et inventaire** : Maintenir un registre actualisé de tous les credentials
   - Propriétaire responsable pour chaque credential
   - Date de dernière rotation
   - Date d'expiration (si applicable)
   - Niveau de criticité

4. **Procédure d'urgence** : Processus documenté pour la révocation et le remplacement rapide
   - Liste des points de contact pour chaque fournisseur de service
   - Étapes détaillées pour la révocation d'urgence
   - Procédure de basculement vers les services de secours

## Procédure de Mise à jour des Credentials

1. Générer les nouveaux credentials
2. Mettre à jour les secrets dans Google Cloud Secret Manager
3. Déployer les changements dans les variables d'environnement selon le pipeline CI/CD
4. Vérifier le bon fonctionnement avec les nouveaux credentials
5. Révoquer les anciens credentials

---

**Dernière mise à jour** : 10 avril 2025  
**Contact** : admin@novaevo.example.com  
**Responsable du document** : Équipe Sécurité NovaEvo