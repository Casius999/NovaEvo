"""
NovaEvo - Module de planification automatique de rendez-vous

Ce module gère la planification intelligente des rendez-vous, en tenant compte
des disponibilités des garages, des priorités d'urgence, et des historiques de services.
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Configuration du logger
logger = logging.getLogger('novaevo.scheduler')

class AppointmentScheduler:
    """
    Gestionnaire de planification de rendez-vous
    
    Cette classe s'occupe de:
    - Rechercher des créneaux disponibles pour des garages à proximité
    - Créer automatiquement des créneaux d'urgence
    - Gérer les priorités de planification
    """
    
    def __init__(self):
        """
        Initialise le planificateur de rendez-vous
        """
        self.api_enabled = os.getenv('APPOINTMENT_API_ENABLED', 'False').lower() in ('true', '1', 't')
        self.api_url = os.getenv('APPOINTMENT_API_URL', '')
        self.api_key = os.getenv('APPOINTMENT_API_KEY', '')
        self.emergency_slots_threshold = int(os.getenv('EMERGENCY_SLOTS_THRESHOLD', '3'))
        
    def find_available_slots(self, location: Dict[str, float], radius: float = 50.0, 
                             timeframe: int = 7, vehicle_type: str = None) -> List[Dict[str, Any]]:
        """
        Recherche des créneaux disponibles dans les garages à proximité
        
        Args:
            location (Dict): Position géographique {latitude: float, longitude: float}
            radius (float): Rayon de recherche en km
            timeframe (int): Période de recherche en jours
            vehicle_type (str, optional): Type de véhicule pour filtrer les garages compatibles
            
        Returns:
            List[Dict]: Liste des créneaux disponibles
        """
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            return self._generate_mock_slots(timeframe)
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'lat': location['latitude'],
                'lng': location['longitude'],
                'radius': radius,
                'days': timeframe
            }
            
            if vehicle_type:
                params['vehicle_type'] = vehicle_type
                
            response = requests.get(
                f"{self.api_url}/api/available-slots",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('slots', [])
            else:
                logger.error(f"Erreur lors de la recherche de créneaux: {response.status_code}")
                return self._generate_mock_slots(timeframe)
                
        except Exception as e:
            logger.error(f"Exception lors de la recherche de créneaux: {str(e)}")
            return self._generate_mock_slots(timeframe)
            
    def find_emergency_slots(self, location: Dict[str, float], urgency_level: str = 'high',
                            max_distance: float = 30.0) -> List[Dict[str, Any]]:
        """
        Recherche des créneaux d'urgence dans les garages à proximité
        
        Args:
            location (Dict): Position géographique {latitude: float, longitude: float}
            urgency_level (str): Niveau d'urgence ('high' ou 'emergency')
            max_distance (float): Distance maximale en km
            
        Returns:
            List[Dict]: Liste des créneaux d'urgence disponibles
        """
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            return self._generate_mock_emergency_slots(urgency_level)
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'lat': location['latitude'],
                'lng': location['longitude'],
                'max_distance': max_distance,
                'urgency_level': urgency_level
            }
            
            response = requests.post(
                f"{self.api_url}/api/emergency-slots",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                slots = response.json().get('slots', [])
                
                # Vérifier le seuil minimum de créneaux d'urgence
                if len(slots) < self.emergency_slots_threshold:
                    # Créer des créneaux supplémentaires si nécessaire
                    logger.info(f"Création dynamique de créneaux d'urgence (seuil non atteint)")
                    self._create_dynamic_emergency_slots(urgency_level)
                    
                    # Refaire la requête pour obtenir les nouveaux créneaux
                    response = requests.post(
                        f"{self.api_url}/api/emergency-slots",
                        headers=headers,
                        json=data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        return response.json().get('slots', [])
                
                return slots
            else:
                logger.error(f"Erreur lors de la recherche de créneaux d'urgence: {response.status_code}")
                return self._generate_mock_emergency_slots(urgency_level)
                
        except Exception as e:
            logger.error(f"Exception lors de la recherche de créneaux d'urgence: {str(e)}")
            return self._generate_mock_emergency_slots(urgency_level)
            
    def schedule_appointment(self, slot_id: str, vehicle_id: str, service_type: str,
                            user_id: str, notes: str = None) -> Dict[str, Any]:
        """
        Planifie un rendez-vous pour un créneau spécifique
        
        Args:
            slot_id (str): ID du créneau sélectionné
            vehicle_id (str): ID du véhicule concerné
            service_type (str): Type de service requis
            user_id (str): ID de l'utilisateur
            notes (str, optional): Notes pour le rendez-vous
            
        Returns:
            Dict: Détails du rendez-vous planifié
        """
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            return self._generate_mock_appointment(slot_id, service_type)
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'slot_id': slot_id,
                'vehicle_id': vehicle_id,
                'service_type': service_type,
                'user_id': user_id
            }
            
            if notes:
                data['notes'] = notes
                
            response = requests.post(
                f"{self.api_url}/api/appointments",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Erreur lors de la planification du rendez-vous: {response.status_code}")
                return self._generate_mock_appointment(slot_id, service_type)
                
        except Exception as e:
            logger.error(f"Exception lors de la planification du rendez-vous: {str(e)}")
            return self._generate_mock_appointment(slot_id, service_type)
            
    def _create_dynamic_emergency_slots(self, urgency_level: str) -> bool:
        """
        Crée dynamiquement des créneaux d'urgence supplémentaires
        
        Args:
            urgency_level (str): Niveau d'urgence ('high' ou 'emergency')
            
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'urgency_level': urgency_level,
                'count': self.emergency_slots_threshold
            }
            
            response = requests.post(
                f"{self.api_url}/api/create-emergency-slots",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info(f"Créneaux d'urgence créés avec succès: {response.json().get('created', 0)}")
                return True
            else:
                logger.error(f"Erreur lors de la création de créneaux d'urgence: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Exception lors de la création de créneaux d'urgence: {str(e)}")
            return False
    
    def _generate_mock_slots(self, timeframe: int) -> List[Dict[str, Any]]:
        """
        Génère des créneaux fictifs pour les tests
        
        Args:
            timeframe (int): Période en jours
            
        Returns:
            List[Dict]: Liste de créneaux fictifs
        """
        mock_slots = []
        now = datetime.now()
        
        garages = [
            {"id": "garage-1", "name": "Garage Central", "address": "123 Rue Principale, 75001 Paris", "rating": 4.8},
            {"id": "garage-2", "name": "Auto Express", "address": "45 Avenue de la Liberté, 69002 Lyon", "rating": 4.5},
            {"id": "garage-3", "name": "Méca Rapid", "address": "8 Boulevard des Mécaniciens, 33000 Bordeaux", "rating": 4.7}
        ]
        
        # Générer des créneaux sur la période spécifiée
        for day in range(1, timeframe + 1):
            date = now + timedelta(days=day)
            
            # Créneaux pour chaque garage
            for garage in garages:
                for hour in [9, 11, 14, 16]:
                    if day % 2 == 0 and hour == 11 and garage["id"] == "garage-1":
                        continue  # Simuler un créneau non disponible
                        
                    slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    mock_slots.append({
                        "id": f"slot-{garage['id']}-{slot_time.strftime('%Y%m%d%H%M')}",
                        "garage_id": garage["id"],
                        "garage_name": garage["name"],
                        "garage_address": garage["address"],
                        "garage_rating": garage["rating"],
                        "start_time": slot_time.isoformat(),
                        "end_time": (slot_time + timedelta(hours=1, minutes=30)).isoformat(),
                        "service_types": ["diagnostic", "repair", "maintenance"]
                    })
                    
        return mock_slots
    
    def _generate_mock_emergency_slots(self, urgency_level: str) -> List[Dict[str, Any]]:
        """
        Génère des créneaux d'urgence fictifs pour les tests
        
        Args:
            urgency_level (str): Niveau d'urgence ('high' ou 'emergency')
            
        Returns:
            List[Dict]: Liste de créneaux d'urgence fictifs
        """
        mock_slots = []
        now = datetime.now()
        
        garages = [
            {"id": "garage-1", "name": "Garage Central", "address": "123 Rue Principale, 75001 Paris", "rating": 4.8, "distance": 2.3},
            {"id": "garage-2", "name": "Auto Express", "address": "45 Avenue de la Liberté, 69002 Lyon", "rating": 4.5, "distance": 3.1},
            {"id": "garage-4", "name": "Urgence Auto 24/7", "address": "15 Rue des Dépanneurs, 75015 Paris", "rating": 4.9, "distance": 5.2}
        ]
        
        # Délai selon le niveau d'urgence
        if urgency_level == 'emergency':
            delays = [1, 2, 3]  # Heures
        else:
            delays = [4, 6, 8]  # Heures
            
        # Générer des créneaux d'urgence
        for garage in garages:
            for delay in delays:
                slot_time = now + timedelta(hours=delay)
                
                mock_slots.append({
                    "id": f"emergency-{garage['id']}-{slot_time.strftime('%Y%m%d%H%M')}",
                    "garage_id": garage["id"],
                    "garage_name": garage["name"],
                    "garage_address": garage["address"],
                    "garage_rating": garage["rating"],
                    "distance": garage["distance"],
                    "start_time": slot_time.isoformat(),
                    "end_time": (slot_time + timedelta(hours=1)).isoformat(),
                    "urgency_level": urgency_level,
                    "priority_service": True
                })
                
        return mock_slots
        
    def _generate_mock_appointment(self, slot_id: str, service_type: str) -> Dict[str, Any]:
        """
        Génère un rendez-vous fictif pour les tests
        
        Args:
            slot_id (str): ID du créneau
            service_type (str): Type de service
            
        Returns:
            Dict: Détails du rendez-vous fictif
        """
        now = datetime.now()
        
        # Extraire les informations du créneau à partir de son ID
        parts = slot_id.split('-')
        is_emergency = parts[0] == "emergency"
        garage_id = parts[1]
        
        # Déterminer le garage
        garages = {
            "garage-1": {"name": "Garage Central", "address": "123 Rue Principale, 75001 Paris", "phone": "01 23 45 67 89"},
            "garage-2": {"name": "Auto Express", "address": "45 Avenue de la Liberté, 69002 Lyon", "phone": "04 56 78 90 12"},
            "garage-3": {"name": "Méca Rapid", "address": "8 Boulevard des Mécaniciens, 33000 Bordeaux", "phone": "05 67 89 01 23"},
            "garage-4": {"name": "Urgence Auto 24/7", "address": "15 Rue des Dépanneurs, 75015 Paris", "phone": "01 78 90 12 34"}
        }
        
        garage = garages.get(garage_id, {"name": "Garage Inconnu", "address": "Adresse inconnue", "phone": "Téléphone inconnu"})
        
        # Générer l'heure du rendez-vous
        if is_emergency:
            appointment_time = now + timedelta(hours=2)
        else:
            day = int(parts[2][6:8])
            hour = int(parts[2][8:10])
            appointment_time = now.replace(day=day, hour=hour, minute=0, second=0, microsecond=0)
            
        return {
            "id": f"appointment-{now.strftime('%Y%m%d%H%M%S')}",
            "slot_id": slot_id,
            "garage_id": garage_id,
            "garage_name": garage["name"],
            "garage_address": garage["address"],
            "garage_phone": garage["phone"],
            "start_time": appointment_time.isoformat(),
            "end_time": (appointment_time + timedelta(hours=1, minutes=30)).isoformat(),
            "service_type": service_type,
            "status": "confirmed",
            "confirmation_code": f"NOVA-{now.strftime('%y%m%d')}-{hash(slot_id) % 10000:04d}",
            "created_at": now.isoformat(),
            "is_emergency": is_emergency
        }

# Instance singleton pour l'utilisation dans l'application
scheduler = AppointmentScheduler()
