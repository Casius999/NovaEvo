# Pipeline d'Intégration Continue et Déploiement Continu (CI/CD)

## Introduction

Cette documentation détaille l'architecture, les processus et les outils du pipeline d'intégration continue et de déploiement continu (CI/CD) mis en place pour le projet NovaEvo. Ce pipeline garantit une livraison rapide, fiable et reproductible de toutes les fonctionnalités, tout en maintenant un niveau élevé de qualité de code et de documentation.

## 1. Architecture du Pipeline CI/CD

### 1.1 Vue d'Ensemble

Le pipeline CI/CD de NovaEvo suit une approche moderne et automatisée, assurant que chaque modification de code passe par une série d'étapes rigoureuses avant d'atteindre l'environnement de production.

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                            PIPELINE CI/CD NOVAEVO                             │
│                                                                               │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │  CODE   │───▶│  BUILD  │───▶│  TEST   │───▶│ STAGING │───▶│   PROD  │     │
│  │ COMMIT  │    │         │    │         │    │ DEPLOY  │    │ DEPLOY  │     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│       │                             │                            ▲            │
│       │                             │                            │            │
│       ▼                             ▼                            │            │
│  ┌─────────┐                   ┌─────────┐                  ┌─────────┐      │
│  │  CODE   │                   │  ALERT  │                  │ MANUAL  │      │
│  │ REVIEW  │                   │ SYSTEM  │                  │ APPROVAL│      │
│  └─────────┘                   └─────────┘                  └─────────┘      │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Étapes du Pipeline

#### 1.2.1 Phase de Développement
- **Commit & Push**: Le développeur effectue ses modifications et les pousse sur une branche de fonctionnalité.
- **Code Review**: Pull Request avec revue de code obligatoire par un pair.
- **Analyse Statique**: Vérification automatique du style de code, linting et identification de vulnérabilités potentielles.

#### 1.2.2 Phase de Build
- **Compilation**: Compilation du code et génération des artefacts.
- **Construction des Conteneurs**: Build des images Docker pour chaque composant microservice.
- **Scanning de Sécurité**: Analyse de sécurité des dépendances et des images conteneurisées.

#### 1.2.3 Phase de Test
- **Tests Unitaires**: Vérification du comportement individuel des composants.
- **Tests d'Intégration**: Validation des interactions entre composants.
- **Tests Fonctionnels**: Vérification end-to-end des fonctionnalités métier.
- **Tests de Performance**: Évaluation des performances sous charge.
- **Tests de Sécurité**: Vérification des vulnérabilités et conformité.

#### 1.2.4 Phase de Déploiement Staging
- **Déploiement Automatique**: Déploiement sur l'environnement de staging après succès des tests.
- **Tests de Validation**: Exécution de tests de smoke et de validation dans l'environnement déployé.
- **Tests Utilisateur Automatisés**: Simulation de parcours utilisateur réels.

#### 1.2.5 Phase de Déploiement Production
- **Approbation Manuelle**: Validation par les responsables désignés.
- **Déploiement Graduel**: Stratégie de déploiement blue/green ou canary.
- **Vérification Post-Déploiement**: Tests automatisés post-déploiement et monitoring renforcé.

### 1.3 Environnements

#### 1.3.1 Environnement de Développement
- **But**: Développement et tests locaux
- **Déploiement**: Manuel par les développeurs
- **Infrastructure**: Locale ou conteneurisée

#### 1.3.2 Environnement d'Intégration
- **But**: Vérification continue de l'intégration
- **Déploiement**: Automatique à chaque push
- **Infrastructure**: Google Cloud Platform (projet `novaevo-integration`)

#### 1.3.3 Environnement de Staging
- **But**: Validation pré-production
- **Déploiement**: Automatique après tests réussis
- **Infrastructure**: Google Cloud Platform (projet `novaevo-staging`)

#### 1.3.4 Environnement de Production
- **But**: Application en production
- **Déploiement**: Automatique avec approbation
- **Infrastructure**: Google Cloud Platform (projet `novaevo-production`)

## 2. Outils et Technologies

### 2.1 Outils d'Orchestration CI/CD

#### 2.1.1 GitHub Actions
GitHub Actions est l'outil principal d'orchestration CI/CD pour NovaEvo, choisi pour sa parfaite intégration avec le dépôt GitHub et sa flexibilité.

**Configuration:**
- Workflows définis dans `.github/workflows/`
- Intégration avec Google Cloud via GitHub Actions for GCP
- Gestion des secrets via GitHub Secrets

**Workflows Principaux:**
- `ci.yml`: Intégration continue (build + test)
- `staging-deploy.yml`: Déploiement sur staging
- `production-deploy.yml`: Déploiement en production
- `docs-update.yml`: Mise à jour automatique de la documentation

#### 2.1.2 Outils Complémentaires
- **Terraform**: Infrastructure as Code pour provisionner et gérer GCP
- **Pulumi**: Pour les ressources cloud complexes et les configurations avancées
- **ArgoCD**: Déploiement GitOps pour Kubernetes
- **Tekton**: Pipelines Kubernetes natifs pour certains workloads

### 2.2 Outils de Test et Qualité Code

#### 2.2.1 Tests et Validation
- **Jest**: Framework de test JavaScript pour les tests unitaires frontend
- **PyTest**: Framework de test Python pour les tests unitaires backend
- **Cypress**: Tests end-to-end et fonctionnels
- **JMeter**: Tests de charge et performance
- **OWASP ZAP**: Tests de sécurité automatisés

#### 2.2.2 Analyse Statique et Linting
- **ESLint/TSLint**: Linting JavaScript/TypeScript
- **Pylint/Flake8**: Linting Python
- **SonarQube**: Analyse qualité code et dette technique
- **Snyk**: Scan de vulnérabilités des dépendances
- **Trivy**: Scan de vulnérabilités des conteneurs

### 2.3 Intégration Google Cloud Platform

NovaEvo utilise efficacement les ressources GCP existantes pour optimiser les coûts et les performances.

#### 2.3.1 Services GCP Utilisés
- **Google Kubernetes Engine (GKE)**: Orchestration des conteneurs
- **Cloud Build**: Construction et déploiement d'images
- **Container Registry**: Stockage sécurisé des images Docker
- **Cloud Functions**: Fonctions serverless pour l'automatisation
- **Cloud Run**: Services sans état à scaling automatique
- **Pub/Sub**: Messaging asynchrone entre services
- **Cloud Monitoring**: Supervision des performances

#### 2.3.2 Optimisation des Ressources GCP
- Utilisation d'instances préemptives pour les environnements non-critiques
- Scaling automatique basé sur la charge
- Provisionnement éphémère pour les tests et l'intégration
- Nettoyage automatique des ressources inutilisées

### 2.4 Outils de Documentation

La documentation est maintenue à jour via des processus automatisés:

- **Sphinx**: Génération de documentation technique
- **Swagger/OpenAPI**: Documentation automatique des API
- **JSDoc/PyDoc**: Documentation du code source
- **Docusaurus**: Site de documentation pour les utilisateurs
- **MkDocs**: Documentation technique interne

## 3. Gestion et Automatisation des Tests

### 3.1 Stratégie de Test Globale

NovaEvo suit une approche de test pyramidale, privilégiant un grand nombre de tests unitaires rapides, complétés par des tests d'intégration et fonctionnels ciblés.

```
┌───────────────────────────────────────────────────────────────────────┐
│                       PYRAMIDE DE TESTS NOVAEVO                       │
│                                                                       │
│                             ▲  Peu                                    │
│                            ╱│╲ mais                                   │
│                           ╱ │ ╲ critiques                            │
│                          ╱  │  ╲                                      │
│                         ╱E2E Tests╲                                  │
│                        ╱────┼────╲                                   │
│                       ╱     │     ╲                                  │
│                      ╱ Functional  ╲                                 │
│                     ╱      Tests     ╲                               │
│                    ╱────────┼─────────╲                              │
│                   ╱         │          ╲                             │
│                  ╱    Integration Tests  ╲                           │
│                 ╱──────────────┼──────────╲                          │
│                ╱               │           ╲                         │
│               ╱         Unit Tests          ╲                        │
│              ╱─────────────────┼─────────────╲   Nombreux           │
│             ╱                  │              ╲  et                  │
│            ╱                   │               ╲ rapides            │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### 3.2 Types de Tests et Implémentation

#### 3.2.1 Tests Unitaires
- **Couverture cible**: >80% du code
- **Frameworks**: Jest (JS/TS), PyTest (Python)
- **Exécution**: À chaque commit/PR
- **Responsabilité**: Développeurs

**Exemple de configuration Jest:**
```json
{
  "jest": {
    "preset": "ts-jest",
    "testEnvironment": "node",
    "collectCoverage": true,
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

#### 3.2.2 Tests d'Intégration
- **Couverture cible**: >70% des flux critiques
- **Frameworks**: Supertest (API), TestContainers
- **Exécution**: À chaque PR et nightly
- **Responsabilité**: Développeurs + QA

**Exemple de GitHub Actions pour tests d'intégration:**
```yaml
integration-tests:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:13
      env:
        POSTGRES_PASSWORD: postgres
      ports:
        - 5432:5432
  steps:
    - uses: actions/checkout@v3
    - name: Run Integration Tests
      run: npm run test:integration
```

#### 3.2.3 Tests Fonctionnels
- **Couverture cible**: 100% des user stories
- **Frameworks**: Cypress, Puppeteer
- **Exécution**: À chaque déploiement sur staging
- **Responsabilité**: QA Engineers

**Exemple de scénario Cypress:**
```javascript
describe('OBD-II Diagnostic Flow', () => {
  it('should complete a full vehicle diagnostic', () => {
    cy.login('test-user');
    cy.visit('/dashboard');
    cy.contains('New Diagnostic').click();
    cy.get('#vehicle-selector').select('BMW X5');
    cy.contains('Connect OBD-II').click();
    cy.get('.connection-status', { timeout: 10000 }).should('contain', 'Connected');
    cy.contains('Start Diagnostic').click();
    cy.get('.diagnostic-result', { timeout: 30000 }).should('be.visible');
    cy.get('.diagnostic-report').should('contain', 'Engine Status');
  });
});
```

#### 3.2.4 Tests de Performance
- **Métrique cible**: Temps de réponse <200ms au P95
- **Outils**: JMeter, k6, Lighthouse
- **Exécution**: Hebdomadaire et avant production
- **Responsabilité**: SRE Team

**Exemple de script k6:**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },  // Ramp-up
    { duration: '3m', target: 50 },  // Steady load
    { duration: '1m', target: 100 }, // Spike
    { duration: '2m', target: 100 }, // Steady high load
    { duration: '1m', target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests must complete within 200ms
  },
};

export default function() {
  const res = http.get('https://staging.novaevo.com/api/health');
  check(res, { 'status was 200': (r) => r.status === 200 });
  sleep(1);
}
```

#### 3.2.5 Tests de Sécurité
- **Couverture cible**: 100% des API exposées
- **Outils**: OWASP ZAP, Snyk, Trivy
- **Exécution**: À chaque PR et nightly
- **Responsabilité**: Security Team

**Exemple de workflow de scan OWASP ZAP:**
```yaml
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: ZAP Scan
      uses: zaproxy/action-baseline@v0.7.0
      with:
        target: 'https://staging.novaevo.com'
        rules_file_name: '.zap/rules.tsv'
        cmd_options: '-a'
```

### 3.3 Gestion des Tests de Bout en Bout

#### 3.3.1 Tests E2E Critiques
NovaEvo identifie les parcours critiques qui sont testés de bout en bout:

1. **Parcours Diagnostic Complet**:
   - Connexion utilisateur
   - Association véhicule
   - Connexion OBD-II
   - Exécution diagnostic
   - Génération rapport
   - Recommandations pièces

2. **Parcours Recherche et Commande**:
   - Recherche pièce spécifique
   - Filtrage et comparaison
   - Ajout au panier
   - Process d'affiliation
   - Finalisation commande

3. **Parcours Professionnel**:
   - Vérification KBIS
   - Configuration profil
   - Réception demande RDV
   - Planification intervention
   - Facturation et suivi

#### 3.3.2 Environnements de Test E2E
Les tests E2E sont exécutés dans des environnements aussi proches que possible de la production:

- **Staging E2E**: Réplique exacte de production
- **Data Synthétique**: Données de test représentatives
- **Services Virtualisés**: Mockup des services externes
- **Monitoring Identique**: Même stack d'observabilité

### 3.4 Gestion des Alertes et Feedback

#### 3.4.1 Alertes en Cas d'Échec

Le pipeline envoie des alertes automatiques en cas d'échec de test ou de build:

- **Alertes Slack**: Notification dans les canaux dédiés
- **Alertes Email**: Pour les parties prenantes concernées
- **Dashboard CI/CD**: Visualisation en temps réel
- **Intégration JIRA**: Création automatique de tickets

**Niveaux de Sévérité des Alertes:**
1. **INFO**: Tests mineurs échoués
2. **WARNING**: Tests d'intégration échoués
3. **ERROR**: Tests critiques échoués
4. **CRITICAL**: Échec en production

#### 3.4.2 Boucle de Rétroaction

NovaEvo implémente une boucle de rétroaction pour améliorer continuellement le processus de test:

```
┌──────────────┐
│  Exécution   │
│  des Tests   │
└───────┬──────┘
        │
        ▼
┌──────────────┐     ┌──────────────┐
│  Analyse     │────▶│  Création    │
│  Résultats   │     │  Tickets     │
└───────┬──────┘     └──────┬───────┘
        │                   │
        ▼                   ▼
┌──────────────┐     ┌──────────────┐
│  Ajustement  │◀────┤  Résolution  │
│  Stratégie   │     │  Problèmes   │
└───────┬──────┘     └──────────────┘
        │
        ▼
┌──────────────┐
│  Amélioration│
│  Tests       │
└──────────────┘
```

**Métriques de Feedback:**
- Taux d'échec des tests par module
- Durée d'exécution des tests
- Couverture de code
- Taux de faux positifs/négatifs
- Efficacité de détection des bugs

## 4. Workflow de Branching et Fusion

### 4.1 Stratégie de Branching

NovaEvo adopte une stratégie de branching inspirée de Git Flow mais simplifiée:

```
┌───────────────────────────────────────────────────────────────────────┐
│                    STRATÉGIE DE BRANCHING NOVAEVO                     │
│                                                                       │
│ main ─────────o─────────o─────────o─────────o─────────o─────────o─── │
│               │         │         │         │         │         │     │
│ staging ──────┼─────────o─────────o─────────o─────────o─────────o─── │
│               │         ↑         ↑         ↑         ↑         ↑     │
│ develop ──────o─────────o─────────o─────────o─────────o─────────o─── │
│               ↑         ↑         ↑         ↑         ↑         ↑     │
│ features      │         │         │         │         │         │     │
│  feature/1 ───o─────x───│         │         │         │         │     │
│  feature/2 ───────────o─x         │         │         │         │     │
│  feature/3 ───────────────────o───x─────────│         │         │     │
│                                             │         │         │     │
│ bugfix                                      │         │         │     │
│  bugfix/1 ───────────────────────────────o──x         │         │     │
│  bugfix/2 ───────────────────────────────────────o────x         │     │
│                                                              │     │
│ hotfix                                                            │     │
│  hotfix/1 ─────────────────────────────────────────────────o─────x     │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

#### 4.1.1 Branches Principales
- **main**: Code en production
- **staging**: Code validé prêt pour production
- **develop**: Branche d'intégration pour le développement

#### 4.1.2 Branches de Support
- **feature/xxx**: Nouvelles fonctionnalités (depuis develop)
- **bugfix/xxx**: Corrections de bugs non-critiques (depuis develop)
- **hotfix/xxx**: Corrections urgentes (depuis main)

### 4.2 Process de Pull Request

#### 4.2.1 Création de Pull Request
- Titre clair suivant convention: `[TYPE] Description courte`
- Description détaillée avec lien vers ticket JIRA
- Assignation des reviewers (minimum 2)
- Lien vers documentation impactée

**Template PR:**
```markdown
## Description
[Description claire et concise des changements]

## JIRA Ticket
[Lien vers le ticket JIRA]

## Type de changement
- [ ] Feature
- [ ] Bug fix
- [ ] Refactoring
- [ ] Documentation
- [ ] Tests

## Impact
- [ ] Breaking change
- [ ] Backward compatible

## Checklist
- [ ] Tests ajoutés/mis à jour
- [ ] Documentation mise à jour
- [ ] Code conforme aux standards
- [ ] Build et tests CI/CD passent
```

#### 4.2.2 Critères de Validation PR
- Revue de code par minimum 2 personnes
- Tous les tests automatisés réussis
- Couverture de code maintenue ou améliorée
- Pas de dette technique ajoutée
- Documentation mise à jour

#### 4.2.3 Règles de Fusion Automatique
- Toutes les approbations requises obtenues
- Tous les checks CI/CD passés
- Compatibilité avec la branche cible vérifiée

### 4.3 Protection des Branches

#### 4.3.1 Règles pour Branches Protégées
- **main**: Fusion uniquement via PR approuvée depuis staging
- **staging**: Fusion uniquement via PR approuvée depuis develop
- **develop**: Fusion uniquement via PR approuvée

#### 4.3.2 Politique de Build Obligatoire
- Toutes les vérifications CI doivent passer
- Code review obligatoire pour toute PR
- Scan de sécurité et qualité de code obligatoire

**Configuration GitHub:**
```json
{
  "protection": {
    "required_status_checks": {
      "strict": true,
      "contexts": [
        "ci/build",
        "ci/test",
        "security/scan",
        "quality/sonarqube"
      ]
    },
    "required_pull_request_reviews": {
      "required_approving_review_count": 2
    },
    "enforce_admins": true
  }
}
```

## 5. Maintenance de la Documentation

### 5.1 Documentation Automatisée du Code

NovaEvo maintient une documentation de code à jour grâce à des processus automatisés:

#### 5.1.1 Documentation in-code
- JSDoc pour JavaScript/TypeScript
- Docstrings pour Python
- Documentation API avec OpenAPI/Swagger

**Exemple JSDoc:**
```javascript
/**
 * Analyse les données OBD-II pour déterminer l'état du véhicule
 * @param {Object} obdData - Données brutes du capteur OBD-II
 * @param {string} vehicleType - Type de véhicule (ex: "BMW X5")
 * @returns {DiagnosticReport} Rapport de diagnostic complet
 * @throws {ConnectionError} Si la connexion OBD-II est perdue
 */
function analyzeVehicleData(obdData, vehicleType) {
  // Implementation
}
```

#### 5.1.2 Génération automatique
- Exécution à chaque commit/PR
- Déploiement sur site de documentation
- Vérification de couverture de documentation

**Workflow Documentation:**
```yaml
documentation:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Generate API Documentation
      run: npm run docs:generate
    - name: Check Documentation Coverage
      run: npm run docs:coverage
    - name: Deploy Documentation
      if: github.ref == 'refs/heads/main'
      run: npm run docs:deploy
```

### 5.2 Maintenance de la Documentation Technique

#### 5.2.1 Documentation Markdown
Les fichiers Markdown du dépôt sont considérés comme source de vérité:

- Structure organisée dans `/docs`
- Mise à jour obligatoire avec chaque PR impactante
- Vérification automatique des liens et références

#### 5.2.2 Automatisation de la Documentation
- Extraction de schémas de base de données
- Génération de diagrammes de flux
- Création automatique de changelog
- Mise à jour des métriques et KPIs

**Exemple d'automatisation:**
```yaml
update-architecture-docs:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Extract DB Schema
      run: ./scripts/extract-schema.sh > docs/database-schema.md
    - name: Generate API Docs
      run: ./scripts/generate-api-docs.sh
    - name: Update Diagrams
      run: ./scripts/update-diagrams.sh
    - name: Commit Updated Docs
      uses: stefanzweifel/git-auto-commit-action@v4
      with:
        commit_message: "docs: update technical documentation [skip ci]"
        file_pattern: docs/*.md
```

## 6. Exemples de Workflows CI/CD

### 6.1 Workflow d'Intégration Continue

```yaml
name: Continuous Integration

on:
  push:
    branches: [ develop, feature/**, bugfix/** ]
  pull_request:
    branches: [ develop, staging, main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      - name: Install dependencies
        run: npm ci
      - name: Run linting
        run: npm run lint

  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      - name: Install dependencies
        run: npm ci
      - name: Run unit tests
        run: npm test
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Snyk Security Scan
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      - name: SonarQube Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'
      - name: Install dependencies
        run: npm ci
      - name: Build
        run: npm run build
      - name: Archive build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build
          path: build/
```

### 6.2 Workflow de Déploiement Staging

```yaml
name: Deploy to Staging

on:
  push:
    branches: [ staging ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Google Cloud SDK
        uses: google-github-actions/setup-gcloud@main
        with:
          project_id: novaevo-staging
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          export_default_credentials: true
      
      - name: Build and Push Docker Image
        run: |
          gcloud builds submit --tag gcr.io/novaevo-staging/app:${{ github.sha }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy novaevo-app \
            --image gcr.io/novaevo-staging/app:${{ github.sha }} \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated
      
      - name: Run Smoke Tests
        run: |
          ./scripts/run-smoke-tests.sh https://novaevo-app-xyz.a.run.app
      
      - name: Run E2E Tests
        run: |
          npm run test:e2e -- --baseUrl=https://novaevo-app-xyz.a.run.app
      
      - name: Notify Slack on Success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          fields: repo,message,author,commit
          mention: 'here'
          if_mention: always
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 6.3 Workflow de Déploiement Production

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  prepare:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Create Deployment Approval
        id: create_deployment
        run: |
          echo "deployment_id=$(date +%s)" >> $GITHUB_OUTPUT
      - name: Wait for Approval
        uses: trstringer/manual-approval@v1
        with:
          secret: ${{ secrets.GITHUB_TOKEN }}
          approvers: tech-lead,product-manager
          minimum-approvals: 2
          timeout-minutes: 60
  
  deploy:
    needs: prepare
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Google Cloud SDK
        uses: google-github-actions/setup-gcloud@main
        with:
          project_id: novaevo-production
          service_account_key: ${{ secrets.GCP_PROD_SA_KEY }}
          export_default_credentials: true
      
      - name: Deploy to Production (Blue/Green)
        run: |
          # Create new deployment (green)
          gcloud run deploy novaevo-app-green \
            --image gcr.io/novaevo-staging/app:${{ github.sha }} \
            --platform managed \
            --region us-central1 \
            --no-traffic
          
          # Run validation
          ./scripts/validate-deployment.sh novaevo-app-green
          
          # Switch traffic
          gcloud run services update-traffic novaevo-app \
            --to-revisions=novaevo-app-green=100
      
      - name: Run Post-Deployment Tests
        run: |
          npm run test:prod-validation
      
      - name: Notify Stakeholders
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          fields: repo,message,author,commit
          mention: 'channel'
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_PROD_WEBHOOK_URL }}
```

## 7. Bonnes Pratiques et Recommandations

### 7.1 Pour les Développeurs

- Exécuter les tests unitaires localement avant chaque commit
- Implémenter les tests en même temps que le code
- Suivre les conventions de nommage pour branches et commits
- Maintenir la documentation à jour avec le code
- Créer des PRs ciblées et de taille raisonnable

### 7.2 Pour les DevOps et SRE

- Surveiller les métriques du pipeline CI/CD
- Optimiser régulièrement les temps de build
- Maintenir les images de base à jour
- Mettre en place des rollbacks automatisés
- Réaliser des audits de sécurité réguliers

### 7.3 Pour les QA et Testeurs

- Maintenir à jour les scénarios de test critiques
- Améliorer la couverture de test stratégiquement
- Analyser les patterns d'échec des tests
- Optimiser les tests de non-régression
- Collaborer avec les développeurs pour la testabilité

## Conclusion

Le pipeline CI/CD de NovaEvo constitue une fondation essentielle pour maintenir la qualité, la fiabilité et l'agilité du projet. En automatisant rigoureusement les processus de build, test et déploiement, l'équipe peut se concentrer sur la création de valeur métier tout en garantissant un niveau élevé de qualité et de sécurité.

Cette infrastructure évoluera avec le projet, s'adaptant aux nouvelles technologies et méthodes, tout en restant fidèle aux principes fondamentaux d'automatisation, de fiabilité et de transparence.

---

*Document créé le 10 avril 2025*