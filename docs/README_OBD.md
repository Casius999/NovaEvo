# Module OBD-II - Documentation

## Description

Le module OBD-II de l'Assistant Auto Ultime permet de se connecter à un véhicule via un adaptateur OBD-II (On-Board Diagnostics II) et de récupérer des données en temps réel comme le régime moteur, la vitesse et les codes d'erreur.

## Prérequis

### Matériel nécessaire

- Un adaptateur OBD-II compatible (ELM327, OBDLink MX+, etc.)
- Un véhicule équipé du système OBD-II (obligatoire pour tous les véhicules essence depuis 2001 et diesel depuis 2004 en Europe)

### Logiciels et bibliothèques

- Python 3.7+
- Bibliothèque Python-OBD (`pip install obd`)
- Bibliothèque PySerial (installée automatiquement avec Python-OBD)

## Installation

1. Installez les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

2. Configurez les variables d'environnement en créant un fichier `.env` à la racine du projet :

```
OBD_PORT=/dev/ttyUSB0  # Linux
# ou
OBD_PORT=COM3          # Windows
OBD_BAUDRATE=9600      # Débit en bauds 
OBD_TIMEOUT=30         # Timeout en secondes
```

## Connexion de l'adaptateur

1. **Localisez le port OBD-II** de votre véhicule - généralement situé sous le tableau de bord, côté conducteur
2. **Branchez l'adaptateur OBD-II** sur ce port
3. Si votre adaptateur est Bluetooth, **associez-le** avec votre ordinateur
4. **Mettez le contact** ou démarrez le moteur avant de vous connecter

## Utilisation

### Utilisation via l'API

Le module OBD-II est accessible via l'endpoint REST `/obd2` de l'API. Vous pouvez effectuer une requête GET pour obtenir les données du véhicule :

```bash
curl http://localhost:5000/obd2
```

Réponse typique :

```json
{
  "RPM": 1200,
  "Speed": 45,
  "DTC": "Aucun code détecté"
}
```

### Utilisation en tant que module Python

Vous pouvez également utiliser le module directement dans votre code Python :

```python
from obd2.obd_main import OBDManager

# Créer une instance du gestionnaire OBD
obd_manager = OBDManager()

# Se connecter au véhicule
if obd_manager.connect():
    # Récupérer le régime moteur
    rpm_data = obd_manager.get_rpm()
    print(f"Régime moteur : {rpm_data['value']} {rpm_data['unit']}")
    
    # Récupérer la vitesse
    speed_data = obd_manager.get_speed()
    print(f"Vitesse : {speed_data['value']} {speed_data['unit']}")
    
    # Récupérer les codes d'erreur
    dtc_data = obd_manager.get_dtc_codes()
    if dtc_data["codes"]:
        print("Codes d'erreur :")
        for code in dtc_data["codes"]:
            print(f" - {code['code']} : {code['description']}")
    else:
        print("Aucun code d'erreur détecté")
    
    # Récupérer les informations de base du véhicule
    info_data = obd_manager.get_basic_info()
    if "info" in info_data:
        print("Informations de base du véhicule :")
        for key, value in info_data["info"].items():
            print(f" - {key} : {value}")
    
    # Toujours fermer la connexion
    obd_manager.disconnect()
else:
    print("Connexion au véhicule impossible")
```

### Exécution du script autonome

Vous pouvez aussi exécuter le module directement pour tester la connexion :

```bash
python -m obd2.obd_main
```

## Fonctionnalités

Le module OBD-II permet de :

1. **Se connecter** à l'adaptateur OBD-II et au véhicule
2. Récupérer le **régime moteur** (RPM)
3. Récupérer la **vitesse** actuelle du véhicule
4. Lire les **codes d'erreur** (DTC - Diagnostic Trouble Codes)
5. Obtenir diverses **informations de base** du véhicule (selon disponibilité) :
   - Numéro VIN
   - Température du liquide de refroidissement
   - Température d'huile
   - Niveau de carburant
   - Charge moteur
   - Température d'admission
   - Pression barométrique

## Dépannage

### Problèmes courants

1. **Impossible de se connecter à l'adaptateur**
   - Vérifiez que l'adaptateur est correctement branché
   - Vérifiez que le port configuré est correct (vérifier dans le gestionnaire de périphériques sous Windows)
   - Testez un autre port USB si vous utilisez un adaptateur USB
   - Assurez-vous que l'adaptateur est alimenté (LED allumée)

2. **Adaptateur connecté mais pas de données du véhicule**
   - Vérifiez que le contact est mis ou que le moteur tourne
   - Certains véhicules nécessitent que le moteur soit démarré
   - Certains adaptateurs ELM327 bas de gamme peuvent être incompatibles avec certains véhicules

3. **Données manquantes ou incomplètes**
   - Tous les véhicules ne supportent pas tous les capteurs/paramètres
   - Les véhicules plus anciens offrent généralement moins de données
   - Certains constructeurs utilisent des protocoles propriétaires nécessitant des adaptateurs spécifiques

## Développement et extension

### Structure des fichiers

```
/obd2/
  ├── __init__.py          # Fichier d'initialisation du package
  ├── obd_main.py          # Module principal OBD-II
  └── README.md            # Documentation spécifique au module
```

### Ajout de nouvelles commandes

Pour ajouter une nouvelle commande OBD-II, créez une nouvelle méthode dans la classe `OBDManager` :

```python
def get_new_parameter(self):
    """
    Obtient un nouveau paramètre du véhicule
    
    Returns:
        dict: Paramètre et statut
    """
    if not self.connected or not self.connection:
        return {"error": "Non connecté au véhicule"}
    
    try:
        cmd = obd.commands.YOUR_COMMAND
        response = self.connection.query(cmd)
        
        if response.is_null():
            return {"error": "Impossible de lire le paramètre"}
            
        return {
            "success": True,
            "value": response.value.magnitude,
            "unit": str(response.value.units),
            "command": cmd.name,
            "time": time.time()
        }
    except Exception as e:
        return {"error": f"Erreur lors de la lecture: {str(e)}"}
```

## Ressources

- [Documentation officielle Python-OBD](https://python-obd.readthedocs.io/en/latest/)
- [Liste des codes OBD-II standard](https://en.wikipedia.org/wiki/OBD-II_PIDs)
- [Codes d'erreur DTC](https://www.obd-codes.com/trouble_codes/)

## Licence

Ce module est distribué sous la même licence que le projet Assistant Auto Ultime.
