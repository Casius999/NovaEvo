# Module ECU Flash / Tuning

Ce module permet la lecture, la modification et le flashage (reprogrammation) de l'ECU (Electronic Control Unit) d'un véhicule.

## Caractéristiques principales

- Connexion directe à l'interface de flashage ECU (Tactrix Openport ou équivalent)
- Lecture des paramètres actuels de l'ECU
- Modification sécurisée des paramètres (cartographie injection, avance allumage, etc.)
- Validation des paramètres selon des limites prédéfinies
- Sauvegarde automatique de la configuration originale
- Système de rollback en cas d'erreur

## Documentation détaillée

Pour une documentation complète sur l'utilisation du module, consultez [README_ECU_FLASH.md](../docs/README_ECU_FLASH.md) dans le dossier `/docs`.

## Exemple d'utilisation rapide

```python
from ecu_flash.ecu_flash_main import flash_ecu

# Paramètres de performance
tuning_params = {
    "cartographie_injection": 105,  # 5% d'augmentation
    "boost_turbo": 1.1              # 10% d'augmentation
}

# Flasher l'ECU
result = flash_ecu(tuning_params)
print(result)
```

## Utilisez avec précaution

⚠️ **AVERTISSEMENT** ⚠️

La modification des paramètres de l'ECU peut affecter les performances du véhicule, provoquer des dommages au moteur si les ajustements sont trop extrêmes, et annuler la garantie du fabricant. Utilisez ce module uniquement si vous comprenez pleinement les risques associés.

## Dépendances

- Python 3.10+
- Bibliothèque professionnelle `ecu_flash_lib`
- Interface matérielle de flashage compatible
- Pilotes USB pour l'interface de flashage

Consultez le fichier [requirements.txt](../requirements.txt) pour les dépendances Python spécifiques.
