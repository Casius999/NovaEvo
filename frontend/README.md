# Frontend - Interface Utilisateur

Ce module gère l'interface utilisateur web et mobile de l'Assistant Auto Ultime.

## Fonctionnalités
- Interface réactive et responsive (web et mobile)
- Dashboard principal avec indicateurs clés
- Zone de dialogue interactif (chat et commandes vocales)
- Visualisation des données OBD-II en temps réel
- Panneau de contrôle pour le tuning ECU
- Interface de recherche de pièces
- Upload et analyse d'images
- Gestion du profil véhicule

## Technologies
- React pour l'interface web
- React Native pour l'application mobile
- WebSockets pour les communications en temps réel
- D3.js pour la visualisation de données
- Material-UI et Tailwind CSS pour le design

## Structure du module
- `/web` - Application web React
  - `/components` - Composants UI réutilisables
  - `/pages` - Pages principales de l'application
  - `/hooks` - Hooks React personnalisés
  - `/context` - Gestionnaires d'état global
  - `/services` - Services d'API et de communication
  - `/utils` - Utilitaires et helpers
  - `/assets` - Ressources statiques

- `/mobile` - Application mobile React Native
  - `/components` - Composants UI réutilisables
  - `/screens` - Écrans principaux
  - `/navigation` - Configuration de la navigation
  - `/hooks` - Hooks React personnalisés
  - `/services` - Services d'API et de communication

- `/common` - Code partagé entre web et mobile
  - `/theme` - Thèmes et styles partagés
  - `/api` - Clients API partagés
  - `/utils` - Utilitaires communs

## Fonctionnalités d'interface
- Mode jour/nuit
- Thèmes personnalisables
- Mode dashboard pour tableau de bord
- Mode diagnostic avec visualisation en temps réel
- Internationalisation (multi-langue)
- Accessibilité (conforme WCAG)