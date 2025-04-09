# Module ECU Flash/Tuning

## 1. Présentation

Le module **ECU Flash/Tuning** est un composant essentiel de l'application Assistant Auto Ultime permettant de lire, modifier et flasher (reprogrammer) l'ECU (Electronic Control Unit) d'un véhicule. Contrairement aux solutions simulées, ce module utilise des outils professionnels de flashage pour une véritable reprogrammation des paramètres du moteur.

### 1.1. Objectif

L'objectif principal de ce module est de permettre aux utilisateurs de:
- Lire la configuration actuelle de l'ECU
- Modifier des paramètres spécifiques de performance (injection, boost, allumage, etc.)
- Appliquer ces modifications en flashant l'ECU
- Garantir une sécurité maximale avec validation des paramètres et mécanismes de rollback

### 1.2. Précautions importantes

⚠️ **ATTENTION** ⚠️

La modification des paramètres de l'ECU peut:
- Affecter la performance et la fiabilité du véhicule
- Avoir un impact sur la consommation de carburant
- Potentiellement endommager le moteur si les paramètres dépassent les limites sécuritaires
- Annuler la garantie du constructeur
- Rendre le véhicule non conforme aux réglementations environnementales

Utilisez ce module uniquement si vous comprenez pleinement les conséquences potentielles.

## 2. Configuration requise

### 2.1. Matériel

Pour utiliser le module ECU Flash avec une connexion réelle:

- **Interface de flashage compatible**: Tactrix Openport, MPPS, Alientech K-Tag, ou équivalent
- **Câble OBD-II** connectant l'interface à la prise de diagnostic du véhicule
- **Alimentation stable** pour éviter toute coupure pendant le flashage

### 2.2. Logiciel

- Bibliothèque professionnelle `ecu_flash_lib` installée
- Pilotes spécifiques pour l'interface de flashage
- Fichiers de configuration de l'ECU pour votre véhicule spécifique

### 2.3. Configuration dans le fichier .env

```
ECU_DEVICE_ID=<identifiant de votre interface de flashage>
ECU_PROTOCOL=CAN
```

## 3. Architecture et conception

Le module est conçu avec une architecture à plusieurs niveaux:

1. **Couche d'abstraction hardware**: Gère la communication avec l'interface de flashage réel
2. **Couche de validation**: Vérifie que les paramètres restent dans des limites sécuritaires
3. **Couche de sauvegarde**: Assure que la configuration originale peut être restaurée
4. **Couche API**: Fournit des endpoints REST pour l'interface utilisateur

### 3.1. Modèle de données

Le module utilise un modèle objet basé sur Pydantic:

- `ECUConfiguration`: Configuration complète de l'ECU
- `ECUParameter`: Paramètre individuel avec limites
- `TuningMap`: Cartographie multi-dimensionnelle (injection, allumage...)
- `MapData`: Données de la cartographie
- `MapAxis`: Définition des axes de la cartographie

## 4. Utilisation

### 4.1. API REST

Le module expose plusieurs endpoints REST:

#### POST /ecu_flash

Flash l'ECU avec les paramètres de tuning spécifiés.

**Request**:
```json
{
  "cartographie_injection": 105,
  "boost_turbo": 1.1
}
```

**Response (succès)**:
```json
{
  "status": "success",
  "message": "Flash de l'ECU réussi.",
  "new_configuration": {
    "cartographie_injection": 105,
    "boost_turbo": 1.1
  }
}
```

**Response (échec)**:
```json
{
  "status": "error",
  "message": "Valeur '1.3' pour 'boost_turbo' hors limite (min: 0.8, max: 1.2)."
}
```

#### POST /ecu_flash/connect

Établit une connexion avec l'ECU.

**Request**: Pas de corps requis

**Response**:
```json
{
  "success": true,
  "message": "Connecté à l'ECU",
  "device_id": "OP-23456",
  "protocol": "CAN",
  "interface": "Tactrix Openport 2.0"
}
```

#### GET /ecu_flash/read

Lit la configuration actuelle de l'ECU.

**Response**:
```json
{
  "success": true,
  "message": "Lecture de l'ECU réussie",
  "vehicle": {
    "make": "Volkswagen",
    "model": "Golf GTI",
    "year": "2023"
  },
  "parameters_count": 24,
  "maps_count": 8
}
```

#### GET /ecu_flash/parameters

Récupère les limites sécurisées pour tous les paramètres.

**Response**:
```json
{
  "status": "success",
  "parameters": {
    "cartographie_injection": {"default": 100, "min": 90, "max": 115},
    "boost_turbo": {"default": 1.0, "min": 0.8, "max": 1.2},
    "avance_allumage": {"default": 10, "min": 5, "max": 15}
  }
}
```

### 4.2. Utilisation via Python

```python
from ecu_flash.ecu_flash_main import flash_ecu, ECUFlashManager

# Flashage direct avec des paramètres spécifiques
params = {
    "cartographie_injection": 105,
    "boost_turbo": 1.1
}
result = flash_ecu(params)
print(result)

# Utilisation plus avancée avec le gestionnaire
manager = ECUFlashManager()
manager.connect_ecu()
manager.load_config_file("ma_config.json")
manager.set_parameter("boost_turbo", 1.1)
manager.flash_ecu()
```

## 5. Connexion à l'outil de flashage réel

### 5.1. Configuration de l'interface Tactrix Openport

1. Branchez l'interface Tactrix Openport sur la prise OBD-II du véhicule
2. Assurez-vous que le contact est mis mais que le moteur est éteint
3. Configurez l'ID de l'appareil dans le fichier `.env`
4. Testez la connexion avec l'endpoint `/ecu_flash/connect`

### 5.2. Diagnostics de connexion

Si la connexion échoue:

1. Vérifiez que l'interface est correctement branchée
2. Assurez-vous que les pilotes sont installés
3. Vérifiez que le contact est mis
4. Consultez les logs pour plus de détails (`logs/ecu_flash.log`)

## 6. Sécurité et rollback

### 6.1. Limites sécurisées

Le module utilise des limites strictes pour chaque paramètre:

```python
SECURE_LIMITS = {
    "cartographie_injection": {"default": 100, "min": 90, "max": 115},
    "boost_turbo": {"default": 1.0, "min": 0.8, "max": 1.2},
    "avance_allumage": {"default": 10, "min": 5, "max": 15},
    "limiteur_regime": {"default": 6500, "min": 6000, "max": 7500},
    # etc.
}
```

Ces limites ont été définies pour offrir un gain de performance tout en restant dans des plages sécuritaires pour le moteur.

### 6.2. Mécanisme de sauvegarde et rollback

Avant toute modification, le module:
1. Sauvegarde la configuration actuelle de l'ECU
2. Conserve cette sauvegarde dans un fichier `ecu_backup.json`
3. En cas d'erreur pendant le flashage, effectue automatiquement un rollback

### 6.3. Rollback manuel

Pour effectuer un rollback manuel:

1. Localisez le fichier de sauvegarde (`ecu_backup.json`)
2. Utilisez la fonction `ECUFlashManager().load_config_file("ecu_backup.json")`
3. Flashez à nouveau l'ECU avec cette configuration

## 7. Tests et validation

Le module inclut des tests unitaires complets:

```bash
# Exécuter les tests spécifiques au module ECU Flash
python -m pytest tests/test_ecu_flash.py -v

# Exécuter les tests d'intégration
python -m pytest tests/test_integration.py::TestECUFlashIntegration -v
```

## 8. Dépannage

### 8.1. Problèmes courants

| Problème | Cause possible | Solution |
|----------|----------------|----------|
| `ImportError: No module named 'ecu_flash_lib'` | Bibliothèque manquante | Installez la bibliothèque avec `pip install ecu_flash_lib` |
| `Error: Device not found` | Interface non détectée | Vérifiez la connexion USB et les pilotes |
| `Validation error: Parameter out of range` | Paramètre hors limites | Utilisez une valeur dans les limites spécifiées |
| `Error during flash: Connection lost` | Perte de connexion | Assurez une alimentation stable pendant le flashage |

### 8.2. Logs

Les logs détaillés se trouvent dans `logs/ecu_flash.log`.

## 9. Exemples d'utilisation

### 9.1. Augmentation modérée des performances

```json
{
  "cartographie_injection": 105,
  "boost_turbo": 1.1,
  "avance_allumage": 12
}
```

### 9.2. Configuration économique

```json
{
  "cartographie_injection": 95,
  "boost_turbo": 0.9,
  "avance_allumage": 8
}
```

## 10. Références et ressources

- [Documentation de la bibliothèque ecu_flash_lib](https://example.com/ecu_flash_lib)
- [Guide Tactrix Openport](https://example.com/tactrix)
- [Bonnes pratiques pour le flashage ECU](https://example.com/ecu_best_practices)

---

**Avertissement**: La modification de l'ECU doit être réalisée par des professionnels ou des utilisateurs avancés comprenant les risques associés. L'utilisation de ce module est à vos propres risques.
