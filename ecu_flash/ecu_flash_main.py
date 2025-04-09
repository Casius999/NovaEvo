"""
Module ECU Flash - Reprogrammation et configuration ECU
Ce module permet de lire, interpréter et modifier les paramètres de l'ECU (cartographie moteur)
"""

import os
import json
import time
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ecu_flash')

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
        (Simulation pour l'instant)
        
        Returns:
            dict: Résultat de la connexion
        """
        if not self.device_id:
            return {
                "success": False,
                "message": "ID de périphérique ECU non configuré dans .env"
            }
            
        # Simulation de connexion
        logger.info(f"Tentative de connexion à l'ECU: {self.device_id} via {self.protocol}")
        time.sleep(1)  # Simuler un délai de connexion
        
        self.connected = True
        self.connection = {"device_id": self.device_id, "protocol": self.protocol}
        
        return {
            "success": True,
            "message": f"Connecté à l'ECU (simulation)",
            "device_id": self.device_id,
            "protocol": self.protocol
        }
    
    def flash_ecu(self):
        """
        Flash l'ECU avec la configuration actuelle
        (Simulation pour l'instant)
        
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
    
    def read_ecu(self):
        """
        Lit la configuration actuelle de l'ECU
        (Simulation pour l'instant)
        
        Returns:
            dict: Données lues de l'ECU
        """
        if not self.connected:
            return {"error": "Non connecté à l'ECU"}
        
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
            
    else:
        print(f"Fichier de test non trouvé: {test_config}")
        print("Créez un dossier 'test_configs' avec un fichier JSON de cartographie pour tester.")

if __name__ == "__main__":
    main()
