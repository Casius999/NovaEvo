# Module OBD-II

Ce module gère la connexion avec les dongles OBD-II et l'interprétation des données du véhicule.

## Fonctionnalités
- Communication avec les interfaces OBD-II via Bluetooth, WiFi ou USB
- Lecture des codes d'erreur (DTC)
- Monitoring en temps réel des paramètres du véhicule
- Enregistrement des données pour analyse ultérieure

## Technologies
- Protocoles OBD-II (SAE J1979)
- Bibliothèques de communication série
- Interprétation des PIDs standard et constructeur

## Structure du module
- `/adapters` - Pilotes pour différents types de dongles OBD-II
- `/protocols` - Implémentation des différents protocoles OBD-II
- `/dtc` - Base de données et interprétation des codes d'erreur
- `/realtime` - Monitoring et analyse en temps réel
- `/api` - Interface pour l'intégration avec les autres modules

## Compatibilité
- Protocoles supportés: ISO 15765 (CAN), ISO 14230 (KWP2000), ISO 9141-2, J1850 PWM, J1850 VPW
- Marques compatibles: Voir la liste complète dans la documentation