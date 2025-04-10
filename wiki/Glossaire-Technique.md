# Glossaire Technique

Ce glossaire fournit les définitions des termes techniques utilisés dans le projet NovaEvo. Il est organisé par ordre alphabétique et sert de référence pour standardiser la terminologie utilisée dans notre documentation, notre code et nos communications.

## A

### API (Application Programming Interface)
Interface permettant à des applications de communiquer entre elles. NovaEvo expose plusieurs APIs pour permettre l'intégration avec des systèmes tiers.

### Architecture Hiérarchique
Approche architecturale de NovaEvo organisant le système en quatre niveaux distincts (stratégique, tactique, opérationnel, fondamental), chacun avec des responsabilités spécifiques.

### Architecture Modulaire
Approche de conception de NovaEvo divisant le système en modules fonctionnels indépendants qui peuvent être développés, testés et déployés séparément.

### Auto-scaling
Mécanisme permettant d'adapter automatiquement les ressources allouées (serveurs, conteneurs, etc.) en fonction de la charge du système.

## B

### Backend
Ensemble des composants serveur de NovaEvo qui traitent la logique métier, l'accès aux données et les intégrations avec des systèmes externes.

### Blue-Green Deployment
Technique de déploiement utilisant deux environnements identiques (bleu et vert) permettant de basculer le trafic de l'un à l'autre pour minimiser les temps d'arrêt.

### BFF (Backend For Frontend)
Pattern d'architecture où des services backend spécifiques sont créés pour servir les besoins particuliers de chaque interface utilisateur (web, mobile, etc.).

## C

### CI/CD (Continuous Integration/Continuous Deployment)
Ensemble de pratiques automatisant l'intégration, les tests et le déploiement du code. NovaEvo utilise GitHub Actions pour implémenter ces processus.

### Circuit Breaker
Pattern de conception qui empêche une application d'effectuer des opérations susceptibles d'échouer, prévenant les cascades de défaillances.

### CQRS (Command Query Responsibility Segregation)
Pattern architectural séparant les opérations de lecture (queries) et d'écriture (commands) pour optimiser les performances et la scalabilité.

## D

### DevOps
Culture, pratiques et outils visant à unifier le développement logiciel (Dev) et l'administration des infrastructures (Ops) pour accélérer et fiabiliser les déploiements.

### Dongle OBD-II
Périphérique matériel se connectant au port OBD-II d'un véhicule et permettant la communication avec les systèmes informatiques embarqués.

### DDD (Domain-Driven Design)
Approche de conception logicielle centrée sur le domaine métier et ses modèles, utilisée dans certains modules complexes de NovaEvo.

## E

### ECU (Engine Control Unit)
Calculateur électronique contrôlant divers aspects du fonctionnement d'un moteur. NovaEvo permet leur diagnostic et, pour certains modèles, leur reprogrammation.

### Event Sourcing
Pattern architectural où les changements d'état d'une application sont capturés comme séquence d'événements, permettant ainsi une traçabilité complète.

## F

### Feature Flag (ou Feature Toggle)
Technique permettant d'activer ou désactiver des fonctionnalités spécifiques sans nécessiter de redéploiement, utilisée pour les tests A/B et les déploiements progressifs.

### Frontend
Interfaces utilisateur de NovaEvo, incluant l'application mobile, l'interface web et les dashboards d'administration.

## G

### GitFlow
Modèle de branches Git adapté par NovaEvo pour organiser le développement collaboratif et garantir la stabilité des branches principales.

## I

### IaC (Infrastructure as Code)
Pratique consistant à gérer l'infrastructure via des fichiers de configuration versionnés plutôt que par configuration manuelle. NovaEvo utilise Terraform et Kubernetes manifests.

### Idempotence
Propriété d'une opération qui peut être appliquée plusieurs fois sans changer le résultat au-delà de la première application, essentielle pour les API robustes.

## K

### Kubernetes
Plateforme d'orchestration de conteneurs utilisée par NovaEvo pour gérer le déploiement, la mise à l'échelle et l'exploitation des applications conteneurisées.

### KPI (Key Performance Indicator)
Indicateur clé de performance permettant de mesurer l'atteinte d'objectifs opérationnels ou stratégiques. NovaEvo suit de nombreux KPIs à différents niveaux.

## M

### Microservices
Architecture où l'application est composée de petits services indépendants communiquant via API. Plusieurs composants de NovaEvo suivent cette approche.

### Monitoring
Surveillance continue des performances, de la disponibilité et de l'état général du système. NovaEvo implémente un système de monitoring multi-niveaux.

### MTTR (Mean Time To Recovery)
Temps moyen nécessaire pour rétablir un service après une panne. Un KPI critique suivi par l'équipe SRE de NovaEvo.

## N

### NLP (Natural Language Processing)
Traitement automatique du langage naturel, utilisé par l'assistant conversationnel de NovaEvo pour comprendre les requêtes des utilisateurs.

## O

### OBD-II (On-Board Diagnostics II)
Standard de diagnostic automobile permettant l'accès aux sous-systèmes du véhicule. NovaEvo s'intègre avec ce protocole pour le diagnostic en temps réel.

### OCR (Optical Character Recognition)
Technologie de reconnaissance optique de caractères permettant d'extraire du texte depuis des images. Utilisée pour numériser documents et plaques d'immatriculation.

### Observability
Capacité à comprendre l'état interne d'un système à partir de ses sorties externes, combinant monitoring, logging et tracing.

## P

### PII (Personally Identifiable Information)
Informations permettant d'identifier directement ou indirectement une personne. NovaEvo implémente des protections strictes pour ces données.

### Prometheus
Système de monitoring open-source utilisé par NovaEvo pour collecter et stocker des métriques en temps réel.

## R

### REST (Representational State Transfer)
Architecture de conception pour les API web utilisée par la plupart des services NovaEvo pour assurer interopérabilité et simplicité.

### RGPD (Règlement Général sur la Protection des Données)
Règlement européen sur la protection des données personnelles auquel NovaEvo se conforme strictement.

### RUM (Real User Monitoring)
Technique de surveillance des performances telles qu'expérimentées par les utilisateurs réels de l'application.

## S

### SLA (Service Level Agreement)
Engagement contractuel sur la disponibilité et les performances des services fournis. NovaEvo définit des SLAs pour ses différentes offres et composants.

### SRE (Site Reliability Engineering)
Discipline appliquant les principes du génie logiciel aux opérations d'infrastructure, utilisée par l'équipe opérationnelle de NovaEvo.

### Swagger (OpenAPI)
Spécification pour décrire, produire, consommer et visualiser des services web RESTful. Toutes les API NovaEvo sont documentées avec OpenAPI.

## T

### TDD (Test-Driven Development)
Méthode de développement où les tests sont écrits avant le code, pratiquée sur les composants critiques de NovaEvo.

### Telemetry
Collecte automatisée de données à distance sur le fonctionnement du système, essentielle pour le monitoring et le diagnostic.

## U

### UX (User Experience)
Expérience globale qu'un utilisateur a en interagissant avec NovaEvo, incluant l'interface, les performances et les émotions suscitées.

## V

### VIN (Vehicle Identification Number)
Numéro d'identification unique d'un véhicule, utilisé par NovaEvo pour identifier précisément les modèles et garantir la compatibilité des fonctionnalités.

## W

### Webhook
Mécanisme HTTP permettant à une application de fournir à d'autres applications des informations en temps réel. NovaEvo expose des webhooks pour les intégrations tierces.

## Z

### Zero-downtime Deployment
Technique de déploiement permettant de mettre à jour une application sans interruption de service, utilisée par NovaEvo pour maximiser la disponibilité.

---

*Ce glossaire est régulièrement mis à jour pour refléter l'évolution du projet et de sa terminologie. Dernière mise à jour : 10 avril 2025*