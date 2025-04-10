# Pipeline d'Intégration et Déploiement Continus (CI/CD)

## Introduction

Le pipeline CI/CD de NovaEvo constitue l'épine dorsale de notre processus de développement, garantissant qualité, fiabilité et vélocité dans la livraison de nouvelles fonctionnalités. Il automatise l'ensemble du cycle de vie du code, depuis la soumission d'une modification jusqu'à son déploiement en production, en passant par diverses phases de validation et de test.

Cette page détaille l'architecture, les composants et les processus de notre pipeline CI/CD, ainsi que les meilleures pratiques à suivre par l'équipe de développement.

## Principes Fondamentaux

Notre pipeline CI/CD repose sur cinq principes fondamentaux :

### 1. Automatisation Totale

Chaque étape du pipeline est entièrement automatisée, éliminant les interventions manuelles sources d'erreurs et garantissant reproductibilité et fiabilité.

### 2. Feedback Rapide

Le pipeline est optimisé pour fournir un retour d'information rapide aux développeurs, permettant d'identifier et de corriger les problèmes au plus tôt dans le cycle de développement.

### 3. Qualité Intégrée

La qualité est vérifiée à chaque étape du pipeline, avec des contrôles de plus en plus rigoureux à mesure que le code progresse vers la production.

### 4. Traçabilité Complète

Chaque exécution du pipeline est intégralement tracée, permettant d'auditer l'origine de chaque modification déployée en production.

### 5. Déploiement Sécurisé

Les déploiements suivent une approche progressive et contrôlée, avec possibilité de rollback automatique en cas de problème détecté.

## Architecture du Pipeline

Le pipeline CI/CD de NovaEvo est structuré en cinq phases principales, chacune comprenant plusieurs étapes :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PHASE DE DÉVELOPPEMENT                          │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌────────────┐ │
│  │ Commit        │──▶│ Revue de Code │──▶│ Merge Request │──▶│ Merge      │ │
│  │               │   │               │   │ Approval      │   │            │ │
│  └───────────────┘   └───────────────┘   └───────────────┘   └────────────┘ │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               PHASE DE BUILD                                │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌────────────┐ │
│  │ Compilation   │──▶│ Construction  │──▶│ Publication   │──▶│ Scan de    │ │
│  │ du Code       │   │ des Images    │   │ des Artefacts │   │ Sécurité   │ │
│  └───────────────┘   └───────────────┘   └───────────────┘   └────────────┘ │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE DE TEST                                  │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌────────────┐ │
│  │ Tests         │──▶│ Tests         │──▶│ Tests de      │──▶│ Tests de   │ │
│  │ Unitaires     │   │ d'Intégration │   │ Performance   │   │ Sécurité   │ │
│  └───────────────┘   └───────────────┘   └───────────────┘   └────────────┘ │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                             PHASE DE STAGING                                │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌────────────┐ │
│  │ Déploiement   │──▶│ Tests         │──▶│ Validation    │──▶│ Approbation│ │
│  │ Automatique   │   │ Fonctionnels  │   │ UAT           │   │ Release    │ │
│  └───────────────┘   └───────────────┘   └───────────────┘   └────────────┘ │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PHASE DE PRODUCTION                              │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌────────────┐ │
│  │ Déploiement   │──▶│ Validation    │──▶│ Monitoring    │──▶│ Rollback   │ │
│  │ Blue/Green    │   │ Post-Deploy   │   │ Continu       │   │ (si besoin)│ │
│  └───────────────┘   └───────────────┘   └───────────────┘   └────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Description Détaillée des Phases

### 1. Phase de Développement

#### Étapes et Responsabilités

| Étape | Description | Responsable | Outils |
|-------|-------------|-------------|--------|
| **Commit** | Soumission du code avec message descriptif | Développeur | Git, GitHub |
| **Revue de Code** | Examen du code par les pairs | Équipe dev | GitHub Pull Requests |
| **Merge Request Approval** | Validation finale des modifications | Tech Lead | GitHub PR Approval |
| **Merge** | Intégration du code dans la branche principale | Tech Lead | GitHub Merge |

#### Pratiques Recommandées

- **Commits Atomiques** : Privilégier de petits commits ciblés sur une seule fonctionnalité
- **Messages Explicites** : Utiliser un format standardisé (type: description détaillée)
- **Branches Éphémères** : Créer une branche par fonctionnalité ou correctif
- **Pull Requests Documentées** : Inclure contexte, solution et tests réalisés

### 2. Phase de Build

#### Étapes et Métriques

| Étape | Description | Métriques | Seuils |
|-------|-------------|-----------|--------|
| **Compilation** | Transformation du code source en artefacts exécutables | Temps de build, Erreurs | <2min, 0 erreur |
| **Construction Images** | Création des conteneurs Docker | Taille images, Vulnérabilités | <500MB, 0 critique |
| **Publication Artefacts** | Stockage des artefacts dans le registry | Temps de publication | <1min |
| **Scan de Sécurité** | Analyse des dépendances et vulnérabilités | Vulnérabilités détectées | 0 haute/critique |

#### Technologies Utilisées

- **Build Backend** : Maven/Gradle (Java), pip/poetry (Python)
- **Build Frontend** : Webpack, Babel, npm
- **Container Registry** : Google Container Registry (GCR)
- **Scanning** : Snyk, Trivy, OWASP Dependency Check

### 3. Phase de Test

Notre stratégie de test suit une approche pyramidale pour équilibrer couverture, vitesse et coût :

```
      ▲ Coût / Temps d'exécution
      │
      │              ┌───────────┐
      │              │   E2E     │  < 5% des tests
      │              └───────────┘
      │         ┌─────────────────────┐
      │         │     Intégration     │  < 30% des tests
      │         └─────────────────────┘
      │    ┌─────────────────────────────┐
      │    │           Unitaires         │  > 65% des tests
      │    └─────────────────────────────┘
      │
      └─────────────────────────────────────► Couverture / Confiance
```

#### Objectifs de Couverture

| Type de Test | Couverture Cible | Temps Max | Responsable |
|--------------|------------------|-----------|-------------|
| **Tests Unitaires** | >80% du code | 5 min | Développeurs |
| **Tests d'Intégration** | >70% des flux | 15 min | Développeurs + QA |
| **Tests Fonctionnels** | 100% des user stories | 30 min | QA |
| **Tests de Performance** | Temps réponse <200ms au P95 | 10 min | SRE |
| **Tests de Sécurité** | 100% des API exposées | 15 min | Équipe Sécurité |

#### Frameworks de Test Utilisés

- **Backend** : JUnit, pytest, Mockito
- **Frontend** : Jest, Testing Library, Cypress
- **API** : Postman, REST-assured
- **Performance** : JMeter, k6
- **Sécurité** : OWASP ZAP, Burp Suite

### 4. Phase de Staging

#### Environnement de Staging

Notre environnement de staging est une réplique exacte de la production en termes d'architecture, mais avec des ressources réduites :

- Même infrastructure cloud (GCP)
- Même topologie de services
- Même configuration réseau
- Données anonymisées issues de la production

#### Validation Utilisateur (UAT)

- Tests manuels par équipe QA sur scénarios critiques
- Tests exploratoires pour identifier bugs non détectés
- Validation des performances dans des conditions réelles
- Vérification des parcours utilisateurs complets

#### Critères d'Acceptation pour Déploiement

| Critère | Seuil | Responsable Validation |
|---------|-------|------------------------|
| Tests fonctionnels réussis | 100% | Lead QA |
| Temps de réponse médian | <100ms | SRE |
| Temps de réponse P95 | <200ms | SRE |
| Taux d'erreur | <0.1% | Lead Dev |
| Vulnérabilités sécurité | 0 critique/haute | RSSI |

### 5. Phase de Production

#### Stratégie de Déploiement Blue/Green

Nous utilisons une approche Blue/Green pour minimiser les interruptions de service :

```
           ┌───────────────┐                        ┌───────────────┐
  ┌───────▶│ Environnement │         ┌─────────────▶│ Environnement │
  │        │ Blue (actif)  │         │              │ Blue (inactif)│
  │        └───────────────┘         │              └───────────────┘
  │              ▲                   │                     ▲
  │              │                   │                     │
┌─┴─────────┐    │                ┌──┴────────┐           │
│           │    │                │           │           │
│  Traffic  │────┘                │  Traffic  │───────────┘
│Utilisateur│                     │Utilisateur│
│           │────┐                │           │───────────┐
│           │    │                │           │           │
└───────────┘    │                └───────────┘           │
                 │                                        │
                 ▼                                        ▼
          ┌───────────────┐                        ┌───────────────┐
          │ Environnement │                        │ Environnement │
          │ Green (inactif│◀──────────────────────▶│ Green (actif) │
          └───────────────┘                        └───────────────┘
               AVANT                                    APRÈS
```

#### Procédure de Déploiement

1. Déployer la nouvelle version dans l'environnement inactif (Green)
2. Exécuter les tests de smoke sur Green
3. Basculer un petit pourcentage du trafic vers Green (canary)
4. Surveiller les métriques clés pendant 15 minutes
5. Si tout est normal, basculer progressivement 100% du trafic
6. Conserver l'ancien environnement (Blue) pendant 24h pour rollback rapide si nécessaire

#### Monitoring Post-Déploiement

| Métrique | Surveillance | Seuil Alerte | Action si Dépassement |
|----------|--------------|--------------|------------------------|
| Taux d'erreur | 30 min | >0.5% | Rollback automatique |
| Latence P95 | 30 min | >300ms | Investigation, rollback si persistant |
| Utilisation CPU | 1h | >85% | Scale-up automatique |
| Erreurs log | 1h | >10 erreurs/min | Alerte équipe de garde |

## Outils et Technologies

Notre pipeline CI/CD s'appuie sur un ensemble d'outils modernes et performants :

### Plateforme CI/CD

- **Orchestration** : GitHub Actions
- **Registry** : Google Container Registry (GCR), GitHub Packages
- **Infrastructure** : Kubernetes sur Google Cloud Platform
- **Configuration** : Terraform, Helm Charts

### Monitoring et Observabilité

- **Métriques** : Prometheus, Grafana
- **Logs** : ELK Stack (Elasticsearch, Logstash, Kibana)
- **Traces** : Jaeger, OpenTelemetry
- **Alertes** : AlertManager, PagerDuty

### Sécurité

- **Scan de Code** : SonarQube, CodeQL
- **Scan de Dépendances** : Snyk, Dependabot
- **Scan de Conteneurs** : Trivy, Clair
- **Tests de Pénétration** : OWASP ZAP, Burp Suite

## Configuration du Pipeline GitHub Actions

Notre pipeline est défini dans les fichiers de configuration GitHub Actions situés dans le répertoire `.github/workflows/` du projet. Voici un exemple simplifié de notre workflow principal :

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  # Phase de Build
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          java-version: '17'
      - name: Build with Maven
        run: mvn -B package --file pom.xml
      - name: Build Docker image
        run: docker build -t novaevo:${{ github.sha }} .
      - name: Scan image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'novaevo:${{ github.sha }}'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

  # Phase de Test
  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up environment
        run: ./scripts/setup-test-env.sh
      - name: Run unit tests
        run: mvn test
      - name: Run integration tests
        run: mvn verify -P integration-tests
      - name: Run performance tests
        run: ./scripts/run-performance-tests.sh

  # Phase de Staging
  staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: novaevo-staging
          image: gcr.io/novaevo/app:${{ github.sha }}
          region: europe-west1
      - name: Run functional tests
        run: ./scripts/run-e2e-tests.sh
      - name: Notify team
        if: success()
        run: ./scripts/notify-team.sh "Deployment to staging successful"

  # Phase de Production
  production:
    needs: staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: 
      name: production
      url: https://app.novaevo.com
    steps:
      - name: Deploy to production (Blue/Green)
        uses: google-github-actions/deploy-cloudrun@v1
        with:
          service: novaevo-production
          image: gcr.io/novaevo/app:${{ github.sha }}
          region: europe-west1
          strategy: blue-green
      - name: Run smoke tests
        run: ./scripts/run-smoke-tests.sh
      - name: Monitor deployment
        run: ./scripts/monitor-deployment.sh
```

Pour les configurations complètes et détaillées, consultez notre [GitHub Repository](https://github.com/Casius999/NovaEvo).

## Stratégie de Branches et Environnements

NovaEvo utilise le modèle GitFlow adapté, avec une correspondance entre branches et environnements :

```
                   ┌───────────┐
                   │  hotfix/  │
                   └─────┬─────┘
                         │
┌───────────┐      ┌─────▼─────┐      ┌────────────┐      ┌────────────┐
│  feature/  │─────▶│ develop  │─────▶│  release/  │─────▶│   main     │
└───────────┘      └───────────┘      └────────────┘      └────────────┘
                         │                                       │
                   ┌─────▼─────┐                          ┌─────▼─────┐
                   │  DEV Env  │                          │  PROD Env  │
                   └───────────┘                          └───────────┘
```

### Types de Branches

| Branche | Préfixe | Déploiement | Protection |
|---------|---------|-------------|------------|
| Main | `main` | Production | ✅ (Approbation obligatoire) |
| Develop | `develop` | Staging | ✅ (CI requis) |
| Feature | `feature/` | Dev | ❌ |
| Release | `release/` | Pre-prod | ✅ (CI requis) |
| Hotfix | `hotfix/` | Test + Prod | ✅ (Approbation obligatoire) |

### Environnements

| Environnement | URL | Source | Usage |
|---------------|-----|--------|-------|
| Dev | dev.novaevo.com | Branch: develop | Développement continu |
| Staging | staging.novaevo.com | Branch: develop/release | Validation pré-production |
| Pre-Prod | preprod.novaevo.com | Branch: release | UAT final |
| Production | app.novaevo.com | Branch: main | Environnement client |

## Métriques de Performance du Pipeline

Nous suivons en permanence les performances de notre pipeline CI/CD pour identifier les opportunités d'optimisation :

| Métrique | Objectif | Actuel | Tendance |
|----------|----------|--------|----------|
| **Lead Time** (idée → production) | <2 semaines | 11 jours | ↓ Amélioration |
| **Cycle Time** (commit → production) | <2 jours | 1,5 jour | ↔ Stable |
| **Build Time** (durée totale pipeline) | <30 min | 28 min | ↓ Amélioration |
| **Success Rate** (% de builds réussis) | >95% | 97.3% | ↑ Amélioration |
| **MTTR** (temps moyen réparation) | <4h | 2h30 | ↓ Amélioration |
| **Déploiements/Semaine** | >3 | 5.2 | ↑ Amélioration |

## Responsabilités et Rôles

La gestion du pipeline CI/CD implique plusieurs rôles avec des responsabilités distinctes :

| Rôle | Responsabilités |
|------|-----------------|
| **Développeur** | • Créer des tests unitaires et d'intégration<br>• Résoudre les échecs de build<br>• Participer aux revues de code |
| **Tech Lead** | • Approbation des merge requests<br>• Surveillance des métriques du pipeline<br>• Optimisation du pipeline |
| **DevOps Engineer** | • Maintenance de l'infrastructure CI/CD<br>• Configuration des outils d'automatisation<br>• Gestion des environnements |
| **SRE** | • Surveillance des déploiements<br>• Gestion des incidents<br>• Optimisation des performances |
| **QA** | • Élaboration des tests automatisés<br>• Validation UAT<br>• Définition des critères d'acceptation |
| **Release Manager** | • Coordination des releases<br>• Validation finale des déploiements<br>• Communication avec les parties prenantes |

## Amélioration Continue du Pipeline

Le pipeline CI/CD est lui-même soumis à notre démarche d'amélioration continue :

### Processus d'Amélioration

1. **Collecte de Métriques** : Mesure systématique des KPIs du pipeline
2. **Identification des Goulots** : Analyse des étapes les plus lentes ou problématiques
3. **Expérimentation** : Test de nouvelles configurations ou outils
4. **Mise en Œuvre** : Déploiement des améliorations validées
5. **Évaluation** : Mesure de l'impact des changements

### Initiatives d'Amélioration Actuelles

- **Parallélisation Accrue** : Exécution simultanée de plus de tests
- **Caching Optimisé** : Réduction du temps de build via caching amélioré
- **Tests Incrémentaux** : Exécution des tests seulement pour les composants modifiés
- **Analyse Précoce** : Déplacement de certaines analyses en amont du pipeline

## Documentation Complémentaire

Pour approfondir certains aspects de notre pipeline CI/CD, consultez les ressources suivantes :

- [Stratégie de Test](Stratégie-de-Test) - Description détaillée de notre approche de test
- [Environnements](Environnements) - Documentation des environnements de déploiement
- [Déploiement Automatisé](Déploiement-Automatisé) - Procédures détaillées de déploiement
- [Monitoring et Alertes](Monitoring-et-Alertes) - Système de surveillance des déploiements

---

*Dernière mise à jour : 10 avril 2025*