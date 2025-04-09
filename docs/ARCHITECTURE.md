# Architecture de l'Assistant Auto Ultime

Ce document présente l'architecture globale de l'application Assistant Auto Ultime, détaillant les interactions entre les différents modules et composants du système.

## Vue d'ensemble

L'Assistant Auto Ultime est conçu selon une architecture modulaire qui permet une séparation claire des responsabilités et facilite l'intégration de nouvelles fonctionnalités.

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │   OCR    │  │  OBD-II  │  │   NLP    │  │  Image   │  │Abonnement││
│  │ Interface│  │ Interface│  │ Interface│  │Recognition│  │Interface ││
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼──────────────┼──┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                             API REST                                 │
└───────┬──────────────┬──────────────┬──────────────┬──────────────┬──┘
         │              │              │              │              │
┌────────▼─────┐ ┌──────▼───────┐ ┌────▼─────┐ ┌──────▼───────┐ ┌───▼─────────┐
│  Module OCR  │ │ Module OBD-II │ │Module NLP│ │Module Image │ │Module       │
│              │ │               │ │          │ │Recognition  │ │Subscriptions│
└──────┬───────┘ └───────┬───────┘ └────┬─────┘ └──────┬──────┘ └───────┬─────┘
        │                 │               │             │                │
┌───────▼────────────────▼───────────────▼─────────────▼────────────────▼─────┐
│                          Services Externes                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌────────────────────┐│
│  │ Google Cloud │  │ Dongle OBD-II│  │    OpenAI   │  │       Stripe       ││
│  │    Vision    │  │(Véhicule)    │  │     API     │  │(Gestion paiements) ││
│  └──────────────┘  └──────────────┘  └─────────────┘  └────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

## Interactions entre les modules

1. **Frontend** - Interface utilisateur React qui communique avec le backend via une API REST
   - Interfaces dédiées pour chaque fonctionnalité principale (OCR, OBD-II, NLP, etc.)
   - Gestion des abonnements et authentification

2. **API REST** - Points d'entrée backend pour toutes les fonctionnalités
   - Routage vers les modules appropriés
   - Validation des requêtes
   - Gestion des autorisations

3. **Modules Fonctionnels** - Implémentation des fonctionnalités métier
   - **Module OCR** : Extraction d'informations de cartes grises
   - **Module OBD-II** : Communication avec le dongle OBD-II et interprétation des données véhicule
   - **Module NLP** : Traitement du langage naturel pour les requêtes utilisateur
   - **Module Image Recognition** : Analyse d'images pour le diagnostic visuel
   - **Module ECU Flash** : Reprogrammation de l'ECU pour l'optimisation des performances
   - **Module Parts Finder** : Recherche multi-sources de pièces détachées
   - **Module Subscriptions** : Gestion des abonnements et paiements via Stripe
   - **Module Mapping Affiliations** : Système d'affiliation pour cartographies moteur

4. **Services Externes** - Intégrations avec des services tiers
   - Google Cloud Vision pour l'OCR
   - OpenAI pour le traitement du langage naturel
   - Stripe pour la gestion des paiements
   - APIs partenaires pour les cartographies et pièces détachées

## Flux de données

### Exemple : Analyse OCR de carte grise

1. L'utilisateur prend une photo de sa carte grise via l'interface OCR du frontend
2. L'image est envoyée au backend via l'API REST (`POST /ocr`)
3. Le module OCR transmet l'image à Google Cloud Vision API
4. L'API renvoie les textes extraits
5. Le module OCR analyse et structure ces données
6. Les informations structurées sont renvoyées au frontend via l'API REST
7. Le frontend affiche les résultats à l'utilisateur

### Exemple : Abonnement utilisateur

1. L'utilisateur choisit un plan d'abonnement via l'interface
2. Les informations sont envoyées au backend via l'API REST (`POST /subscribe`)
3. Le module Subscriptions crée un client et un abonnement dans Stripe
4. Stripe renvoie la confirmation et les détails de l'abonnement
5. Le module Subscriptions sauvegarde ces informations dans la base de données
6. La confirmation d'abonnement est renvoyée au frontend
7. L'interface indique à l'utilisateur que son abonnement est actif

## Stockage des données

- Base de données relationnelle (PostgreSQL) pour :
  - Utilisateurs et leurs profils
  - Informations d'abonnement
  - Historique des véhicules
  - Résultats des diagnostics

- Système de fichiers pour :
  - Images temporaires
  - Logs de diagnostic
  - Sauvegardes ECU

## Sécurité

- HTTPS pour toutes les communications
- Authentification JWT pour l'API
- Chiffrement des mots de passe (bcrypt)
- Stockage sécurisé des clés API externes
- Protection contre les injections SQL et XSS

## Évolutivité

L'architecture modulaire facilite :
- L'ajout de nouvelles fonctionnalités
- La mise à l'échelle horizontale des composants
- La maintenance indépendante de chaque module
- Le déploiement par service (microservices)
- L'intégration de nouveaux services externes