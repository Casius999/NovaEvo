"""
Module ECU Flash - Reprogrammation et configuration ECU
Ce module permet de lire, interpréter et modifier les paramètres de l'ECU (cartographie moteur)
en utilisant une bibliothèque professionnelle de flashage réel.
"""

import os
import json
import time
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any, Tuple

# Importer la bibliothèque professionnelle de flashage
try:
    from ecu_flash_lib import ECUFlashController
except ImportError:
    logging.warning("La bibliothèque ecu_flash_lib n'est pas disponible. Certaines fonctionnalités seront limitées.")

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ecu_flash')

# Limites sécurisées pour les paramètres de tuning
SECURE_LIMITS = {
    "cartographie_injection": {"default": 100, "min": 90, "max": 115},
    "boost_turbo": {"default": 1.0, "min": 0.8, "max": 1.2},
    "avance_allumage": {"default": 10, "min": 5, "max": 15},
    "limiteur_regime": {"default": 6500, "min": 6000, "max": 7500},
    "richesse_melange": {"default": 1.0, "min": 0.9, "max": 1.1},
    "temperature_admission": {"default": 50, "min": 45, "max": 65},
    "pression_carburant": {"default": 3.5, "min": 3.0, "max": 4.0}
}

# Modèles de données pour la cartographie
class MapAxis(BaseModel):
    """Définition d'un axe de cartographie"""
    name: str
    units: str
    values: List[float]
    description: Optional[str] = None

class MapData(BaseModel):
    """Données d'une cartographie 2D ou 3D"""
    values: List[List[float]]  # Format: [row][column]
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default_value: Optional[float] = None

class TuningMap(BaseModel):
    """Cartographie complète avec axes et données"""
    name: str
    description: str
    x_axis: MapAxis
    y_axis: Optional[MapAxis] = None  # Optionnel pour cartographies 1D
    data: MapData
    units: str
    type: str = "2D"  # "1D", "2D" ou "3D"
    category: str  # "ignition", "fuel", "boost", etc.
    editable: bool = True
    
class ECUParameter(BaseModel):
    """Paramètre individuel de l'ECU"""
    name: str
    value: Union[float, int, bool, str]
    description: str
    units: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    editable: bool = True
    category: str

class ECUConfiguration(BaseModel):
    """Configuration complète de l'ECU"""
    vehicle: Dict[str, str]
    parameters: Dict[str, ECUParameter]
    maps: Dict[str, TuningMap]
    metadata: Dict[str, Any]

def validate_tuning_parameters(tuning_parameters: dict) -> Tuple[bool, str]:
    """
    Vérifie que chaque paramètre est dans sa plage sécurisée
    
    Args:
        tuning_parameters (dict): Paramètres de tuning à valider
        
    Returns:
        Tuple[bool, str]: Résultat de la validation (succès/échec, message)
    """
    for param, value in tuning_parameters.items():
        if param in SECURE_LIMITS:
            limits = SECURE_LIMITS[param]
            if not (limits["min"] <= value <= limits["max"]):
                return False, f"Valeur '{value}' pour '{param}' hors limite (min: {limits['min']}, max: {limits['max']})."
        else:
            return False, f"Paramètre inconnu: {param}."
    return True, ""

def backup_current_configuration(controller: 'ECUFlashController', backup_file="ecu_backup.json"):
    """
    Lit et sauvegarde la configuration actuelle de l'ECU via l'API du flash tool
    
    Args:
        controller (ECUFlashController): Contrôleur de flashage ECU
        backup_file (str): Chemin du fichier de sauvegarde
        
    Returns:
        dict: Configuration actuelle de l'ECU
    """
    # Récupère la configuration actuelle de l'ECU via l'API réelle
    logger.info("Sauvegarde de la configuration actuelle de l'ECU")
    current_config = controller.read_configuration()
    
    # Sauvegarde dans un fichier
    try:
        os.makedirs(os.path.dirname(os.path.abspath(backup_file)), exist_ok=True)
        with open(backup_file, "w") as f:
            json.dump(current_config, f, indent=2)
        logger.info(f"Configuration sauvegardée dans {backup_file}")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier de backup: {str(e)}")
    
    return current_config

def flash_ecu(tuning_parameters: dict) -> dict:
    """
    Flashe l'ECU avec les paramètres fournis en utilisant l'outil de flashage réel
    
    Args:
        tuning_parameters (dict): Paramètres de tuning à appliquer
        
    Returns:
        dict: Résultat de l'opération de flashage
    """
    # Valider les paramètres
    is_valid, message = validate_tuning_parameters(tuning_parameters)
    if not is_valid:
        logger.error(f"Validation des paramètres échouée: {message}")
        return {"status": "error", "message": message}
    
    logger.info(f"Flashage de l'ECU avec les paramètres: {tuning_parameters}")
    
    try:
        # Initialiser le contrôleur de flashage ECU (outil de flashage réel)
        controller = ECUFlashController()
        logger.info("Connecté à l'outil de flashage")
        
        # Sauvegarder la configuration actuelle
        backup = backup_current_configuration(controller)
        logger.info("Configuration actuelle sauvegardée")
        
        try:
            # Appliquer les nouveaux réglages via la méthode réelle de flashage
            logger.info("Application des nouveaux paramètres...")
            result = controller.flash_configuration(tuning_parameters)
            
            if result.get('success'):
                logger.info("Flash de l'ECU réussi")
                return {
                    "status": "success",
                    "message": "Flash de l'ECU réussi.",
                    "new_configuration": tuning_parameters
                }
            else:
                # En cas d'échec, effectuer un rollback
                logger.warning(f"Flash de l'ECU échoué: {result.get('message', 'Raison inconnue')}")
                logger.info("Tentative de rollback...")
                controller.restore_configuration(backup)
                logger.info("Rollback effectué avec succès")
                return {
                    "status": "error",
                    "message": f"Flash de l'ECU échoué: {result.get('message', 'Raison inconnue')}. Rollback effectué."
                }
        except Exception as e:
            # En cas d'exception, tenter un rollback et renvoyer l'erreur
            logger.error(f"Exception lors du flash: {str(e)}")
            logger.info("Tentative de rollback...")
            try:
                controller.restore_configuration(backup)
                logger.info("Rollback effectué avec succès")
            except Exception as rollback_error:
                logger.error(f"Erreur lors du rollback: {str(rollback_error)}")
                return {
                    "status": "error", 
                    "message": f"Erreur critique: Flash échoué ({str(e)}) et rollback échoué ({str(rollback_error)})"
                }
            
            return {
                "status": "error", 
                "message": f"Erreur lors du flash: {str(e)}. Rollback effectué."
            }
    except ImportError:
        logger.error("Bibliothèque de flashage ECU non disponible")
        return {
            "status": "error",
            "message": "Bibliothèque de flashage ECU (ecu_flash_lib) non disponible. Veuillez installer le logiciel requis."
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du contrôleur de flashage: {str(e)}")
        return {
            "status": "error",
            "message": f"Erreur lors de la connexion à l'outil de flashage ECU: {str(e)}"
        }

class ECUFlashManager:
    """Gestionnaire de reprogrammation ECU"""
    
    def __init__(self):
        """Initialisation du gestionnaire de flash ECU"""
        self.device_id = os.getenv('ECU_DEVICE_ID')
        self.protocol = os.getenv('ECU_PROTOCOL', 'CAN')
        self.current_config = None
        self.modified = False
        self.connection = None
        self.connected = False
        self.flash_controller = None
        
        # Tenter d'initialiser le contrôleur de flash réel si disponible
        try:
            self.init_real_flash_controller()
        except ImportError:
            logger.warning("Bibliothèque ecu_flash_lib non disponible. Mode de simulation activé.")
        except Exception as e:
            logger.warning(f"Erreur lors de l'initialisation du contrôleur de flashage réel: {str(e)}")
    
    def init_real_flash_controller(self):
        """Initialise le contrôleur de flashage ECU réel"""
        try:
            self.flash_controller = ECUFlashController()
            logger.info("Contrôleur de flashage ECU réel initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du contrôleur de flashage: {str(e)}")
            raise
    
    def load_config_file(self, file_path):
        """
        Charge un fichier de configuration ECU
        
        Args:
            file_path (str): Chemin vers le fichier JSON de configuration
            
        Returns:
            dict: Configuration chargée ou erreur
        """
        try:
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            
            # Valider avec Pydantic
            self.current_config = ECUConfiguration(**config_data)
            logger.info(f"Configuration chargée: {len(self.current_config.parameters)} paramètres, "
                       f"{len(self.current_config.maps)} cartographies")
            self.modified = False
            
            return {
                "success": True,
                "message": "Configuration chargée avec succès",
                "vehicle": self.current_config.vehicle,
                "parameters_count": len(self.current_config.parameters),
                "maps_count": len(self.current_config.maps)
            }
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
            return {"error": f"Erreur lors du chargement du fichier: {str(e)}"}
    
    def save_config_file(self, file_path):
        """
        Sauvegarde la configuration actuelle dans un fichier
        
        Args:
            file_path (str): Chemin de destination
            
        Returns:
            dict: Résultat de la sauvegarde
        """
        if not self.current_config:
            return {"error": "Aucune configuration chargée"}
        
        try:
            # Conversion en dictionnaire
            config_dict = self.current_config.model_dump()
            
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            self.modified = False
            logger.info(f"Configuration sauvegardée: {file_path}")
            
            return {
                "success": True,
                "message": "Configuration sauvegardée avec succès",
                "path": file_path
            }
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return {"error": f"Erreur lors de la sauvegarde du fichier: {str(e)}"}
    
    def get_parameter(self, param_name):
        """
        Récupère un paramètre de la configuration actuelle
        
        Args:
            param_name (str): Nom du paramètre
            
        Returns:
            dict: Paramètre ou erreur
        """
        if not self.current_config:
            return {"error": "Aucune configuration chargée"}
        
        if param_name not in self.current_config.parameters:
            return {"error": f"Paramètre non trouvé: {param_name}"}
        
        param = self.current_config.parameters[param_name]
        return {
            "success": True,
            "parameter": {
                "name": param.name,
                "value": param.value,
                "description": param.description,
                "units": param.units,
                "min_value": param.min_value,
                "max_value": param.max_value,
                "editable": param.editable,
                "category": param.category
            }
        }
    
    def set_parameter(self, param_name, value):
        """
        Modifie la valeur d'un paramètre
        
        Args:
            param_name (str): Nom du paramètre
            value: Nouvelle valeur
            
        Returns:
            dict: Résultat de la modification
        """
        if not self.current_config:
            return {"error": "Aucune configuration chargée"}
        
        if param_name not in self.current_config.parameters:
            return {"error": f"Paramètre non trouvé: {param_name}"}
        
        param = self.current_config.parameters[param_name]
        
        if not param.editable:
            return {"error": f"Le paramètre {param_name} n'est pas modifiable"}
        
        # Vérifier les limites si définies
        if param.min_value is not None and value < param.min_value:
            return {"error": f"Valeur trop basse. Minimum: {param.min_value}"}
            
        if param.max_value is not None and value > param.max_value:
            return {"error": f"Valeur trop élevée. Maximum: {param.max_value}"}
        
        # Stocker l'ancienne valeur pour le rapport
        old_value = param.value
        
        # Mettre à jour
        try:
            param.value = value
            self.current_config.parameters[param_name] = param
            self.modified = True
            
            logger.info(f"Paramètre modifié: {param_name} de {old_value} à {value}")
            
            return {
                "success": True,
                "message": f"Paramètre {param_name} modifié",
                "old_value": old_value,
                "new_value": value,
                "units": param.units
            }
        except Exception as e:
            logger.error(f"Erreur lors de la modification du paramètre: {str(e)}")
            return {"error": f"Erreur lors de la modification: {str(e)}"}
    
    def get_map(self, map_name):
        """
        Récupère une cartographie
        
        Args:
            map_name (str): Nom de la cartographie
            
        Returns:
            dict: Cartographie ou erreur
        """
        if not self.current_config:
            return {"error": "Aucune configuration chargée"}
        
        if map_name not in self.current_config.maps:
            return {"error": f"Cartographie non trouvée: {map_name}"}
        
        tuning_map = self.current_config.maps[map_name]
        
        # Convertir en format de réponse simplifié
        map_data = {
            "name": tuning_map.name,
            "description": tuning_map.description,
            "type": tuning_map.type,
            "category": tuning_map.category,
            "units": tuning_map.units,
            "editable": tuning_map.editable,
            "x_axis": {
                "name": tuning_map.x_axis.name,
                "units": tuning_map.x_axis.units,
                "values": tuning_map.x_axis.values
            },
            "data": tuning_map.data.values
        }
        
        # Ajouter l'axe Y si présent (cartographie 2D+)
        if tuning_map.y_axis:
            map_data["y_axis"] = {
                "name": tuning_map.y_axis.name,
                "units": tuning_map.y_axis.units,
                "values": tuning_map.y_axis.values
            }
        
        return {
            "success": True,
            "map": map_data
        }
    
    def modify_map_cell(self, map_name, x_index, y_index, value):
        """
        Modifie une cellule d'une cartographie
        
        Args:
            map_name (str): Nom de la cartographie
            x_index (int): Index sur l'axe X
            y_index (int): Index sur l'axe Y (peut être 0 pour carte 1D)
            value (float): Nouvelle valeur
            
        Returns:
            dict: Résultat de la modification
        """
        if not self.current_config:
            return {"error": "Aucune configuration chargée"}
        
        if map_name not in self.current_config.maps:
            return {"error": f"Cartographie non trouvée: {map_name}"}
        
        tuning_map = self.current_config.maps[map_name]
        
        if not tuning_map.editable:
            return {"error": f"La cartographie {map_name} n'est pas modifiable"}
        
        # Vérifier les limites des indices
        if y_index >= len(tuning_map.data.values):
            return {"error": f"Index Y hors limites: {y_index}"}
            
        if x_index >= len(tuning_map.data.values[y_index]):
            return {"error": f"Index X hors limites: {x_index}"}
        
        # Vérifier les limites de valeur
        if tuning_map.data.min_value is not None and value < tuning_map.data.min_value:
            return {"error": f"Valeur trop basse. Minimum: {tuning_map.data.min_value}"}
            
        if tuning_map.data.max_value is not None and value > tuning_map.data.max_value:
            return {"error": f"Valeur trop élevée. Maximum: {tuning_map.data.max_value}"}
        
        # Stocker l'ancienne valeur pour le rapport
        old_value = tuning_map.data.values[y_index][x_index]
        
        # Mettre à jour
        try:
            tuning_map.data.values[y_index][x_index] = value
            self.modified = True
            
            logger.info(f"Cartographie {map_name} modifiée: cellule [{y_index}][{x_index}] "
                       f"de {old_value} à {value}")
            
            return {
                "success": True,
                "message": f"Cellule modifiée dans {map_name}",
                "coordinates": {"x": x_index, "y": y_index},
                "old_value": old_value,
                "new_value": value,
                "units": tuning_map.units
            }
        except Exception as e:
            logger.error(f"Erreur lors de la modification de la cartographie: {str(e)}")
            return {"error": f"Erreur lors de la modification: {str(e)}"}
    
    def connect_ecu(self):
        """
        Établit une connexion avec l'ECU
        
        Returns:
            dict: Résultat de la connexion
        """
        if not self.device_id:
            return {
                "success": False,
                "message": "ID de périphérique ECU non configuré dans .env"
            }
        
        try:
            # Tenter d'utiliser le contrôleur réel si disponible
            if self.flash_controller:
                logger.info(f"Connexion réelle à l'ECU: {self.device_id} via {self.protocol}")
                connection_result = self.flash_controller.connect(device_id=self.device_id, protocol=self.protocol)
                
                if connection_result.get('success'):
                    self.connected = True
                    self.connection = {
                        "device_id": self.device_id, 
                        "protocol": self.protocol,
                        "interface": connection_result.get('interface', 'Unknown')
                    }
                    
                    logger.info(f"Connecté à l'ECU via {self.connection.get('interface')}")
                    
                    return {
                        "success": True,
                        "message": f"Connecté à l'ECU",
                        "device_id": self.device_id,
                        "protocol": self.protocol,
                        "interface": self.connection.get('interface')
                    }
                else:
                    logger.error(f"Échec de connexion à l'ECU: {connection_result.get('message', 'Raison inconnue')}")
                    return {
                        "success": False,
                        "message": f"Échec de connexion à l'ECU: {connection_result.get('message', 'Raison inconnue')}"
                    }
            else:
                # Simulation de connexion
                logger.info(f"Simulation de connexion à l'ECU: {self.device_id} via {self.protocol}")
                time.sleep(1)  # Simuler un délai de connexion
                
                self.connected = True
                self.connection = {"device_id": self.device_id, "protocol": self.protocol}
                
                logger.info("Connecté à l'ECU (simulation)")
                
                return {
                    "success": True,
                    "message": f"Connecté à l'ECU (simulation)",
                    "device_id": self.device_id,
                    "protocol": self.protocol
                }
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à l'ECU: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur lors de la connexion à l'ECU: {str(e)}"
            }
    
    def flash_ecu_with_custom_params(self, tuning_parameters):
        """
        Flash l'ECU avec des paramètres personnalisés
        
        Args:
            tuning_parameters (dict): Paramètres de tuning
            
        Returns:
            dict: Résultat du flash
        """
        if not self.connected:
            return {"error": "Non connecté à l'ECU"}
        
        # Utiliser la fonction indépendante pour le flashage réel
        try:
            if self.flash_controller:
                logger.info(f"Utilisation du contrôleur réel pour flasher l'ECU avec {tuning_parameters}")
                return flash_ecu(tuning_parameters)
            else:
                # Simulation de flash
                logger.info(f"Simulation de flash avec paramètres: {tuning_parameters}")
                is_valid, message = validate_tuning_parameters(tuning_parameters)
                
                if not is_valid:
                    return {"status": "error", "message": message}
                
                time.sleep(2)  # Simuler un délai de flash
                
                return {
                    "status": "success",
                    "message": "ECU flashée avec succès (simulation)",
                    "timestamp": time.time(),
                    "new_configuration": tuning_parameters
                }
        except Exception as e:
            logger.error(f"Erreur lors du flash ECU: {str(e)}")
            return {"status": "error", "message": f"Erreur lors du flash ECU: {str(e)}"}
    
    def flash_ecu(self):
        """
        Flash l'ECU avec la configuration actuelle
        
        Returns:
            dict: Résultat du flash
        """
        if not self.connected:
            return {"error": "Non connecté à l'ECU"}
            
        if not self.current_config:
            return {"error": "Aucune configuration chargée"}
            
        if not self.modified:
            return {
                "success": True,
                "message": "Aucune modification à flasher"
            }
        
        try:
            if self.flash_controller:
                # Convertir la configuration Pydantic en dictionnaire pour le flashage
                logger.info("Conversion de la configuration pour flashage réel")
                config_dict = {}
                
                # Extraire les paramètres à flasher
                for param_name, param in self.current_config.parameters.items():
                    if param.editable:  # Ne flasher que les paramètres modifiables
                        config_dict[param_name] = param.value
                
                # Flashage réel
                logger.info(f"Flashage réel de l'ECU avec {len(config_dict)} paramètres")
                flash_result = self.flash_controller.flash_configuration(config_dict)
                
                if flash_result.get('success'):
                    self.modified = False
                    logger.info("Flash réel réussi")
                    
                    return {
                        "success": True,
                        "message": "ECU flashée avec succès",
                        "timestamp": time.time(),
                        "vehicle": self.current_config.vehicle,
                        "parameters_flashed": len(config_dict)
                    }
                else:
                    logger.error(f"Échec du flash réel: {flash_result.get('message', 'Raison inconnue')}")
                    return {
                        "success": False,
                        "message": f"Échec du flash: {flash_result.get('message', 'Raison inconnue')}"
                    }
            else:
                # Simulation de flash
                logger.info("Démarrage du flash ECU (simulation)")
                time.sleep(2)  # Simuler un délai de flash
                
                self.modified = False
                
                return {
                    "success": True,
                    "message": "ECU flashée avec succès (simulation)",
                    "timestamp": time.time(),
                    "vehicle": self.current_config.vehicle
                }
        except Exception as e:
            logger.error(f"Erreur lors du flash ECU: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur lors du flash ECU: {str(e)}"
            }
    
    def read_ecu(self):
        """
        Lit la configuration actuelle de l'ECU
        
        Returns:
            dict: Données lues de l'ECU
        """
        if not self.connected:
            return {"error": "Non connecté à l'ECU"}
        
        try:
            if self.flash_controller:
                # Lecture réelle de l'ECU
                logger.info("Lecture réelle de l'ECU")
                
                # Utiliser l'API réelle pour lire la configuration
                read_result = self.flash_controller.read_configuration()
                
                if read_result.get('success'):
                    # Convertir la configuration lue en modèle Pydantic
                    config_data = read_result.get('configuration', {})
                    logger.info(f"Configuration lue: {len(config_data)} paramètres")
                    
                    # Mettre à jour la configuration interne
                    # Note: ceci est simplifié, dans un cas réel il faudrait convertir
                    # la structure retournée par l'API en notre modèle Pydantic
                    self.current_config = config_data
                    self.modified = False
                    
                    return {
                        "success": True,
                        "message": "Lecture de l'ECU réussie",
                        "parameters_count": len(config_data)
                    }
                else:
                    logger.error(f"Échec de lecture de l'ECU: {read_result.get('message', 'Raison inconnue')}")
                    return {
                        "success": False,
                        "message": f"Échec de lecture de l'ECU: {read_result.get('message', 'Raison inconnue')}"
                    }
            else:
                # Simulation de lecture
                logger.info("Lecture de l'ECU (simulation)")
                time.sleep(1.5)  # Simuler un délai de lecture
                
                if self.current_config:
                    return {
                        "success": True,
                        "message": "Lecture de l'ECU réussie (simulation)",
                        "vehicle": self.current_config.vehicle,
                        "parameters_count": len(self.current_config.parameters),
                        "maps_count": len(self.current_config.maps)
                    }
                else:
                    return {
                        "success": True,
                        "message": "Lecture de l'ECU réussie, mais aucune donnée (simulation)",
                        "vehicle": {"make": "Simulation", "model": "Test", "year": "2025"}
                    }
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de l'ECU: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur lors de la lecture de l'ECU: {str(e)}"
            }

# Exemple d'utilisation
def main():
    """Fonction principale pour tester le module ECU Flash"""
    ecu_manager = ECUFlashManager()
    
    # Exemple de test avec un fichier de configuration JSON
    test_config = "test_configs/ecu_map_sample.json"
    
    if os.path.exists(test_config):
        print(f"Chargement de la configuration: {test_config}")
        result = ecu_manager.load_config_file(test_config)
        print(json.dumps(result, indent=2))
        
        if "success" in result:
            # Tester la récupération d'un paramètre
            param_result = ecu_manager.get_parameter("idle_rpm")
            if "success" in param_result:
                print(f"\nParamètre: {param_result['parameter']['name']}")
                print(f"Valeur: {param_result['parameter']['value']} {param_result['parameter']['units']}")
            
            # Tester la récupération d'une cartographie
            map_result = ecu_manager.get_map("ignition_advance")
            if "success" in map_result:
                print(f"\nCartographie: {map_result['map']['name']}")
                print(f"Type: {map_result['map']['type']}")
                print(f"Unités: {map_result['map']['units']}")
                
            # Tester simulation de flash
            ecu_manager.connect_ecu()
            ecu_manager.modified = True  # Simuler des modifications
            flash_result = ecu_manager.flash_ecu()
            print(f"\nRésultat du flash: {flash_result['message']}")
            
            # Tester le flash avec des paramètres personnalisés
            tuning_params = {
                "cartographie_injection": 105,
                "boost_turbo": 1.1
            }
            custom_flash_result = ecu_manager.flash_ecu_with_custom_params(tuning_params)
            print(f"\nRésultat du flash personnalisé: {custom_flash_result['message']}")
            
    else:
        print(f"Fichier de test non trouvé: {test_config}")
        print("Créez un dossier 'test_configs' avec un fichier JSON de cartographie pour tester.")

if __name__ == "__main__":
    main()
