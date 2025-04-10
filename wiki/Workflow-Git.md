# Workflow Git

## Vue d'ensemble

Le workflow Git de NovaEvo est conçu pour garantir la qualité, la traçabilité et la stabilité du code, tout en permettant un développement collaboratif efficace. Ce document détaille notre approche, basée sur un Git Flow adapté aux spécificités de notre projet.

## Principes fondamentaux

Notre workflow Git repose sur les principes suivants :

- **Isolation** : Développement de chaque fonctionnalité dans sa propre branche
- **Qualité** : Validation systématique par revue de code et tests automatisés
- **Traçabilité** : Historique clair et structuré des modifications
- **Stabilité** : Protection des branches principales contre les modifications directes
- **Cohérence** : Standards et conventions uniformes pour tous les contributeurs

## Structure des branches

### Branches principales

Notre dépôt est organisé autour de plusieurs branches principales avec des rôles spécifiques :

| Branche | Description | Protection | Durée de vie |
|---------|-------------|------------|--------------|
| **`main`** | Code en production, toujours stable | Protégée, merge après validation | Permanente |
| **`develop`** | Branche d'intégration continue | Protégée, merge après tests | Permanente |
| **`release/*`** | Préparation des versions à déployer | Semi-protégée | Temporaire |
| **`feature/*`** | Développement de fonctionnalités | Non-protégée | Temporaire |
| **`bugfix/*`** | Corrections de bugs non-urgents | Non-protégée | Temporaire |
| **`hotfix/*`** | Corrections urgentes en production | Semi-protégée | Temporaire |

### Règles de nommage des branches

Pour maintenir l'organisation du dépôt, nous suivons ces conventions de nommage :

- **Feature branches** : `feature/[issue-id]-courte-description-en-kebab-case`
  - Exemple : `feature/NOV-123-integration-api-obd2`

- **Bugfix branches** : `bugfix/[issue-id]-courte-description`
  - Exemple : `bugfix/NOV-456-correction-parsing-dtc`

- **Hotfix branches** : `hotfix/[issue-id]-courte-description`
  - Exemple : `hotfix/NOV-789-fix-authentication-faille`

- **Release branches** : `release/vX.Y.Z`
  - Exemple : `release/v1.2.0`

- **Documentation branches** : `docs/sujet-de-la-documentation`
  - Exemple : `docs/mise-a-jour-workflow-git`

## Cycle de vie du développement

### 1. Création d'une branche de fonctionnalité

Toute nouvelle fonctionnalité commence par la création d'une branche dédiée à partir de `develop` :

```bash
# Mettre à jour develop
git checkout develop
git pull origin develop

# Créer la nouvelle branche
git checkout -b feature/NOV-123-nom-de-la-fonctionnalite
```

### 2. Développement et commits

Pendant le développement, les commits doivent suivre le format [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Où :
- **type** est l'un des suivants :
  - `feat` : Nouvelle fonctionnalité
  - `fix` : Correction de bug
  - `docs` : Documentation uniquement
  - `style` : Changements ne modifiant pas le code (espaces, formatage, etc.)
  - `refactor` : Refactorisation de code
  - `perf` : Améliorations de performance
  - `test` : Ajout ou modification de tests
  - `chore` : Tâches de maintenance, build, etc.

- **scope** est le module ou composant concerné (optionnel)
- **description** est un résumé court et concis

Exemples :

```
feat(auth): ajouter l'authentification via Google OAuth

fix(obd): corriger la déconnexion inattendue des dongles

docs(api): mettre à jour la documentation des endpoints OCR
```

### 3. Gestion des modifications en cours

#### Commits intermédiaires

Les commits intermédiaires permettent de sauvegarder votre travail régulièrement :

```bash
git add [fichiers]
git commit -m "feat(module): description de la modification"
```

#### Synchronisation avec develop

Pour éviter les divergences importantes, synchronisez régulièrement votre branche avec `develop` via rebase :

```bash
git fetch origin develop
git rebase origin/develop
```

#### Gestion des conflits

En cas de conflits lors du rebase :

1. Résolvez les fichiers en conflit
2. `git add [fichiers résolus]`
3. `git rebase --continue`
4. Si nécessaire : `git rebase --abort` pour annuler le rebase

### 4. Finalisation de la fonctionnalité

#### Préparation de la Pull Request

Avant de soumettre une Pull Request, effectuez ces vérifications :

1. Assurez-vous que la branche est à jour avec `develop`
   ```bash
   git fetch origin develop
   git rebase origin/develop
   ```

2. Vérifiez que les tests passent localement
   ```bash
   npm run test
   ```

3. Assurez-vous que le code respecte les standards
   ```bash
   npm run lint
   ```

4. Rebasez si nécessaire pour obtenir un historique propre
   ```bash
   git rebase -i HEAD~[nombre de commits]
   ```

5. Poussez votre branche vers le dépôt distant
   ```bash
   git push origin feature/NOV-123-nom-de-la-fonctionnalite
   ```

#### Création de la Pull Request

Créez une Pull Request sur GitHub avec les éléments suivants :

- **Titre** : Format Conventional Commits, incluant l'ID du ticket
  - Exemple : `feat(auth): NOV-123 implémentation de l'authentification Google OAuth`

- **Description** :
  - Lien vers le ticket Jira
  - Description détaillée des changements
  - Points d'attention pour les reviewers
  - Instructions de test si nécessaires
  - Screenshots/captures si pertinent

#### Template de Pull Request

```markdown
## Description
Cette PR implémente l'authentification via Google OAuth.
Lien vers le ticket: [NOV-123](https://novaevo.atlassian.net/browse/NOV-123)

## Changements
- Ajout du SDK Google OAuth
- Création du flux d'authentification OAuth
- Stockage sécurisé des tokens
- Tests unitaires et d'intégration

## Points d'attention
- La configuration des clés API est documentée dans le README
- Vérifier particulièrement la gestion du refresh token

## Comment tester
1. Configurer les variables d'environnement selon la documentation
2. Lancer l'application en mode développement
3. Cliquer sur "Se connecter avec Google"
4. Vérifier que le flux complet fonctionne

## Screenshots
![Capture du bouton de connexion](https://url-de-l-image.png)
```

### 5. Revue de code

#### Processus de revue

1. Assignez au moins deux reviewers :
   - Un tech lead ou senior développeur
   - Un autre développeur familier avec le domaine

2. La CI/CD lance automatiquement :
   - Tests unitaires et d'intégration
   - Analyse statique de code
   - Vérification du build

3. Les reviewers examinent :
   - La qualité du code
   - La couverture des tests
   - Le respect des standards
   - L'architecture et la conception
   - La performance et la sécurité

4. Cycle d'itération :
   - Feedback des reviewers
   - Modifications selon les commentaires
   - Nouvelle revue

#### Critères d'approbation

Une PR est approuvée quand :
- Au moins deux reviewers ont approuvé
- Tous les tests passent
- Tous les commentaires bloquants sont résolus
- Le code respecte les standards du projet

### 6. Merge dans develop

Une fois la PR approuvée, le merge dans `develop` se fait via l'interface GitHub :

- Option préférée : **Squash and merge**
  - Combine tous les commits en un seul
  - Maintient un historique propre
  - Conserve une référence à la PR

- Message de squash :
  ```
  feat(auth): implémentation de l'authentification Google OAuth (#123)
  
  * Ajout du SDK Google OAuth
  * Création du flux d'authentification
  * Stockage sécurisé des tokens
  * Tests unitaires et d'intégration
  ```

### 7. Nettoyage

Après le merge, nettoyez votre environnement local :

```bash
git checkout develop
git pull origin develop
git branch -d feature/NOV-123-nom-de-la-fonctionnalite
```

## Processus de release

### Préparation d'une release

1. Créez une branche de release à partir de `develop` :
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/v1.2.0
   ```

2. Effectuez les ajustements finaux :
   - Mise à jour des numéros de version
   - Finalisation du CHANGELOG
   - Documentation de dernière minute

3. Créez une PR de `release/v1.2.0` vers `main`
   - Tests complets sur l'environnement de staging
   - Validation finale par l'équipe produit

4. Après approbation, merge dans `main` :
   ```bash
   git checkout main
   git merge --no-ff release/v1.2.0
   git tag -a v1.2.0 -m "Version 1.2.0"
   git push origin main --tags
   ```

5. Synchronisez `develop` avec la release :
   ```bash
   git checkout develop
   git merge --no-ff release/v1.2.0
   git push origin develop
   ```

### Hotfixes

Pour les corrections urgentes en production :

1. Créez une branche hotfix à partir de `main` :
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/NOV-789-fix-critique
   ```

2. Implémentez et testez la correction

3. Créez des PRs vers `main` ET `develop`

4. Après merge dans `main`, créez un tag de version :
   ```bash
   git checkout main
   git pull origin main
   git tag -a v1.2.1 -m "Hotfix: correction critique d'authentification"
   git push origin --tags
   ```

## Workflow CI/CD

### Intégration avec GitHub Actions

Notre workflow Git est intégré avec GitHub Actions qui exécute automatiquement :

#### Sur chaque push dans une branche de feature :
- Linting et validation du format
- Tests unitaires
- Build de vérification

#### Sur création d'une PR vers develop :
- Tests complets (unitaires, intégration, e2e)
- Analyse de qualité de code (SonarQube)
- Build et déploiement sur environnement de revue

#### Sur merge dans develop :
- Tests complets
- Build et déploiement sur environnement de développement

#### Sur merge dans main :
- Tests complets
- Build et déploiement sur environnement de production
- Création des tags de release

## Bonnes pratiques

### Gestion des commits

- Gardez les commits atomiques (une seule préoccupation par commit)
- Écrivez des messages de commit descriptifs et cohérents
- Réorganisez vos commits avant de soumettre une PR (`git rebase -i`)

### Travail collaboratif

- Communiquez vos intentions avant de commencer des changements majeurs
- Créez des branches courtes et ciblées
- Utilisez l'assignation de PR pour éviter les travaux en doublon
- Faites des PR de taille raisonnable (<500 lignes) quand possible

### Documentation

- Documentez les changements d'API ou d'architecture
- Mettez à jour le CHANGELOG pour chaque feature significative
- Assurez-vous que le README est toujours à jour
- Incluez des commentaires pour le code complexe

## Résolution de problèmes

### Situations courantes

#### Reset à un état précédent
```bash
# Annuler les changements non commités
git checkout -- [fichier]

# Annuler le dernier commit (conserve les changements)
git reset HEAD~1

# Annuler le dernier commit (supprime les changements)
git reset --hard HEAD~1
```

#### Retrouver des changements perdus
```bash
# Voir l'historique de toutes les actions
git reflog

# Restaurer à un point spécifique
git checkout [hash de reflog]
```

#### Gérer un rebase incorrect
```bash
# Abandonner un rebase en cours
git rebase --abort

# Continuer un rebase après résolution de conflits
git rebase --continue
```

#### Synchroniser un fork avec le dépôt principal
```bash
# Ajouter le dépôt original comme remote
git remote add upstream [URL du dépôt original]

# Récupérer les derniers changements
git fetch upstream

# Merger les changements dans votre branche locale
git checkout main
git merge upstream/main
```

## Outils recommandés

### Extensions VS Code

- **GitLens** - Visualisation avancée de Git
- **Git History** - Historique de Git interactif
- **GitHub Pull Requests** - Gestion des PR depuis VS Code

### Outils CLI

- **git-flow** - Facilite l'utilisation du Git Flow
- **hub** - Extension GitHub pour la ligne de commande
- **conventional-changelog-cli** - Génération de CHANGELOG

### Outils GUI

- **GitKraken** - Interface graphique complète
- **Sourcetree** - Alternative graphique populaire
- **GitHub Desktop** - Client simple pour GitHub

## Formation et ressources

### Ressources internes

- Sessions de formation Git (programmées trimestriellement)
- Documentation dans le wiki (vous êtes ici!)
- Exemples de workflow dans le dépôt d'exemples

### Ressources externes

- [Pro Git Book](https://git-scm.com/book/fr/v2) - Guide complet de Git
- [Conventional Commits](https://www.conventionalcommits.org/) - Standard de messages de commit
- [Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials) - Tutoriels Git avancés

---

*Dernière mise à jour : 10 avril 2025*