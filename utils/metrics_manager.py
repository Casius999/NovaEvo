"""
NovaEvo - Gestionnaire de Métriques de Performance

Ce module gère la collecte, l'enregistrement et l'analyse des métriques de performance
de l'application, permettant d'optimiser l'expérience utilisateur et de suivre
les performances des différents composants.
"""

import os
import json
import time
import logging
import threading
import statistics
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from collections import defaultdict

# Configuration du logger
logger = logging.getLogger('novaevo.metrics')

class MetricsManager:
    """
    Gestionnaire de métriques de performance
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de métriques
        """
        self.enabled = os.getenv('METRICS_ENABLED', 'True').lower() in ('true', '1', 't')
        self.metrics_dir = os.getenv('METRICS_DIR', 'data/metrics')
        self.retention_days = int(os.getenv('METRICS_RETENTION_DAYS', '90'))
        
        # Créer le répertoire des métriques si nécessaire
        if self.enabled:
            os.makedirs(self.metrics_dir, exist_ok=True)
            
        # Initialiser les compteurs de métriques
        self.counters = defaultdict(int)
        self.timers = {}
        self.gauges = {}
        self.histograms = defaultdict(list)
        
        # État du nettoyage automatique
        self.auto_cleanup_running = False
        
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Incrémente un compteur de métrique
        
        Args:
            name (str): Nom de la métrique
            value (int): Valeur à ajouter (défaut: 1)
            tags (Dict[str, str], optional): Tags associés à la métrique
        """
        if not self.enabled:
            return
            
        metric_key = self._format_metric_key(name, tags)
        self.counters[metric_key] += value
        
        # Enregistrer les métriques toutes les 100 incrémentations
        if self.counters[metric_key] % 100 == 0:
            self._save_counters()
            
    def start_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Démarre un chronomètre pour mesurer le temps d'exécution
        
        Args:
            name (str): Nom de la métrique
            tags (Dict[str, str], optional): Tags associés à la métrique
        """
        if not self.enabled:
            return
            
        metric_key = self._format_metric_key(name, tags)
        self.timers[metric_key] = time.time()
        
    def stop_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """
        Arrête un chronomètre et enregistre la durée
        
        Args:
            name (str): Nom de la métrique
            tags (Dict[str, str], optional): Tags associés à la métrique
            
        Returns:
            float: Durée en secondes, ou -1 si le chronomètre n'existe pas
        """
        if not self.enabled:
            return -1
            
        metric_key = self._format_metric_key(name, tags)
        
        if metric_key not in self.timers:
            logger.warning(f"Tentative d'arrêt d'un chronomètre inexistant: {metric_key}")
            return -1
            
        duration = time.time() - self.timers[metric_key]
        self.histograms[f"{metric_key}.duration"].append(duration)
        
        # Supprimer le chronomètre
        del self.timers[metric_key]
        
        # Enregistrer les métriques périodiquement
        if len(self.histograms[f"{metric_key}.duration"]) % 50 == 0:
            self._save_histograms()
            
        return duration
        
    def set_gauge(self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> None:
        """
        Définit la valeur d'une jauge
        
        Args:
            name (str): Nom de la métrique
            value (Union[int, float]): Valeur à définir
            tags (Dict[str, str], optional): Tags associés à la métrique
        """
        if not self.enabled:
            return
            
        metric_key = self._format_metric_key(name, tags)
        self.gauges[metric_key] = value
        
        # Enregistrer les jauges à chaque modification
        self._save_gauges()
        
    def record_value(self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> None:
        """
        Enregistre une valeur dans un histogramme
        
        Args:
            name (str): Nom de la métrique
            value (Union[int, float]): Valeur à enregistrer
            tags (Dict[str, str], optional): Tags associés à la métrique
        """
        if not self.enabled:
            return
            
        metric_key = self._format_metric_key(name, tags)
        self.histograms[metric_key].append(value)
        
        # Enregistrer les histogrammes périodiquement
        if len(self.histograms[metric_key]) % 50 == 0:
            self._save_histograms()
            
    def log_event(self, event_type: str, description: str, data: Optional[Dict[str, Any]] = None,
                 severity: str = 'info', tags: Optional[Dict[str, str]] = None) -> None:
        """
        Enregistre un événement avec des données associées
        
        Args:
            event_type (str): Type d'événement
            description (str): Description de l'événement
            data (Dict[str, Any], optional): Données associées à l'événement
            severity (str): Niveau de sévérité (info, warning, error, critical)
            tags (Dict[str, str], optional): Tags associés à l'événement
        """
        if not self.enabled:
            return
            
        # Créer l'objet événement
        event = {
            'event_type': event_type,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'tags': tags or {}
        }
        
        if data:
            event['data'] = data
            
        # Enregistrer l'événement dans un fichier dédié
        self._save_event(event)
        
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """
        Récupère la valeur d'un compteur
        
        Args:
            name (str): Nom de la métrique
            tags (Dict[str, str], optional): Tags associés à la métrique
            
        Returns:
            int: Valeur du compteur
        """
        if not self.enabled:
            return 0
            
        metric_key = self._format_metric_key(name, tags)
        return self.counters.get(metric_key, 0)
        
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> Union[int, float, None]:
        """
        Récupère la valeur d'une jauge
        
        Args:
            name (str): Nom de la métrique
            tags (Dict[str, str], optional): Tags associés à la métrique
            
        Returns:
            Union[int, float, None]: Valeur de la jauge ou None si elle n'existe pas
        """
        if not self.enabled:
            return None
            
        metric_key = self._format_metric_key(name, tags)
        return self.gauges.get(metric_key)
        
    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Récupère les statistiques d'un histogramme
        
        Args:
            name (str): Nom de la métrique
            tags (Dict[str, str], optional): Tags associés à la métrique
            
        Returns:
            Dict[str, float]: Statistiques de l'histogramme (min, max, avg, p50, p90, p95, p99)
        """
        if not self.enabled:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'avg': 0,
                'p50': 0,
                'p90': 0,
                'p95': 0,
                'p99': 0
            }
            
        metric_key = self._format_metric_key(name, tags)
        values = self.histograms.get(metric_key, [])
        
        if not values:
            return {
                'count': 0,
                'min': 0,
                'max': 0,
                'avg': 0,
                'p50': 0,
                'p90': 0,
                'p95': 0,
                'p99': 0
            }
            
        # Calculer les statistiques
        sorted_values = sorted(values)
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'p50': sorted_values[int(len(sorted_values) * 0.5)],
            'p90': sorted_values[int(len(sorted_values) * 0.9)],
            'p95': sorted_values[int(len(sorted_values) * 0.95)],
            'p99': sorted_values[int(len(sorted_values) * 0.99)]
        }
        
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Récupère toutes les métriques
        
        Returns:
            Dict[str, Any]: Toutes les métriques
        """
        if not self.enabled:
            return {}
            
        # Calculer les statistiques des histogrammes
        histogram_stats = {}
        for name, values in self.histograms.items():
            if values:
                sorted_values = sorted(values)
                histogram_stats[name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'p50': sorted_values[int(len(sorted_values) * 0.5)],
                    'p90': sorted_values[int(len(sorted_values) * 0.9)],
                    'p95': sorted_values[int(len(sorted_values) * 0.95)],
                    'p99': sorted_values[int(len(sorted_values) * 0.99)]
                }
                
        return {
            'counters': dict(self.counters),
            'gauges': self.gauges,
            'histograms': histogram_stats,
            'timestamp': datetime.now().isoformat()
        }
        
    def save_all_metrics(self) -> None:
        """
        Enregistre toutes les métriques dans des fichiers
        """
        if not self.enabled:
            return
            
        self._save_counters()
        self._save_gauges()
        self._save_histograms()
        
    def start_auto_cleanup(self) -> None:
        """
        Démarre le nettoyage automatique des fichiers de métriques anciens
        """
        if not self.enabled or self.auto_cleanup_running:
            return
            
        self.auto_cleanup_running = True
        
        def cleanup_worker():
            """Fonction de nettoyage périodique"""
            while self.auto_cleanup_running:
                try:
                    self._cleanup_old_files()
                except Exception as e:
                    logger.error(f"Erreur lors du nettoyage des fichiers: {str(e)}")
                    
                # Dormir 24h avant le prochain nettoyage
                time.sleep(86400)  # 24 heures
                
        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()
        
        logger.info("Nettoyage automatique des métriques démarré")
        
    def stop_auto_cleanup(self) -> None:
        """
        Arrête le nettoyage automatique des fichiers de métriques
        """
        self.auto_cleanup_running = False
        logger.info("Nettoyage automatique des métriques arrêté")
        
    def _format_metric_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """
        Formate une clé de métrique avec ses tags
        
        Args:
            name (str): Nom de la métrique
            tags (Dict[str, str], optional): Tags associés à la métrique
            
        Returns:
            str: Clé formatée
        """
        if not tags:
            return name
            
        # Trier les tags pour une clé cohérente
        sorted_tags = sorted(tags.items())
        tag_str = ','.join(f"{k}={v}" for k, v in sorted_tags)
        
        return f"{name}[{tag_str}]"
        
    def _save_counters(self) -> None:
        """
        Enregistre les compteurs dans un fichier
        """
        try:
            # Créer le nom de fichier avec la date du jour
            date_str = datetime.now().strftime('%Y%m%d')
            file_path = os.path.join(self.metrics_dir, f"counters_{date_str}.json")
            
            # Charger les données existantes si elles existent
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    
            # Fusionner avec les données existantes
            for key, value in self.counters.items():
                existing_data[key] = value
                
            # Enregistrer les données
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des compteurs: {str(e)}")
            
    def _save_gauges(self) -> None:
        """
        Enregistre les jauges dans un fichier
        """
        try:
            # Créer le nom de fichier avec la date du jour
            date_str = datetime.now().strftime('%Y%m%d')
            file_path = os.path.join(self.metrics_dir, f"gauges_{date_str}.json")
            
            # Charger les données existantes si elles existent
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    
            # Fusionner avec les données existantes
            for key, value in self.gauges.items():
                existing_data[key] = value
                
            # Enregistrer les données
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des jauges: {str(e)}")
            
    def _save_histograms(self) -> None:
        """
        Enregistre les statistiques des histogrammes dans un fichier
        """
        try:
            # Créer le nom de fichier avec la date du jour
            date_str = datetime.now().strftime('%Y%m%d')
            file_path = os.path.join(self.metrics_dir, f"histograms_{date_str}.json")
            
            # Charger les données existantes si elles existent
            existing_data = {}
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    
            # Calculer les statistiques pour chaque histogramme
            for name, values in self.histograms.items():
                if not values:
                    continue
                    
                sorted_values = sorted(values)
                
                # Calculer les percentiles uniquement s'il y a assez de valeurs
                p50 = p90 = p95 = p99 = 0
                if len(sorted_values) >= 2:
                    p50 = sorted_values[int(len(sorted_values) * 0.5)]
                    if len(sorted_values) >= 10:
                        p90 = sorted_values[int(len(sorted_values) * 0.9)]
                        p95 = sorted_values[int(len(sorted_values) * 0.95)]
                        if len(sorted_values) >= 100:
                            p99 = sorted_values[int(len(sorted_values) * 0.99)]
                
                existing_data[name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'p50': p50,
                    'p90': p90,
                    'p95': p95,
                    'p99': p99,
                    'last_updated': datetime.now().isoformat()
                }
                
            # Enregistrer les données
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des histogrammes: {str(e)}")
            
    def _save_event(self, event: Dict[str, Any]) -> None:
        """
        Enregistre un événement dans un fichier
        
        Args:
            event (Dict[str, Any]): Événement à enregistrer
        """
        try:
            # Créer le répertoire des événements si nécessaire
            events_dir = os.path.join(self.metrics_dir, 'events')
            os.makedirs(events_dir, exist_ok=True)
            
            # Créer le nom de fichier avec la date du jour
            date_str = datetime.now().strftime('%Y%m%d')
            file_path = os.path.join(events_dir, f"events_{date_str}.jsonl")
            
            # Ajouter l'événement au fichier
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement d'un événement: {str(e)}")
            
    def _cleanup_old_files(self) -> None:
        """
        Supprime les fichiers de métriques plus anciens que la période de rétention
        """
        try:
            # Calculer la date limite
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            cutoff_str = cutoff_date.strftime('%Y%m%d')
            
            # Parcourir tous les fichiers de métriques
            for file_name in os.listdir(self.metrics_dir):
                if file_name.endswith('.json'):
                    # Extraire la date du nom de fichier
                    parts = file_name.split('_')
                    if len(parts) >= 2:
                        date_str = parts[1].split('.')[0]
                        if date_str < cutoff_str:
                            # Supprimer le fichier
                            os.remove(os.path.join(self.metrics_dir, file_name))
                            logger.info(f"Fichier de métriques supprimé: {file_name}")
                            
            # Nettoyer également les fichiers d'événements
            events_dir = os.path.join(self.metrics_dir, 'events')
            if os.path.exists(events_dir):
                for file_name in os.listdir(events_dir):
                    if file_name.endswith('.jsonl'):
                        # Extraire la date du nom de fichier
                        parts = file_name.split('_')
                        if len(parts) >= 2:
                            date_str = parts[1].split('.')[0]
                            if date_str < cutoff_str:
                                # Supprimer le fichier
                                os.remove(os.path.join(events_dir, file_name))
                                logger.info(f"Fichier d'événements supprimé: {file_name}")
                                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des fichiers: {str(e)}")

# Instance singleton pour l'utilisation dans l'application
metrics_manager = MetricsManager()
