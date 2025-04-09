# Guide de Monitoring - Assistant Auto Ultime

Ce document détaille la configuration du monitoring, du logging et des systèmes d'analyse pour Assistant Auto Ultime.

## 1. Architecture de Monitoring

Le système de monitoring se compose de plusieurs couches complémentaires:

```
┌───────────────────┐      ┌───────────────────┐     ┌───────────────────┐
│  Monitoring Appli │      │  Monitoring Infra │     │  Analyse Métier   │
├───────────────────┤      ├───────────────────┤     ├───────────────────┤
│ - Erreurs (Sentry)│      │ - Serveurs        │     │ - Analytics       │
│ - Performance     │      │ - Base de données │     │ - Conversion      │
│ - Disponibilité   │      │ - Réseau          │     │ - Feedback        │
└────────┬──────────┘      └─────────┬─────────┘     └─────────┬─────────┘
         │                           │                          │
         └───────────────┬───────────┴──────────────┬──────────┘
                         │                          │
                 ┌───────┴──────────┐      ┌────────┴─────────┐
                 │  Alerting        │      │  Dashboards      │
                 └──────────────────┘      └──────────────────┘
```

## 2. Sentry: Monitoring des Erreurs

Sentry est notre principale solution pour le suivi des erreurs applicatives.

### 2.1. Configuration

Dans les variables d'environnement:
```
SENTRY_DSN=https://your-project-key@sentry.io/your-project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
ENVIRONMENT=production  # ou development, testing
```

### 2.2. Intégration Backend (Flask)

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=float(os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
    environment=os.getenv('ENVIRONMENT', 'development')
)
```

### 2.3. Intégration Frontend (React)

```javascript
// Dans index.js
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [new BrowserTracing()],
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
});
```

### 2.4. Configuration des Alertes Sentry

Sentry est configuré pour envoyer des alertes via:
- Email aux administrateurs système
- Intégration Slack dans le canal #alerts-prod
- Webhooks vers notre système PagerDuty pour les incidents critiques

## 3. Système de Logging

### 3.1. Architecture de Logging

Le système implémente une approche de logging à plusieurs niveaux:

1. **Logs applicatifs**: Générés par l'application
2. **Logs système**: Générés par les serveurs et l'infrastructure
3. **Logs d'accès**: Requêtes HTTP et opérations d'API

### 3.2. Configuration de Logging Backend

```python
import logging
from logging.handlers import RotatingFileHandler

# Configuration du logger
logger = logging.getLogger('assistant_auto')
logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))

# Handler pour le fichier avec rotation
file_handler = RotatingFileHandler(
    os.getenv('LOG_FILE', 'logs/auto_assistant.log'),
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Handler pour la console en développement
if os.getenv('ENVIRONMENT') != 'production':
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
```

### 3.3. Centralisation des Logs

En production, les logs sont centralisés avec ELK Stack (Elasticsearch, Logstash, Kibana):

1. **Logstash**: Collecte et transforme les logs
2. **Elasticsearch**: Stocke et indexe les données
3. **Kibana**: Interface de visualisation et analyse

Configuration Filebeat pour collecte automatique:
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /path/to/logs/*.log
  fields:
    application: assistant-auto-ultime
    environment: production
```

## 4. Monitoring Infrastructure

### 4.1. Prometheus & Grafana

Le monitoring infrastructure utilise Prometheus pour la collecte et Grafana pour la visualisation.

#### Métriques collectées:
- Utilisation CPU/Mémoire/Disque
- Performance base de données
- Trafic réseau et latence
- État des services

#### Configuration Prometheus (extrait):
```yaml
scrape_configs:
  - job_name: 'assistant-auto-backend'
    scrape_interval: 15s
    static_configs:
      - targets: ['backend:5000']
  - job_name: 'assistant-auto-frontend'
    scrape_interval: 15s
    static_configs:
      - targets: ['frontend:3000']
```

### 4.2. Alertmanager

Configuration des alertes infrastructure:
```yaml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 3h
  receiver: 'team-backend'
  routes:
  - match:
      service: frontend
    receiver: 'team-frontend'

receivers:
- name: 'team-backend'
  email_configs:
  - to: 'backend-team@example.com'
- name: 'team-frontend'
  email_configs:
  - to: 'frontend-team@example.com'
```

## 5. Analytics et Feedback

### 5.1. Google Analytics / Matomo

Configuration Analytics pour le tracking utilisateur:

```html
<!-- Configuration Google Analytics (extrait de index.html) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>

<!-- Ou Matomo (auto-hébergé) -->
<script>
  var _paq = window._paq = window._paq || [];
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="//analytics.your-domain.com/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '1']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  })();
</script>
```

### 5.2. Événements Personnalisés

Liste des événements personnalisés trackés:
- Recherche de pièces
- Connexion OBD-II
- Scan OCR
- Flash ECU
- Souscription abonnement
- Feedback soumis
- Clic sur affiliation

### 5.3. Système de Feedback

Le système de feedback est conçu pour:
1. Collecter les commentaires utilisateurs
2. Signaler des bugs
3. Recueillir des suggestions

Les retours sont:
- Stockés dans `data/feedback/` au format JSON
- Consultables via un tableau de bord admin
- Catégorisés automatiquement
- Convertis en tickets dans notre système de gestion de projet

## 6. Dashboards Opérationnels

### 6.1. Dashboard Technique

Dashboard Grafana principal avec:
- État des services (uptime)
- Performances système
- Latence API
- Taux d'erreurs
- Métriques base de données

### 6.2. Dashboard Métier

Dashboard métier incluant:
- Utilisateurs actifs
- Conversions
- Taux d'engagement
- Performance par fonctionnalité
- Revenu d'affiliation

## 7. Tests de Performance

### 7.1. Tests de Charge

Tests réguliers avec k6:
```javascript
import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  vus: 100,
  duration: '5m',
};

export default function () {
  http.get('https://app.assistant-auto-ultime.com/api/');
  sleep(1);
}
```

### 7.2. Tests de Web Vitals

Suivi des Core Web Vitals:
- LCP (Largest Contentful Paint)
- FID (First Input Delay)
- CLS (Cumulative Layout Shift)

Ces métriques sont collectées via:
- Google Analytics
- Chrome UX Report
- Outils synthétiques (Lighthouse CI)

## 8. Procédures d'Incident

### 8.1. Gestion des Incidents

Procédure standard:
1. **Détection**: Via alertes automatiques
2. **Qualification**: Évaluation de la gravité et de l'impact
3. **Communication**: Information des équipes concernées
4. **Résolution**: Correction du problème
5. **Post-mortem**: Analyse des causes et amélioration

### 8.2. Niveaux de Sévérité

| Niveau | Description | SLA | Notification |
|--------|-------------|-----|-------------|
| P1 | Service inaccessible | 15min | SMS + Appel |
| P2 | Fonctionnalité critique affectée | 1h | SMS |
| P3 | Problème non critique | 4h | Email |
| P4 | Anomalie mineure | 24h | Ticket |

## 9. Synthèse des Outils

| Outil | Usage | Environnement |
|-------|-------|---------------|
| Sentry | Suivi des erreurs | Dev + Prod |
| Prometheus | Métriques système | Prod |
| Grafana | Visualisation | Prod |
| ELK Stack | Centralisation des logs | Prod |
| Google Analytics | Analytics utilisateur | Prod |
| Matomo | Analytics auto-hébergé (opt.) | Prod |
| Datadog | Monitoring alternatif | Prod (optionnel) |

## 10. Recommandations d'Implémentation

1. **Déploiement graduel**:
   - Commencer par Sentry et logging de base
   - Ajouter Prometheus/Grafana
   - Implémenter ELK en dernier

2. **Bonnes pratiques**:
   - Utiliser des tags cohérents dans toute l'infrastructure
   - Automatiser la rotation des logs
   - Inclure des identifiants de trace dans tous les journaux
   - Implémenter un rate limiting pour les logs verbeux

3. **Documentation**:
   - Maintenir un catalogue des métriques
   - Documenter les alertes et procédures
   - Créer un runbook pour les incidents courants
