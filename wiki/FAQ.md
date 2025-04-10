# Questions Fréquentes (FAQ)

Cette page rassemble les questions les plus fréquemment posées concernant le projet NovaEvo, son utilisation, son architecture et son développement. Elle est organisée par thématiques pour faciliter la recherche d'informations.

## Général

### Qu'est-ce que NovaEvo?
NovaEvo est une plateforme complète pour les passionnés et professionnels de l'automobile, intégrant des fonctionnalités avancées d'OCR, de diagnostic OBD-II, de traitement du langage naturel, de reconnaissance d'images, de reprogrammation ECU et de recherche de pièces détachées. La plateforme propose également un système d'abonnement et un service d'affiliation global pour tous les achats effectués via l'application.

### Quels sont les objectifs principaux de NovaEvo?
Les objectifs principaux de NovaEvo sont :
- Démocratiser l'accès à des outils de diagnostic automobile avancés
- Créer un écosystème complet réunissant utilisateurs et professionnels du secteur
- Offrir des fonctionnalités de pointe exploitant l'IA et les technologies connectées
- Optimiser l'expérience de maintenance et d'amélioration automobile
- Générer de la valeur pour l'ensemble des acteurs de l'écosystème

### Comment NovaEvo se différencie-t-il de ses concurrents?
NovaEvo se distingue par :
- Une approche intégrée combinant diagnostic, recherche de pièces et mise en relation
- Des technologies de pointe en OCR, NLP et reconnaissance d'images
- Un système d'affiliation global couvrant l'ensemble des transactions
- Une architecture modulaire et évolutive
- Une intelligence contextuelle avancée
- Des capacités de monitoring et d'allocation dynamique des ressources

## Technique

### Quelle est l'architecture globale de NovaEvo?
NovaEvo implémente une architecture à la fois hiérarchique (verticalement) et modulaire (horizontalement). Cette structure bidimensionnelle offre cohérence globale et flexibilité fonctionnelle. L'architecture se divise en quatre niveaux hiérarchiques (stratégique, tactique, opérationnel, fondamental) et en modules fonctionnels indépendants. Pour plus de détails, consultez la page [Architecture](Architecture).

### Quelles technologies sont utilisées par NovaEvo?
NovaEvo utilise un stack technologique moderne incluant :
- **Backend** : Python, Node.js, FastAPI, Express
- **Database** : PostgreSQL, Redis, MongoDB
- **Frontend** : React, React Native
- **Infrastructure** : Docker, Kubernetes, Cloud Services
- **AI/ML** : TensorFlow, PyTorch, OpenCV
- **DevOps** : GitHub Actions, Prometheus, Grafana

### Comment contribuer au développement de NovaEvo?
Pour contribuer au projet :
1. Familiarisez-vous avec notre [Workflow Git](Workflow-Git)
2. Consultez la section [Gouvernance Collaborative](Gouvernance-Collaborative)
3. Identifiez les tâches ouvertes dans notre backlog
4. Suivez nos standards de codage et procédures de revue
5. Soumettez vos Pull Requests selon le processus défini

### Quelle est la stratégie de test de NovaEvo?
Notre approche de testing est pyramidale :
- **Tests unitaires** : couverture >80% du code
- **Tests d'intégration** : vérification des interactions entre composants
- **Tests fonctionnels** : validation des scénarios métier
- **Tests E2E** : validation des parcours utilisateurs complets
- **Tests de performance** : évaluation sous charge
Pour plus de détails, consultez notre [Pipeline CI/CD](Pipeline-CI-CD).

## Fonctionnalités

### Comment fonctionne le module OCR?
Le module OCR permet la numérisation et l'extraction automatique de données depuis des documents automobiles (carte grise, certificat d'immatriculation, factures d'entretien, etc.). Il utilise des algorithmes de deep learning spécialement entraînés pour reconnaître les formats de documents automobiles et en extraire les informations pertinentes avec une haute précision.

### Comment se connecter à l'interface OBD-II?
La connexion OBD-II se fait via un dongle Bluetooth ou WiFi compatible. L'application détecte automatiquement les dongles disponibles et guide l'utilisateur pour la connexion. Une fois connecté, NovaEvo peut communiquer avec les calculateurs du véhicule pour lire les codes d'erreur, consulter les données en temps réel et effectuer des diagnostics avancés.

### Qu'est-ce que la fonctionnalité de reprogrammation ECU?
La fonctionnalité de reprogrammation ECU (ou "flash") permet d'optimiser les paramètres du calculateur moteur pour améliorer les performances, la consommation ou la fiabilité du véhicule. Cette fonctionnalité avancée est encadrée par des vérifications de sécurité strictes et nécessite des permissions spécifiques.

### Comment fonctionne le système d'affiliation?
Le système d'affiliation global de NovaEvo permet de tracker toutes les transactions issues de l'application (achats de pièces, services professionnels, etc.). Une commission est générée et distribuée selon le parcours utilisateur et les intervenants dans la chaîne de valeur. Des tableaux de bord détaillés permettent de suivre les revenus d'affiliation.

## Utilisation

### Comment s'inscrire à NovaEvo?
L'inscription peut se faire directement via l'application mobile ou le site web. Pour les particuliers, seule une adresse email vérifiée est nécessaire. Pour les professionnels, une validation supplémentaire incluant la vérification KBIS et des certifications professionnelles est requise.

### Quels types d'abonnements sont disponibles?
NovaEvo propose plusieurs formules d'abonnement :
- **Basic** : Fonctionnalités essentielles de diagnostic
- **Premium** : Fonctionnalités avancées, accès illimité aux diagnostics
- **Professional** : Outils spécifiques pour les professionnels, API d'intégration
- **Enterprise** : Solutions personnalisées pour les grandes entreprises
Pour plus de détails, consultez la page [Modèle Économique](Modèle-Économique).

### Comment est assurée la sécurité des données?
La sécurité des données est une priorité :
- Chiffrement des données en transit et au repos
- Authentification multi-facteurs
- Politique stricte de minimisation des données
- Conformité RGPD et autres réglementations
- Audits de sécurité réguliers
Pour plus de détails, consultez la page [Sécurité et Conformité](Sécurité-et-Conformité).

## Développement Futur

### Quelle est la roadmap de NovaEvo?
Notre roadmap inclut :
- Extension des compatibilités véhicules
- Expansion géographique vers de nouveaux marchés
- Intégration de nouvelles technologies (IA, IoT)
- Développement de nouvelles fonctionnalités premium
- Enrichissement de l'écosystème partenaires
La roadmap détaillée est consultable sur la page [Roadmap](Roadmap).

### Comment proposer de nouvelles fonctionnalités?
Les propositions de fonctionnalités peuvent être soumises via :
- L'outil de feedback intégré à l'application
- Notre plateforme GitHub (via les issues)
- Les sessions de co-création avec la communauté
Toutes les propositions sont évaluées selon notre processus de priorisation produit.

### Comment NovaEvo assure-t-il la compatibilité avec les différents véhicules?
La compatibilité est assurée par :
- Une base de données complète de protocoles et spécifications
- Des mises à jour régulières des définitions véhicules
- Des tests sur un large panel de marques et modèles
- Des partenariats avec les constructeurs et équipementiers
- Des retours de la communauté utilisateurs

## Support

### Comment obtenir de l'aide en cas de problème?
Le support est disponible via :
- La documentation en ligne (wiki, tutoriels)
- L'assistant IA intégré à l'application
- Le forum communautaire
- Le support technique par email
- Le support téléphonique (abonnements premium)

### Où signaler un bug ou un problème?
Les bugs peuvent être signalés :
- Via la fonctionnalité de feedback dans l'application
- Sur la plateforme GitHub (pour les problèmes techniques)
- Auprès du support client pour les problèmes utilisateurs
Chaque signalement est analysé, priorisé et suivi selon nos processus de qualité.

### Comment devenir partenaire de NovaEvo?
Pour devenir partenaire :
1. Consultez notre programme partenaires sur le site web
2. Remplissez le formulaire de demande de partenariat
3. Un responsable partenariats vous contactera pour évaluer les opportunités de collaboration
4. Un contrat de partenariat sera établi selon votre profil et vos objectifs

---

*Cette FAQ est régulièrement mise à jour en fonction des questions récurrentes. Dernière mise à jour : 10 avril 2025*