# Module OBD-II - Diagnostic Automobile en Temps Réel

Ce module permet à l'Assistant Auto Ultime de se connecter à l'interface OBD-II (On-Board Diagnostics II) d'un véhicule pour récupérer des données en temps réel.

## Fonctionnalités

- Connexion à un dongle OBD-II (ELM327, OBDLink MX+, etc.)
- Récupération du régime moteur (RPM)
- Récupération de la vitesse actuelle
- Lecture des codes d'erreur (DTC)
- Récupération d'informations de base du véhicule (température, niveau de carburant, etc.)

## Structure du module

```
/obd2/
  ├── __init__.py          # Fichier d'initialisation du package
  ├── obd_main.py          # Module principal OBD-II
  └── README.md            # Documentation sommaire
```

## Implémentation

Le module est implémenté avec la bibliothèque Python-OBD, qui offre une interface simple pour communiquer avec les dongles OBD-II.

La classe principale `OBDManager` gère :
- La connexion et déconnexion au véhicule
- La récupération des différentes données via les capteurs du véhicule
- La gestion des erreurs et des cas où certains capteurs ne sont pas disponibles

## API REST

Le module est accessible via l'endpoint `/obd2` de l'API REST, qui retourne les données actuelles du véhicule au format JSON.

## Documentation détaillée

Une documentation complète est disponible dans le fichier [docs/README_OBD.md](../docs/README_OBD.md), qui inclut :

- Prérequis matériels et logiciels
- Instructions d'installation et de configuration
- Guide d'utilisation détaillé
- Exemples de code
- Conseils de dépannage
- Ressources supplémentaires

## Tests

Des tests unitaires pour le module se trouvent dans [tests/test_obd.py](../tests/test_obd.py) et peuvent être exécutés avec pytest :

```bash
pytest tests/test_obd.py -v
```
