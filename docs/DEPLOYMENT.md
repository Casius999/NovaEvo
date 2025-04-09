# Guide de déploiement - Assistant Auto Ultime

Ce document décrit les procédures de déploiement, le pipeline CI/CD, le monitoring et le système de feedback pour Assistant Auto Ultime.

## 1. Pipeline CI/CD

Le projet utilise GitHub Actions pour l'intégration continue (CI) et le déploiement continu (CD). Le pipeline est configuré dans le fichier `.github/workflows/ci-cd.yml`.

### 1.1. Structure du pipeline

Le pipeline CI/CD est composé de plusieurs jobs :

1. **Test** : Exécution des tests unitaires et d'intégration
   - Utilise pytest avec couverture de code
   - Génère un rapport de couverture
   - Vérifie que tous les tests passent

2. **Lint** : Vérification de la qualité du code
   - Analyse statique avec flake8
   - Vérification du formatage avec black
   - Vérification des imports avec isort

3. **Build-and-test-frontend** : Construction et test du frontend
   - Installation des dépendances npm
   - Exécution des tests frontend
   - Construction de l'application React

4. **Deploy** : Déploiement en production
   - Déclenché seulement sur la branche main
   - Construction et publication des images Docker
   - Déploiement sur DigitalOcean Kubernetes

### 1.2. Configuration du déploiement

Le déploiement est configuré pour utiliser DigitalOcean Kubernetes, mais peut être adapté à d'autres plateformes comme AWS, Azure ou GCP.

#### Secrets nécessaires

Pour que le pipeline fonctionne correctement, vous devez configurer les secrets suivants dans les paramètres GitHub du dépôt :

| Nom du secret | Description |
|---------------|-------------|
| `DIGITALOCEAN_ACCESS_TOKEN` | Token d'accès à l'API DigitalOcean |
| `DIGITALOCEAN_CLUSTER_NAME` | Nom du cluster Kubernetes cible |
| `DOCKER_USERNAME` | Nom d'utilisateur Docker Hub |
| `DOCKER_PASSWORD` | Mot de passe Docker Hub |

#### Configuration Kubernetes

Les fichiers de déploiement Kubernetes se trouvent dans le dossier `kubernetes/` :
- `backend-deployment.yaml` : Déploiement du backend
- `frontend-deployment.yaml` : Déploiement du frontend
- `service.yaml` : Services pour exposer les applications

## 2. Variables d'environnement

### 2.1. Variables requises

Le fichier `.env.example` contient toutes les variables d'environnement nécessaires. Copiez-le vers `.env` et configurez les valeurs appropriées :

```bash
cp .env.example .env
# Éditez le fichier .env avec les valeurs appropriées
```

### 2.2. Sécurisation des variables en production

En production, les variables sensibles ne doivent pas être stockées dans des fichiers :

1. **Kubernetes** : Utilisez des Secrets Kubernetes
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: assistant-auto-secrets
   type: Opaque
   data:
     GOOGLE_API_KEY: <BASE64_ENCODED_VALUE>
     OPENAI_API_KEY: <BASE64_ENCODED_VALUE>
     STRIPE_API_KEY: <BASE64_ENCODED_VALUE>
   ```

2. **DigitalOcean** : Utilisez les options d'environnement des App Platform
   - Configurez les variables d'environnement via l'interface web ou l'API

## 3. Configuration HTTPS

La sécurité en production est essentielle, particulièrement pour les applications manipulant des données sensibles.

### 3.1. Certificats SSL

1. **Let's Encrypt** (recommandé pour la production)
   - Utilisez cert-manager dans Kubernetes pour l'automatisation des certificats
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
   ```

2. **DigitalOcean** offre également des certificats SSL managés

### 3.2. Configuration Nginx

Un exemple de configuration Nginx est fourni dans le README principal. Pour le déploiement Kubernetes, utilisez plutôt un Ingress :

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: assistant-auto-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - app.assistant-auto-ultime.com
    secretName: assistant-auto-tls
  rules:
  - host: app.assistant-auto-ultime.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: assistant-auto-backend
            port:
              number: 5000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: assistant-auto-frontend
            port:
              number: 3000
```

## 4. Monitoring et Logging

### 4.1. Sentry

Le projet est configuré pour utiliser Sentry pour le suivi des erreurs et des exceptions.

#### Configuration

1. Créez un compte et un projet sur [Sentry](https://sentry.io)
2. Ajoutez votre DSN Sentry dans les variables d'environnement :
   ```
   SENTRY_DSN=https://your-dsn@sentry.io/project
   SENTRY_TRACES_SAMPLE_RATE=0.1
   ENVIRONMENT=production
   ```

#### Avantages

- Suivi des erreurs en temps réel
- Regroupement automatique des problèmes similaires
- Notification des nouvelles erreurs
- Analyse de performance (traces)

### 4.2. Système de Logging

L'application utilise le module `logging` de Python avec une configuration avancée :

- Logs stockés dans le dossier `logs/`
- Rotation des logs pour éviter une croissance illimitée
- Différents niveaux de log (INFO, WARNING, ERROR)

En production, il est recommandé d'utiliser un service de logs centralisé comme :
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog
- Papertrail

### 4.3. Analytics

Pour suivre l'utilisation de l'application, vous pouvez intégrer Google Analytics ou Matomo :

1. **Google Analytics** : Ajoutez votre ID de suivi dans le fichier frontend/public/index.html
2. **Matomo** : Solution auto-hébergée pour un contrôle total des données

## 5. Collecte de Feedback Utilisateur

Un système de feedback utilisateur a été implémenté pour recueillir les avis, signalements de bugs et suggestions d'amélioration.

### 5.1. Frontend

Le composant `Feedback` permet aux utilisateurs de soumettre leurs retours via l'interface. Il est accessible :
- Dans le footer de l'application
- Sur la page d'accueil
- Via la route dédiée `/feedback`

### 5.2. Backend

L'endpoint `/feedback` reçoit les données de feedback et :
1. Enregistre les retours dans le dossier `data/feedback/` au format JSON
2. Journalise les entrées pour suivi
3. Peut envoyer des notifications par email pour les retours critiques

### 5.3. Traitement des feedbacks

Pour exploiter au mieux ces retours :
1. Consultez régulièrement les fichiers générés dans `data/feedback/`
2. Catégorisez les retours (bug, suggestion, commentaire)
3. Intégrez les bugs et suggestions pertinentes dans les issues GitHub

## 6. Sauvegarde et Récupération

### 6.1. Stratégie de sauvegarde

En production, implémentez une stratégie de sauvegarde robuste :

1. **Base de données** : Sauvegardes automatiques quotidiennes
   ```bash
   # Exemple pour PostgreSQL
   pg_dump -U username dbname > backup_$(date +%Y%m%d).sql
   ```

2. **Données utilisateur** : Sauvegarde des dossiers `data/` et `uploads/`
   ```bash
   rsync -az data/ backups/data/
   ```

3. **Stockage externe** : Utilisez un service de stockage comme S3 ou DigitalOcean Spaces
   ```bash
   aws s3 sync backups/ s3://your-bucket/assistant-auto-backups/
   ```

### 6.2. Plan de récupération

Documentez clairement la procédure de restauration en cas d'incident :

1. Restauration de la base de données
2. Récupération des fichiers de données
3. Redéploiement des applications
4. Vérification post-restauration

## 7. Maintenance

### 7.1. Mises à jour de dépendances

Utilisez des outils comme dependabot ou renovate pour garder les dépendances à jour.

### 7.2. Cycle de mise à jour recommandé

- **Correctifs de sécurité** : Immédiatement
- **Mises à jour mineures** : Mensuellement
- **Mises à jour majeures** : Trimestriellement avec planification

## 8. Checklist de déploiement

Avant de déployer une nouvelle version en production, vérifiez :

- [ ] Tous les tests passent
- [ ] La couverture de code est satisfaisante
- [ ] Les variables d'environnement sont correctement configurées
- [ ] Les secrets sont sécurisés
- [ ] Les certificats SSL sont valides
- [ ] Le monitoring est opérationnel
- [ ] Un plan de rollback est prêt en cas de problème

## 9. Documentation supplémentaire

Pour plus d'informations sur des aspects spécifiques du déploiement, consultez :

- [Kubernetes.md](./Kubernetes.md) - Détails sur la configuration Kubernetes
- [Monitoring.md](./Monitoring.md) - Documentation avancée sur le monitoring
- [SSL_Security.md](./SSL_Security.md) - Guide complet sur la sécurisation HTTPS
