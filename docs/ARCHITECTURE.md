# Architecture de NovaEvo

Ce document présente l'architecture globale de la plateforme NovaEvo, détaillant les interactions entre les différents modules et composants du système, avec un accent particulier sur les éléments différenciants de notre solution.

## Vue d'ensemble

NovaEvo est conçu selon une architecture modulaire et évolutive qui permet une séparation claire des responsabilités et facilite l'intégration de nouvelles fonctionnalités, tout en offrant une expérience utilisateur fluide et intégrée.

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    Frontend                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │   OCR    │  │  OBD-II  │  │   NLP    │  │  Image   │  │Abonnement│  │ Planning │ │
│  │ Interface│  │ Interface│  │ Interface│  │Recognition│  │Interface │  │Intelligent│ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──┘
         │              │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    API REST                                          │
└───────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──┘
         │              │              │              │              │              │
┌────────▼─────┐ ┌──────▼───────┐ ┌────▼─────┐ ┌──────▼───────┐ ┌───▼─────────┐ ┌──▼─────────┐
│  Module OCR  │ │ Module OBD-II │ │Module NLP│ │Module Image │ │Module       │ │Module KBIS │
│              │ │               │ │          │ │Recognition  │ │Subscriptions│ │Verification│
└──────┬───────┘ └───────┬───────┘ └────┬─────┘ └──────┬──────┘ └───────┬─────┘ └──────┬─────┘
        │                 │               │             │                │              │  
        │                 │               │             │                │              │
┌───────▼─────┐ ┌─────────▼─────┐ ┌──────▼────────┐ ┌──▼─────────┐ ┌────▼──────┐  ┌───▼────────┐
│Module       │ │Module         │ │Module         │ │Module      │ │Module     │  │Module      │
│Parts Finder │ │ECU Flash      │ │Planning       │ │Affiliation │ │Feedback   │  │Professional│
│             │ │               │ │Intelligence   │ │Global 100% │ │Communauté │  │Network     │
└──────┬──────┘ └───────┬───────┘ └──────┬────────┘ └──────┬─────┘ └─────┬─────┘  └─────┬──────┘
        │                │                │                 │              │              │
┌───────▼────────────────▼────────────────▼─────────────────▼──────────────▼──────────────▼─────┐
│                                 Services Externes                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │ Google Cloud │  │ Dongle OBD-II│  │    OpenAI   │  │   Stripe    │  │ Base de Vérification││
│  │    Vision    │  │(Véhicule)    │  │     API     │  │  (Paiement) │  │      KBIS           ││
│  └──────────────┘  └──────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Architecture des modules clés

### 1. Module de Vérification KBIS

Ce module assure l'authentification et la légitimité des professionnels:

```
┌─────────────────────────────────────────────────────────┐
│              Module de Vérification KBIS                │
│                                                         │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────┐  │
│  │ Scan KBIS   │ -> │ OCR Spécialisé │ -> │Validation│  │
│  └─────────────┘    └────────────────┘    └────┬─────┘  │
│                                                │        │
│  ┌──────────────┐   ┌─────────────────┐   ┌───▼──────┐  │
│  │Statut Pro    │<- │Filtres Anti-    │<- │Vérif DB  │  │
│  │Attribué      │   │Fraude           │   │Officielle│  │
│  └──────────────┘   └─────────────────┘   └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2. Module de Planification Intelligente

```
┌─────────────────────────────────────────────────────────┐
│           Module de Planification Intelligente          │
│                                                         │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────┐  │
│  │ Base données│ -> │  Algorithme    │ -> │Priorisa- │  │
│  │ temporelle  │    │  d'optimisation│    │tion      │  │
│  └─────────────┘    └────────────────┘    └────┬─────┘  │
│                                                │        │
│  ┌──────────────┐   ┌─────────────────┐   ┌───▼──────┐  │
│  │Alertes &     │<- │Synchronisation  │<- │Recomman- │  │
│  │Rappels       │   │Bidirectionnelle │   │dation    │  │
│  └──────────────┘   └─────────────────┘   └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 3. Module de Feedback Communautaire

```
┌─────────────────────────────────────────────────────────┐
│              Module de Feedback Communautaire           │
│                                                         │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────┐  │
│  │ Collection  │ -> │ Vérification   │ -> │Analyse   │  │
│  │ Evaluations │    │ Authenticité   │    │Statistique│  │
│  └─────────────┘    └────────────────┘    └────┬─────┘  │
│                                                │        │
│  ┌──────────────┐   ┌─────────────────┐   ┌───▼──────┐  │
│  │Impact sur    │<- │Modération       │<- │Publication│  │
│  │Recommandation│   │Proactive        │   │Feedback  │  │
│  └──────────────┘   └─────────────────┘   └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 4. Module d'Affiliation Global 100%

```
┌─────────────────────────────────────────────────────────┐
│              Module d'Affiliation Global                │
│                                                         │
│  ┌─────────────┐    ┌────────────────┐    ┌──────────┐  │
│  │ Tracking    │ -> │  Attribution   │ -> │Anti-Fraude│  │
│  │ Multi-canal │    │  Multi-touch   │    │Validation │  │
│  └─────────────┘    └────────────────┘    └────┬─────┘  │
│                                                │        │
│  ┌──────────────┐   ┌─────────────────┐   ┌───▼──────┐  │
│  │Génération    │<- │Recommandations  │<- │Data      │  │
│  │Commissions   │   │Personnalisées   │   │Analytics │  │
│  └──────────────┘   └─────────────────┘   └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Interactions entre les modules

1. **Frontend** - Interface utilisateur React qui communique avec le backend via une API REST
   - Interfaces dédiées pour chaque fonctionnalité principale (OCR, OBD-II, NLP, etc.)
   - Interface de planification intelligente de rendez-vous
   - Système d'authentification différencié particuliers/professionnels
   - Gestion des abonnements (Standard/Premium)

2. **API REST** - Points d'entrée backend pour toutes les fonctionnalités
   - Routage vers les modules appropriés
   - Validation des requêtes
   - Gestion des autorisations
   - Support des requêtes complexes multi-modules

3. **Modules Fonctionnels** - Implémentation des fonctionnalités métier
   - **Module OCR** : Extraction d'informations de cartes grises
   - **Module OBD-II** : Communication avec le dongle OBD-II et interprétation des données véhicule
   - **Module NLP** : Traitement du langage naturel pour les requêtes utilisateur
   - **Module Image Recognition** : Analyse d'images pour le diagnostic visuel
   - **Module ECU Flash** : Reprogrammation de l'ECU pour l'optimisation des performances
   - **Module Parts Finder** : Recherche multi-sources de pièces détachées
   - **Module Subscriptions** : Gestion des abonnements et paiements via Stripe
   - **Module KBIS Verification** : Authentification des professionnels par scan KBIS
   - **Module Planning Intelligence** : Planification intelligente des rendez-vous
   - **Module Affiliation Global** : Système d'affiliation couvrant 100% des transactions
   - **Module Feedback Communautaire** : Évaluation et notation des professionnels
   - **Module Professional Network** : Gestion du réseau de professionnels vérifiés

4. **Services Externes** - Intégrations avec des services tiers
   - Google Cloud Vision pour l'OCR
   - OpenAI pour le traitement du langage naturel
   - Stripe pour la gestion des paiements
   - Base de données officielle pour vérification KBIS
   - APIs partenaires pour les cartographies et pièces détachées

## Flux de données clés

### Flux 1 : Vérification d'un professionnel par KBIS

1. Le professionnel scanne son KBIS via l'interface mobile
2. L'image est envoyée au backend via l'API REST (`POST /verification/kbis`)
3. Le module KBIS Verification traite l'image avec l'OCR spécialisé
4. Les informations extraites sont vérifiées auprès de la base de données officielle
5. Le système anti-fraude analyse la cohérence des informations
6. Le statut "Professionnel Vérifié" est attribué avec le niveau approprié
7. La confirmation est renvoyée au frontend
8. L'interface affiche le badge de vérification et active les fonctionnalités pro

### Flux 2 : Planification intelligente d'un rendez-vous

1. L'utilisateur indique son besoin d'intervention via l'interface
2. La demande est envoyée au backend via l'API REST (`POST /planning/appointment`)
3. Le module Planning Intelligence analyse le besoin et la priorité
4. L'algorithme d'optimisation consulte les disponibilités des professionnels vérifiés à proximité
5. Le système génère des recommandations de créneaux optimaux
6. Les options sont renvoyées au frontend
7. L'utilisateur sélectionne un créneau
8. Le système confirme le rendez-vous et l'ajoute aux agendas respectifs
9. Des rappels automatiques sont programmés

### Flux 3 : Transaction avec affiliation 100%

1. L'utilisateur consulte une pièce détachée recommandée pour son véhicule
2. Il clique sur "Commander" via l'interface
3. L'action est interceptée par le module d'Affiliation (`POST /affiliation/track`)
4. Le système génère un lien de tracking avec paramètres uniques
5. L'utilisateur est redirigé vers le site du partenaire avec le tracking actif
6. L'achat est réalisé sur le site partenaire
7. Le module d'Affiliation capture la transaction complète (API, webhook ou scraping)
8. La commission est calculée et enregistrée
9. L'historique d'achat est mis à jour dans le profil utilisateur
10. Les futures recommandations sont affinées en fonction de cet achat

## Base de données et stockage

### Schéma relationnel principal

```
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│    Users      │          │   Vehicles    │          │ Appointments  │
├───────────────┤          ├───────────────┤          ├───────────────┤
│ id            │◄─────────┤ owner_id      │          │ id            │
│ type          │          │ make          │          │ user_id       │
│ email         │          │ model         │◄─────────┤ vehicle_id    │
│ is_verified   │          │ year          │          │ pro_id        │
│ subscription  │          │ vin           │          │ datetime      │
│ created_at    │          │ plate_number  │          │ status        │
└───────────────┘          └───────────────┘          └───────────────┘
        ▲                                                     │
        │                                                     │
        │                                                     ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ Professionals │          │  Affiliations │          │   Feedback    │
├───────────────┤          ├───────────────┤          ├───────────────┤
│ id            │          │ id            │          │ id            │
│ user_id       │          │ user_id       │          │ appointment_id│
│ kbis_status   │          │ transaction_id│          │ rating        │
│ kbis_number   │          │ amount        │          │ comment       │
│ services      │◄─────────┤ partner_id    │◄─────────┤ pro_id        │
│ verification  │          │ commission    │          │ created_at    │
└───────────────┘          └───────────────┘          └───────────────┘
```

### Stockage spécialisé

- **Base de données temporelle** (TimescaleDB) pour:
  - Données de planification et disponibilité des créneaux
  - Historique des interventions
  - Métriques de performance des professionnels

- **Base de données graphe** pour:
  - Réseau de professionnels
  - Relations entre utilisateurs, véhicules et services
  - Recommandations contextuelles

- **Système de fichiers sécurisé** pour:
  - Documents KBIS scannés (chiffrés)
  - Images des véhicules
  - Diagnostics détaillés

## Sécurité et Conformité

### Sécurité des données

- HTTPS pour toutes les communications
- Authentification JWT avec niveaux d'accès différenciés
- Chiffrement des données sensibles (AES-256)
- Isolation des données professionnelles/particuliers
- Protection contre les injections SQL, XSS et CSRF
- Audit logs pour toutes les actions sensibles

### Conformité RGPD

- Stockage séparé des données personnelles
- Processus d'effacement des données
- Mécanismes de consentement explicite
- Politique de rétention des données claire
- Procédures de notification en cas de faille

### Sécurité du système de vérification KBIS

- Double validation des documents
- Détection des tentatives de fraude
- Isolation du système de stockage des documents
- Rotation automatique des clés de chiffrement
- Monitoring continu des anomalies

## Scalabilité et haute disponibilité

L'architecture de NovaEvo est conçue pour une scalabilité horizontale et verticale:

- **Déploiement en conteneurs** (Docker/Kubernetes)
- **Architecture microservices** pour scaling indépendant
- **Cache distribué** (Redis) pour optimisation des performances
- **Load balancing** intelligent
- **Réplication multi-région** pour haute disponibilité
- **Circuit breakers** pour résilience des services externes
- **Auto-scaling** basé sur la charge

## Technologies clés

- **Backend**: Node.js, Python (ML/AI), Go (services critiques)
- **Frontend**: React Native, Redux, GraphQL
- **Bases de données**: PostgreSQL, TimescaleDB, Redis, Neo4j
- **Infrastructure**: AWS/GCP, Kubernetes, Terraform
- **Monitoring**: Prometheus, Grafana, ELK Stack
- **CI/CD**: GitHub Actions, Jenkins, ArgoCD

## Évolution future

L'architecture modulaire de NovaEvo facilite:
- L'intégration de nouveaux services et partenaires
- L'expansion internationale avec adaptations locales
- L'ajout de fonctionnalités avancées (IA prédictive, réalité augmentée)
- La connexion avec d'autres systèmes de l'écosystème automobile
- L'évolution vers une marketplace complète de services automobile

---

*Document mis à jour le 9 avril 2025*