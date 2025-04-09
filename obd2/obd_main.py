"""
Module OBD-II - Connexion et diagnostique véhicule
Ce module gère la connexion à un dongle OBD-II et récupère les données du véhicule
"""
import os
import time
import json
from dotenv import load_dotenv
import obd
from obd import OBDCommand, Unit
from obd.protocols import ECU
from obd.utils import bytes_to_int

# Charger les variables d'environnement
load_dotenv()

class OBDManager:
    """Gestionnaire de connexion OBD-II"""
    
    def __init__(self):
        """Initialisation du gestionnaire OBD"""
        self.connection = None
        self.connected = False
        self.port = os.getenv('OBD_PORT', '/dev/ttyUSB0')
        self.baudrate = int(os.getenv('OBD_BAUDRATE', 9600))
        self.timeout = int(os.getenv('OBD_TIMEOUT', 30))
    
    def connect(self, port=None, baudrate=None, timeout=None):
        """
        Établit la connexion avec l'interface OBD-II
        
        Args:
            port (str, optional): Port série du dongle OBD
            baudrate (int, optional): Débit en bauds
            timeout (int, optional): Timeout en secondes
            
        Returns:
            bool: True si connexion réussie, False sinon
        """
        # Utiliser les paramètres spécifiés ou les valeurs par défaut
        port = port or self.port
        baudrate = baudrate or self.baudrate
        timeout = timeout or self.timeout
        
        try:
            print(f"Tentative de connexion OBD sur {port} (baudrate: {baudrate})...")
            self.connection = obd.OBD(portstr=port, baudrate=baudrate, timeout=timeout)
            
            if self.connection.status() == obd.OBDStatus.CAR_CONNECTED:
                self.connected = True
                print("Véhicule connecté avec succès!")
                return True
            else:
                status_str = {
                    obd.OBDStatus.NOT_CONNECTED: "Non connecté",
                    obd.OBDStatus.ELM_CONNECTED: "ELM connecté, mais pas de véhicule",
                    obd.OBDStatus.OBD_CONNECTED: "OBD connecté, mais standard inconnu",
                    obd.OBDStatus.CAR_CONNECTED: "Véhicule connecté"
                }.get(self.connection.status(), "Statut inconnu")
                
                print(f"Connexion incomplète: {status_str}")
                return False
                
        except Exception as e:
            print(f"Erreur de connexion OBD: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Ferme la connexion OBD"""
        if self.connection:
            try:
                self.connection.close()
                print("Connexion OBD fermée")
            except Exception as e:
                print(f"Erreur lors de la déconnexion: {str(e)}")
            finally:
                self.connected = False
                self.connection = None
    
    def get_rpm(self):
        """
        Obtient le régime moteur (RPM)
        
        Returns:
            dict: Valeur RPM et statut
        """
        if not self.connected or not self.connection:
            return {"error": "Non connecté au véhicule"}
        
        try:
            cmd = obd.commands.RPM
            response = self.connection.query(cmd)
            
            if response.is_null():
                return {"error": "Impossible de lire le RPM"}
                
            return {
                "success": True,
                "value": response.value.magnitude,  # Valeur numérique de RPM
                "unit": str(response.value.units),  # Unité (généralement "rpm")
                "command": cmd.name,
                "time": time.time()
            }
        except Exception as e:
            return {"error": f"Erreur lors de la lecture RPM: {str(e)}"}
    
    def get_speed(self):
        """
        Obtient la vitesse du véhicule
        
        Returns:
            dict: Vitesse et statut
        """
        if not self.connected or not self.connection:
            return {"error": "Non connecté au véhicule"}
        
        try:
            cmd = obd.commands.SPEED
            response = self.connection.query(cmd)
            
            if response.is_null():
                return {"error": "Impossible de lire la vitesse"}
                
            return {
                "success": True,
                "value": response.value.magnitude,  # Valeur numérique (km/h)
                "unit": str(response.value.units),  # Unité (généralement "kph")
                "command": cmd.name,
                "time": time.time()
            }
        except Exception as e:
            return {"error": f"Erreur lors de la lecture de vitesse: {str(e)}"}
    
    def get_dtc_codes(self):
        """
        Obtient les codes défaut DTC du véhicule
        
        Returns:
            dict: Liste des codes défaut et leur description
        """
        if not self.connected or not self.connection:
            return {"error": "Non connecté au véhicule"}
        
        try:
            cmd = obd.commands.GET_DTC
            response = self.connection.query(cmd)
            
            if response.is_null():
                return {
                    "success": True,
                    "message": "Aucun code défaut détecté",
                    "codes": []
                }
            
            codes = []
            for code in response.value:
                codes.append({
                    "code": code[0],  # Le code DTC (ex: P0123)
                    "description": code[1]  # Description (si disponible)
                })
                
            return {
                "success": True,
                "codes": codes,
                "count": len(codes),
                "time": time.time()
            }
        except Exception as e:
            return {"error": f"Erreur lors de la lecture des codes défaut: {str(e)}"}
    
    def get_basic_info(self):
        """
        Obtient des informations de base sur le véhicule
        
        Returns:
            dict: Informations de base du véhicule
        """
        if not self.connected or not self.connection:
            return {"error": "Non connecté au véhicule"}
        
        try:
            info = {}
            
            # Récupérer les informations disponibles
            commands = [
                ("VIN", obd.commands.VIN),
                ("FUEL_STATUS", obd.commands.FUEL_STATUS),
                ("ENGINE_LOAD", obd.commands.ENGINE_LOAD),
                ("COOLANT_TEMP", obd.commands.COOLANT_TEMP),
                ("INTAKE_TEMP", obd.commands.INTAKE_TEMP),
                ("FUEL_LEVEL", obd.commands.FUEL_LEVEL),
                ("OIL_TEMP", obd.commands.OIL_TEMP),
                ("BAROMETRIC_PRESSURE", obd.commands.BAROMETRIC_PRESSURE)
            ]
            
            for name, cmd in commands:
                if cmd in self.connection.supported_commands:
                    response = self.connection.query(cmd)
                    if not response.is_null():
                        if hasattr(response.value, 'magnitude'):
                            info[name] = {
                                "value": response.value.magnitude,
                                "unit": str(response.value.units)
                            }
                        else:
                            info[name] = {
                                "value": str(response.value)
                            }
            
            return {
                "success": True,
                "info": info,
                "time": time.time()
            }
        except Exception as e:
            return {"error": f"Erreur lors de la récupération des informations: {str(e)}"}

# Exemple d'utilisation
def main():
    """Fonction principale pour tester le module OBD"""
    obd_manager = OBDManager()
    
    # Tenter de se connecter
    connected = obd_manager.connect()
    
    if connected:
        print("Test de lecture RPM...")
        rpm_result = obd_manager.get_rpm()
        print(json.dumps(rpm_result, indent=2))
        
        print("\nTest de lecture vitesse...")
        speed_result = obd_manager.get_speed()
        print(json.dumps(speed_result, indent=2))
        
        print("\nTest de lecture codes défaut...")
        dtc_result = obd_manager.get_dtc_codes()
        print(json.dumps(dtc_result, indent=2))
        
        print("\nTest de lecture info basiques...")
        info_result = obd_manager.get_basic_info()
        print(json.dumps(info_result, indent=2))
        
        # Déconnecter
        obd_manager.disconnect()
    else:
        print("Impossible de se connecter au véhicule. Vérifiez que:")
        print("1. Le dongle OBD-II est correctement branché")
        print("2. Le moteur du véhicule est allumé")
        print("3. Le port configuré est correct (voir .env)")

if __name__ == "__main__":
    main()
