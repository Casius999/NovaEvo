# Documentation

Cette section contient toute la documentation du projet Assistant Auto Ultime.

## Structure de la documentation

### Documentation utilisateur
- `/user-guides` - Guides utilisateur pour chaque fonctionnalité
  - `/getting-started.md` - Guide de démarrage rapide
  - `/installation.md` - Guide d'installation
  - `/ocr-module.md` - Utilisation du module OCR pour cartes grises
  - `/obd2-module.md` - Guide de connexion et diagnostic OBD-II
  - `/voice-commands.md` - Liste des commandes vocales supportées
  - `/image-recognition.md` - Guide d'utilisation de la reconnaissance d'image
  - `/ecu-tuning.md` - Guide pour la reprogrammation ECU
  - `/parts-finder.md` - Recherche de pièces détachées

### Documentation technique
- `/technical` - Documentation technique
  - `/architecture.md` - Architecture globale du système
  - `/api-reference` - Documentation détaillée des API
  - `/data-models` - Modèles de données
  - `/security.md` - Considérations de sécurité
  - `/performance.md` - Optimisation des performances

### Documentation développeur
- `/dev` - Documentation pour les développeurs
  - `/setup.md` - Configuration de l'environnement de développement
  - `/coding-standards.md` - Standards de codage
  - `/testing.md` - Procédures de test
  - `/ci-cd.md` - Pipeline d'intégration continue
  - `/extension.md` - Guide pour étendre les fonctionnalités

### Plans et stratégie
- `/business` - Documents stratégiques
  - `/roadmap.md` - Feuille de route du projet
  - `/financial-plan.md` - Plan financier
  - `/market-analysis.md` - Analyse de marché
  - `/business-model.md` - Modèle économique

### Légal
- `/legal` - Documents légaux
  - `/terms-of-service.md` - Conditions d'utilisation
  - `/privacy-policy.md` - Politique de confidentialité
  - `/warranty-disclaimer.md` - Avertissements et garanties

## Comment contribuer à la documentation

Pour contribuer à la documentation, veuillez suivre ces étapes :
1. Assurez-vous que la documentation respecte le format Markdown
2. Suivez la structure établie
3. Incluez des captures d'écran ou des diagrammes si nécessaire
4. Soumettez vos modifications via une Pull Request

## Génération de la documentation

La documentation est automatiquement générée en site web statique à l'aide de Docusaurus :

```bash
cd docs
npm install
npm run build
```