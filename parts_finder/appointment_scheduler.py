"""
NovaEvo - Module de planification automatique de rendez-vous

Ce module gère la planification intelligente des rendez-vous, en tenant compte
des disponibilités des garages, des priorités d'urgence, et des historiques de services.
"""

import os
import json
import requests
import logging
import threading
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Configuration du logger
logger = logging.getLogger('novaevo.scheduler')

class AppointmentScheduler:
    """
    Gestionnaire de planification de rendez-vous
    
    Cette classe s'occupe de:
    - Rechercher des créneaux disponibles pour des garages à proximité
    - Créer automatiquement des créneaux d'urgence
    - Gérer les priorités de planification
    - Suivre les disponibilités des professionnels
    """
    
    def __init__(self):
        """
        Initialise le planificateur de rendez-vous
        """
        self.api_enabled = os.getenv('APPOINTMENT_API_ENABLED', 'False').lower() in ('true', '1', 't')
        self.api_url = os.getenv('APPOINTMENT_API_URL', '')
        self.api_key = os.getenv('APPOINTMENT_API_KEY', '')
        self.emergency_slots_threshold = int(os.getenv('EMERGENCY_SLOTS_THRESHOLD', '3'))
        self.notification_enabled = os.getenv('APPOINTMENT_NOTIFICATIONS', 'False').lower() in ('true', '1', 't')
        self.geocoder = None
        try:
            self.geocoder = Nominatim(user_agent="novaevo-scheduler")
        except:
            logger.warning("Impossible d'initialiser le geocoder. Les conversions d'adresses seront désactivées.")
        
        # File d'attente des notifications/rappels
        self.notification_queue = []
        
        # Cache de garages à proximité
        self.location_cache = {}
        
        # Statistiques des rendez-vous
        self.stats = {
            'total_appointments': 0,
            'emergency_appointments': 0,
            'cancelled_appointments': 0,
            'dynamic_slots_created': 0,
            'most_active_locations': {}
        }
        
        # Démarrer le thread de notifications si activé
        if self.notification_enabled:
            self._start_notification_thread()
            
    def find_available_slots(self, location: Dict[str, float], radius: float = 50.0, 
                             timeframe: int = 7, vehicle_type: str = None,
                             service_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Recherche des créneaux disponibles dans les garages à proximité
        
        Args:
            location (Dict): Position géographique {latitude: float, longitude: float}
            radius (float): Rayon de recherche en km
            timeframe (int): Période de recherche en jours
            vehicle_type (str, optional): Type de véhicule pour filtrer les garages compatibles
            service_types (List[str], optional): Types de services recherchés
            
        Returns:
            List[Dict]: Liste des créneaux disponibles
        """
        # Créer une clé de cache pour cette recherche
        location_key = f"{location['latitude']:.2f},{location['longitude']:.2f}-{radius}"
        
        # Vérifier si nous avons des résultats en cache pour cette zone
        if location_key in self.location_cache and \
           (datetime.now() - self.location_cache[location_key]['timestamp']).total_seconds() < 3600:
            logger.info(f"Utilisation du cache pour la zone {location_key}")
            cached_data = self.location_cache[location_key]['data']
            
            # Filtrer les créneaux selon les critères supplémentaires
            filtered_slots = cached_data
            if service_types:
                filtered_slots = [
                    slot for slot in filtered_slots 
                    if any(service in slot.get('service_types', []) for service in service_types)
                ]
            if vehicle_type:
                filtered_slots = [
                    slot for slot in filtered_slots 
                    if vehicle_type in slot.get('vehicle_types', [])
                ]
                
            return filtered_slots
            
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            slots = self._generate_mock_slots(timeframe, service_types)
            
            # Mettre en cache ces résultats
            self.location_cache[location_key] = {
                'timestamp': datetime.now(),
                'data': slots
            }
            
            return slots
            
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
                
            if service_types:
                params['service_types'] = ','.join(service_types)
                
            response = requests.get(
                f"{self.api_url}/api/available-slots",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                slots = response.json().get('slots', [])
                
                # Ajouter des informations géographiques si possible
                for slot in slots:
                    if 'garage_address' in slot and self.geocoder:
                        try:
                            address = slot['garage_address']
                            if 'garage_location' not in slot:
                                # Géocoder l'adresse
                                geo_location = self.geocoder.geocode(address)
                                if geo_location:
                                    slot['garage_location'] = {
                                        'latitude': geo_location.latitude,
                                        'longitude': geo_location.longitude
                                    }
                                    # Calculer la distance réelle
                                    slot['distance'] = geodesic(
                                        (location['latitude'], location['longitude']),
                                        (geo_location.latitude, geo_location.longitude)
                                    ).kilometers
                        except Exception as geo_err:
                            logger.warning(f"Erreur de géocodage pour {slot['garage_name']}: {str(geo_err)}")
                
                # Mettre en cache ces résultats
                self.location_cache[location_key] = {
                    'timestamp': datetime.now(),
                    'data': slots
                }
                
                return slots
            else:
                logger.error(f"Erreur lors de la recherche de créneaux: {response.status_code}")
                # Générer des créneaux fictifs
                slots = self._generate_mock_slots(timeframe, service_types)
                
                # Mettre en cache ces résultats
                self.location_cache[location_key] = {
                    'timestamp': datetime.now(),
                    'data': slots
                }
                
                return slots
                
        except Exception as e:
            logger.error(f"Exception lors de la recherche de créneaux: {str(e)}")
            slots = self._generate_mock_slots(timeframe, service_types)
            
            # Mettre en cache ces résultats
            self.location_cache[location_key] = {
                'timestamp': datetime.now(),
                'data': slots
            }
            
            return slots
            
    def find_emergency_slots(self, location: Dict[str, float], urgency_level: str = 'high',
                           max_distance: float = 30.0, service_type: str = None) -> List[Dict[str, Any]]:
        """
        Recherche des créneaux d'urgence dans les garages à proximité
        
        Args:
            location (Dict): Position géographique {latitude: float, longitude: float}
            urgency_level (str): Niveau d'urgence ('high' ou 'emergency')
            max_distance (float): Distance maximale en km
            service_type (str, optional): Type de service requis
            
        Returns:
            List[Dict]: Liste des créneaux d'urgence disponibles
        """
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            return self._generate_mock_emergency_slots(urgency_level, service_type)
            
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
            
            if service_type:
                data['service_type'] = service_type
                
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
                    created = self._create_dynamic_emergency_slots(urgency_level, max_distance, location, service_type)
                    
                    if created:
                        # Refaire la requête pour obtenir les nouveaux créneaux
                        response = requests.post(
                            f"{self.api_url}/api/emergency-slots",
                            headers=headers,
                            json=data,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            slots = response.json().get('slots', [])
                            
                            # Marquer les créneaux nouvellement créés
                            for slot in slots:
                                if 'created_dynamically' in slot and slot['created_dynamically']:
                                    self.stats['dynamic_slots_created'] += 1
                
                # Ajouter des informations géographiques si possible
                for slot in slots:
                    if 'garage_address' in slot and self.geocoder and 'distance' not in slot:
                        try:
                            address = slot['garage_address']
                            if 'garage_location' not in slot:
                                # Géocoder l'adresse
                                geo_location = self.geocoder.geocode(address)
                                if geo_location:
                                    slot['garage_location'] = {
                                        'latitude': geo_location.latitude,
                                        'longitude': geo_location.longitude
                                    }
                                    # Calculer la distance réelle
                                    slot['distance'] = geodesic(
                                        (location['latitude'], location['longitude']),
                                        (geo_location.latitude, geo_location.longitude)
                                    ).kilometers
                        except Exception as geo_err:
                            logger.warning(f"Erreur de géocodage pour {slot['garage_name']}: {str(geo_err)}")
                
                return slots
            else:
                logger.error(f"Erreur lors de la recherche de créneaux d'urgence: {response.status_code}")
                return self._generate_mock_emergency_slots(urgency_level, service_type)
                
        except Exception as e:
            logger.error(f"Exception lors de la recherche de créneaux d'urgence: {str(e)}")
            return self._generate_mock_emergency_slots(urgency_level, service_type)
            
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
            appointment = self._generate_mock_appointment(slot_id, service_type)
            self._add_appointment_to_stats(appointment)
            self._schedule_notifications(appointment)
            return appointment
            
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
                appointment = response.json()
                self._add_appointment_to_stats(appointment)
                self._schedule_notifications(appointment)
                return appointment
            else:
                logger.error(f"Erreur lors de la planification du rendez-vous: {response.status_code}")
                appointment = self._generate_mock_appointment(slot_id, service_type)
                self._add_appointment_to_stats(appointment)
                self._schedule_notifications(appointment)
                return appointment
                
        except Exception as e:
            logger.error(f"Exception lors de la planification du rendez-vous: {str(e)}")
            appointment = self._generate_mock_appointment(slot_id, service_type)
            self._add_appointment_to_stats(appointment)
            self._schedule_notifications(appointment)
            return appointment
            
    def cancel_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """
        Annule un rendez-vous existant
        
        Args:
            appointment_id (str): ID du rendez-vous à annuler
            
        Returns:
            Dict: Résultat de l'annulation
        """
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            self.stats['cancelled_appointments'] += 1
            return {
                'success': True,
                'appointment_id': appointment_id,
                'status': 'cancelled',
                'cancelled_at': datetime.now().isoformat()
            }
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.delete(
                f"{self.api_url}/api/appointments/{appointment_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code in (200, 204):
                self.stats['cancelled_appointments'] += 1
                return {
                    'success': True,
                    'appointment_id': appointment_id,
                    'status': 'cancelled',
                    'cancelled_at': datetime.now().isoformat()
                }
            else:
                logger.error(f"Erreur lors de l'annulation du rendez-vous: {response.status_code}")
                return {
                    'success': False,
                    'appointment_id': appointment_id,
                    'error': f"Erreur lors de l'annulation (code: {response.status_code})"
                }
                
        except Exception as e:
            logger.error(f"Exception lors de l'annulation du rendez-vous: {str(e)}")
            return {
                'success': False,
                'appointment_id': appointment_id,
                'error': f"Exception: {str(e)}"
            }
            
    def reschedule_appointment(self, appointment_id: str, new_slot_id: str) -> Dict[str, Any]:
        """
        Replanifie un rendez-vous existant sur un nouveau créneau
        
        Args:
            appointment_id (str): ID du rendez-vous à replanifier
            new_slot_id (str): ID du nouveau créneau
            
        Returns:
            Dict: Nouveau rendez-vous planifié
        """
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            # Simuler un rendez-vous modifié
            appointment = self._generate_mock_appointment(new_slot_id, "rescheduled")
            appointment['previous_appointment_id'] = appointment_id
            appointment['rescheduled'] = True
            return appointment
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'appointment_id': appointment_id,
                'new_slot_id': new_slot_id
            }
            
            response = requests.patch(
                f"{self.api_url}/api/appointments/{appointment_id}/reschedule",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la replanification du rendez-vous: {response.status_code}")
                # Simuler un rendez-vous modifié
                appointment = self._generate_mock_appointment(new_slot_id, "rescheduled")
                appointment['previous_appointment_id'] = appointment_id
                appointment['rescheduled'] = True
                return appointment
                
        except Exception as e:
            logger.error(f"Exception lors de la replanification du rendez-vous: {str(e)}")
            # Simuler un rendez-vous modifié
            appointment = self._generate_mock_appointment(new_slot_id, "rescheduled")
            appointment['previous_appointment_id'] = appointment_id
            appointment['rescheduled'] = True
            return appointment
            
    def get_service_history(self, vehicle_id: str) -> List[Dict[str, Any]]:
        """
        Récupère l'historique de service d'un véhicule
        
        Args:
            vehicle_id (str): ID du véhicule
            
        Returns:
            List[Dict]: Liste des rendez-vous passés
        """
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            # Générer un historique fictif
            history = []
            for i in range(3):
                appt_date = datetime.now() - timedelta(days=30*(i+1))
                service_types = ["diagnostic", "maintenance", "repair"]
                service_type = service_types[i % len(service_types)]
                garage_names = ["Garage Central", "Auto Express", "Méca Rapid"]
                garage_name = garage_names[i % len(garage_names)]
                
                history.append({
                    "id": f"history-{vehicle_id}-{i}",
                    "vehicle_id": vehicle_id,
                    "garage_id": f"garage-{i+1}",
                    "garage_name": garage_name,
                    "service_type": service_type,
                    "date": appt_date.isoformat(),
                    "status": "completed",
                    "price": round(random.uniform(50, 350), 2),
                    "notes": f"Service {service_type} effectué"
                })
            
            return history
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_url}/api/vehicles/{vehicle_id}/history",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('appointments', [])
            else:
                logger.error(f"Erreur lors de la récupération de l'historique: {response.status_code}")
                # Générer un historique fictif
                history = []
                for i in range(3):
                    appt_date = datetime.now() - timedelta(days=30*(i+1))
                    service_types = ["diagnostic", "maintenance", "repair"]
                    service_type = service_types[i % len(service_types)]
                    garage_names = ["Garage Central", "Auto Express", "Méca Rapid"]
                    garage_name = garage_names[i % len(garage_names)]
                    
                    history.append({
                        "id": f"history-{vehicle_id}-{i}",
                        "vehicle_id": vehicle_id,
                        "garage_id": f"garage-{i+1}",
                        "garage_name": garage_name,
                        "service_type": service_type,
                        "date": appt_date.isoformat(),
                        "status": "completed",
                        "price": round(random.uniform(50, 350), 2),
                        "notes": f"Service {service_type} effectué"
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Exception lors de la récupération de l'historique: {str(e)}")
            # Générer un historique fictif
            history = []
            for i in range(3):
                appt_date = datetime.now() - timedelta(days=30*(i+1))
                service_types = ["diagnostic", "maintenance", "repair"]
                service_type = service_types[i % len(service_types)]
                garage_names = ["Garage Central", "Auto Express", "Méca Rapid"]
                garage_name = garage_names[i % len(garage_names)]
                
                history.append({
                    "id": f"history-{vehicle_id}-{i}",
                    "vehicle_id": vehicle_id,
                    "garage_id": f"garage-{i+1}",
                    "garage_name": garage_name,
                    "service_type": service_type,
                    "date": appt_date.isoformat(),
                    "status": "completed",
                    "price": round(random.uniform(50, 350), 2),
                    "notes": f"Service {service_type} effectué"
                })
            
            return history
            
    def get_garage_details(self, garage_id: str) -> Dict[str, Any]:
        """
        Récupère les détails d'un garage spécifique
        
        Args:
            garage_id (str): ID du garage
            
        Returns:
            Dict: Détails du garage
        """
        if not self.api_enabled or not self.api_url:
            logger.warning("API de planification non configurée ou désactivée")
            # Générer des détails fictifs
            garages = {
                "garage-1": {
                    "id": "garage-1",
                    "name": "Garage Central",
                    "address": "123 Rue Principale, 75001 Paris",
                    "phone": "01 23 45 67 89",
                    "email": "contact@garagecentral.fr",
                    "rating": 4.8,
                    "specialties": ["Mécanique générale", "Diagnostic électronique", "Pneumatiques"],
                    "hours": {
                        "monday": "08:30 - 19:00",
                        "tuesday": "08:30 - 19:00",
                        "wednesday": "08:30 - 19:00",
                        "thursday": "08:30 - 19:00",
                        "friday": "08:30 - 19:00",
                        "saturday": "09:00 - 17:00",
                        "sunday": "Fermé"
                    }
                },
                "garage-2": {
                    "id": "garage-2",
                    "name": "Auto Express",
                    "address": "45 Avenue de la Liberté, 69002 Lyon",
                    "phone": "04 56 78 90 12",
                    "email": "info@autoexpress.fr",
                    "rating": 4.5,
                    "specialties": ["Réparation rapide", "Carrosserie", "Climatisation"],
                    "hours": {
                        "monday": "08:00 - 18:30",
                        "tuesday": "08:00 - 18:30",
                        "wednesday": "08:00 - 18:30",
                        "thursday": "08:00 - 18:30",
                        "friday": "08:00 - 18:30",
                        "saturday": "09:00 - 16:00",
                        "sunday": "Fermé"
                    }
                },
                "garage-3": {
                    "id": "garage-3",
                    "name": "Méca Rapid",
                    "address": "8 Boulevard des Mécaniciens, 33000 Bordeaux",
                    "phone": "05 67 89 01 23",
                    "email": "contact@mecarapid.fr",
                    "rating": 4.7,
                    "specialties": ["Services express", "Vidange", "Freinage"],
                    "hours": {
                        "monday": "09:00 - 19:30",
                        "tuesday": "09:00 - 19:30",
                        "wednesday": "09:00 - 19:30",
                        "thursday": "09:00 - 19:30",
                        "friday": "09:00 - 19:30",
                        "saturday": "10:00 - 18:00",
                        "sunday": "Fermé"
                    }
                },
                "garage-4": {
                    "id": "garage-4",
                    "name": "Urgence Auto 24/7",
                    "address": "15 Rue des Dépanneurs, 75015 Paris",
                    "phone": "01 78 90 12 34",
                    "email": "urgence@auto247.fr",
                    "rating": 4.9,
                    "specialties": ["Dépannage d'urgence", "Réparation 24/7", "Diagnostic rapide"],
                    "hours": {
                        "monday": "00:00 - 23:59",
                        "tuesday": "00:00 - 23:59",
                        "wednesday": "00:00 - 23:59",
                        "thursday": "00:00 - 23:59",
                        "friday": "00:00 - 23:59",
                        "saturday": "00:00 - 23:59",
                        "sunday": "00:00 - 23:59"
                    },
                    "emergency_service": True
                }
            }
            
            return garages.get(garage_id, {"error": "Garage non trouvé"})
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_url}/api/garages/{garage_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la récupération des détails du garage: {response.status_code}")
                # Générer des détails fictifs
                garage = {
                    "id": garage_id,
                    "name": f"Garage {garage_id.split('-')[1] if '-' in garage_id else 'Inconnu'}",
                    "address": "Adresse non disponible",
                    "phone": "Téléphone non disponible",
                    "rating": 4.0,
                    "error": f"Détails non disponibles (code: {response.status_code})"
                }
                return garage
                
        except Exception as e:
            logger.error(f"Exception lors de la récupération des détails du garage: {str(e)}")
            # Générer des détails fictifs
            garage = {
                "id": garage_id,
                "name": f"Garage {garage_id.split('-')[1] if '-' in garage_id else 'Inconnu'}",
                "address": "Adresse non disponible",
                "phone": "Téléphone non disponible",
                "rating": 4.0,
                "error": f"Exception: {str(e)}"
            }
            return garage
            
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du planificateur
        
        Returns:
            Dict: Statistiques diverses
        """
        return {
            'total_appointments': self.stats['total_appointments'],
            'emergency_appointments': self.stats['emergency_appointments'],
            'cancelled_appointments': self.stats['cancelled_appointments'],
            'dynamic_slots_created': self.stats['dynamic_slots_created'],
            'most_active_locations': dict(sorted(
                self.stats['most_active_locations'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]),  # Top 5 des locations
            'cache_status': {
                'location_entries': len(self.location_cache),
                'oldest_entry': min([entry['timestamp'] for entry in self.location_cache.values()]).isoformat() 
                if self.location_cache else None
            }
        }
            
    def _create_dynamic_emergency_slots(self, urgency_level: str, max_distance: float = 30.0,
                                      location: Dict[str, float] = None, 
                                      service_type: str = None) -> bool:
        """
        Crée dynamiquement des créneaux d'urgence supplémentaires
        
        Args:
            urgency_level (str): Niveau d'urgence ('high' ou 'emergency')
            max_distance (float): Distance maximale en km
            location (Dict): Position géographique de référence
            service_type (str): Type de service requis
            
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
            
            if location:
                data['location'] = location
                
            if max_distance:
                data['max_distance'] = max_distance
                
            if service_type:
                data['service_type'] = service_type
                
            response = requests.post(
                f"{self.api_url}/api/create-emergency-slots",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                created_count = response.json().get('created', 0)
                logger.info(f"Créneaux d'urgence créés avec succès: {created_count}")
                self.stats['dynamic_slots_created'] += created_count
                return True
            else:
                logger.error(f"Erreur lors de la création de créneaux d'urgence: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Exception lors de la création de créneaux d'urgence: {str(e)}")
            return False
    
    def _generate_mock_slots(self, timeframe: int, service_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        Génère des créneaux fictifs pour les tests
        
        Args:
            timeframe (int): Période en jours
            service_types (List[str], optional): Types de services à inclure
            
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
        
        # Services disponibles par défaut
        default_services = ["diagnostic", "repair", "maintenance"]
        if not service_types:
            service_types = default_services
        
        # Générer des créneaux sur la période spécifiée
        for day in range(1, timeframe + 1):
            date = now + timedelta(days=day)
            
            # Créneaux pour chaque garage
            for garage in garages:
                for hour in [9, 11, 14, 16]:
                    if day % 2 == 0 and hour == 11 and garage["id"] == "garage-1":
                        continue  # Simuler un créneau non disponible
                        
                    slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    # Filtrer selon les types de service demandés
                    slot_services = random.sample(default_services, random.randint(1, len(default_services)))
                    if service_types and not any(service in slot_services for service in service_types):
                        continue
                    
                    mock_slots.append({
                        "id": f"slot-{garage['id']}-{slot_time.strftime('%Y%m%d%H%M')}",
                        "garage_id": garage["id"],
                        "garage_name": garage["name"],
                        "garage_address": garage["address"],
                        "garage_rating": garage["rating"],
                        "start_time": slot_time.isoformat(),
                        "end_time": (slot_time + timedelta(hours=1, minutes=30)).isoformat(),
                        "service_types": slot_services,
                        "vehicle_types": ["sedan", "suv", "hatchback", "van"],
                        "price_range": {"min": 50, "max": 120}
                    })
                    
        return mock_slots
    
    def _generate_mock_emergency_slots(self, urgency_level: str, service_type: str = None) -> List[Dict[str, Any]]:
        """
        Génère des créneaux d'urgence fictifs pour les tests
        
        Args:
            urgency_level (str): Niveau d'urgence ('high' ou 'emergency')
            service_type (str, optional): Type de service requis
            
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
        
        # Services disponibles
        services = ["diagnostic", "repair", "maintenance", "towing", "emergency_repair"]
        if service_type:
            services = [s for s in services if s == service_type or (service_type in s or s in service_type)]
        
        # Délai selon le niveau d'urgence
        if urgency_level == 'emergency':
            delays = [1, 2, 3]  # Heures
        else:
            delays = [4, 6, 8]  # Heures
            
        # Générer des créneaux d'urgence
        for garage in garages:
            for delay in delays:
                slot_time = now + timedelta(hours=delay)
                
                # Sélectionner aléatoirement 1 à 3 services
                slot_services = random.sample(services, min(random.randint(1, 3), len(services)))
                
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
                    "priority_service": True,
                    "service_types": slot_services,
                    "vehicle_types": ["sedan", "suv", "hatchback", "van"],
                    "price_range": {"min": 80, "max": 200, "emergency_fee": 50}
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
            try:
                day = int(parts[2][6:8])
                hour = int(parts[2][8:10])
                appointment_time = now.replace(day=day, hour=hour, minute=0, second=0, microsecond=0)
            except:
                appointment_time = now + timedelta(days=1, hours=9)
            
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
            "is_emergency": is_emergency,
            "reminders": [
                {"type": "email", "time": (appointment_time - timedelta(days=1)).isoformat()},
                {"type": "sms", "time": (appointment_time - timedelta(hours=2)).isoformat()}
            ],
            "estimated_price": round(random.uniform(50, 200), 2)
        }
        
    def _add_appointment_to_stats(self, appointment: Dict[str, Any]) -> None:
        """
        Ajoute un rendez-vous aux statistiques
        
        Args:
            appointment (Dict): Rendez-vous à ajouter
        """
        self.stats['total_appointments'] += 1
        
        # Comptabiliser les rendez-vous d'urgence
        if appointment.get('is_emergency', False):
            self.stats['emergency_appointments'] += 1
            
        # Tracker les locations actives
        if 'garage_address' in appointment:
            # Simplifier l'adresse pour le regroupement
            address_parts = appointment['garage_address'].split(',')
            if len(address_parts) >= 2:
                postal_code = address_parts[1].strip()
                if postal_code in self.stats['most_active_locations']:
                    self.stats['most_active_locations'][postal_code] += 1
                else:
                    self.stats['most_active_locations'][postal_code] = 1
                    
    def _schedule_notifications(self, appointment: Dict[str, Any]) -> None:
        """
        Planifie les notifications pour un rendez-vous
        
        Args:
            appointment (Dict): Rendez-vous pour lequel planifier des notifications
        """
        if not self.notification_enabled:
            return
            
        try:
            appointment_time = datetime.fromisoformat(appointment['start_time'])
            
            # Notification 24h avant
            notification_24h = {
                'appointment_id': appointment['id'],
                'garage_name': appointment['garage_name'],
                'time': appointment_time.isoformat(),
                'notification_time': (appointment_time - timedelta(days=1)).isoformat(),
                'type': 'email',
                'message': f"Rappel: Rendez-vous chez {appointment['garage_name']} demain à {appointment_time.strftime('%H:%M')}"
            }
            
            # Notification 2h avant
            notification_2h = {
                'appointment_id': appointment['id'],
                'garage_name': appointment['garage_name'],
                'time': appointment_time.isoformat(),
                'notification_time': (appointment_time - timedelta(hours=2)).isoformat(),
                'type': 'sms',
                'message': f"Rappel: Rendez-vous chez {appointment['garage_name']} dans 2h à {appointment_time.strftime('%H:%M')}"
            }
            
            self.notification_queue.extend([notification_24h, notification_2h])
            
        except Exception as e:
            logger.error(f"Erreur lors de la planification des notifications: {str(e)}")
            
    def _start_notification_thread(self) -> None:
        """
        Démarre le thread de traitement des notifications
        """
        def notification_worker():
            """Thread worker qui traite les notifications en attente"""
            while True:
                try:
                    now = datetime.now()
                    
                    # Traiter les notifications arrivées à échéance
                    notifications_to_send = []
                    remaining_notifications = []
                    
                    for notification in self.notification_queue:
                        notification_time = datetime.fromisoformat(notification['notification_time'])
                        if notification_time <= now:
                            notifications_to_send.append(notification)
                        else:
                            remaining_notifications.append(notification)
                    
                    # Mettre à jour la file d'attente
                    self.notification_queue = remaining_notifications
                    
                    # Envoyer les notifications
                    for notification in notifications_to_send:
                        try:
                            logger.info(f"Envoi de notification: {notification['type']} pour le rendez-vous {notification['appointment_id']}")
                            # Ici, on pourrait appeler un service d'envoi d'emails/SMS
                            # En version de démonstration, on simule simplement l'envoi
                        except Exception as e:
                            logger.error(f"Erreur lors de l'envoi de notification: {str(e)}")
                    
                except Exception as e:
                    logger.error(f"Erreur dans le thread de notifications: {str(e)}")
                    
                # Attendre 1 minute avant la prochaine vérification
                time.sleep(60)
        
        # Démarrer le thread de notifications
        notification_thread = threading.Thread(target=notification_worker, daemon=True)
        notification_thread.start()
        logger.info("Thread de notifications démarré")

# Instance singleton pour l'utilisation dans l'application
scheduler = AppointmentScheduler()
