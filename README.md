# NovaEvo

## Description
NovaEvo est une plateforme complète pour les passionnés et professionnels de l'automobile, intégrant des fonctionnalités avancées d'OCR, de diagnostic OBD-II, de traitement du langage naturel, de reconnaissance d'images, de reprogrammation ECU et de recherche de pièces détachées. La plateforme propose désormais un système d'abonnement et un service d'affiliation global pour tous les achats effectués via l'application.

## Objectifs
- Simplifier le diagnostic automobile via une interface intuitive
- Automatiser la reconnaissance des informations de carte grise
- Fournir un accès direct aux données OBD-II du véhicule
- Permettre l'interaction par commandes vocales naturelles
- Offrir un diagnostic visuel via reconnaissance d'images
- Faciliter la reprogrammation ECU pour l'optimisation des performances
- Proposer un catalogue complet de pièces détachées (origine, sport, compétition)
- **NOUVEAU** : Offrir un service d'abonnement avec dongle OBD-II inclus
- **NOUVEAU** : Implémenter un système d'affiliation global assurant le suivi de 100% des achats réalisés via l'application
- **NOUVEAU** : Intégrer des modules contextuels avec synchronisation en temps réel
- **NOUVEAU** : Planifier automatiquement des rendez-vous avec des professionnels qualifiés
- **NOUVEAU** : Garantir une intégrité et une traçabilité totale des données via notre architecture hiérarchique

## Structure du dépôt
- `/ocr` - Module de scan OCR pour la carte grise
- `/obd2` - Module de connexion avec le dongle OBD-II
- `/nlp` - Module de traitement du langage naturel (chat et commandes vocales)
- `/image_recognition` - Reconnaissance d'image pour le diagnostic visuel
- `/ecu_flash` - Module de reprogrammation ECU (tuning & flash)
- `/parts_finder` - Recherche de pièces détachées et planification de rendez-vous
- `/frontend` - Interface utilisateur (Web/Mobile)
- `/docs` - Documentation complète du projet
- `/tests` - Tests unitaires et d'intégration
- `/subscriptions` - Système de gestion des abonnements avec Stripe
- `/mapping_affiliations` - Module d'affiliation global pour tous les achats
- `/utils` - Utilitaires pour la gestion des contextes, métriques et sécurité

## Nouveautés - Version 3.0

### Modules Contextuels et Synchronisation
NovaEvo intègre désormais une architecture de synchronisation avec des serveurs dédiés pour enrichir l'expérience utilisateur avec des données contextuelles en temps réel :

- **Données Contextuelles** : Enrichissement des informations véhicules, codes d'erreur, pièces détachées et compatibilité ECU
- **Synchronisation Temps Réel** : Communication automatisée avec des serveurs tiers pour des données toujours à jour
- **Sécurité Renforcée** : Vérification cryptographique des sources de données et protection contre les altérations
- **Analyse de Performance** : Suivi et optimisation des performances pour une expérience fluide

### Planification