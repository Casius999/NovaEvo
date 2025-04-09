"""
Module Image Recognition - Reconnaissance d'image
Ce module utilise OpenCV et des modèles de vision par ordinateur pour identifier 
des pièces automobiles, diagnostiquer des problèmes visuels et analyser l'état du véhicule.
"""
import os
import cv2
import numpy as np
import json
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class ImageRecognitionEngine:
    """Moteur de reconnaissance d'images pour le diagnostic automobile"""
    
    def __init__(self):
        """Initialisation du moteur de reconnaissance d'image"""
        self.model_path = os.getenv('MODEL_PATH', 'models/detection_model.pb')
        self.labels_path = os.getenv('LABELS_PATH', 'models/labels.pbtxt')
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
        
        # Tenter de charger le modèle si disponible
        self.net = None
        self.labels = {}
        
        # Vérifier si les fichiers du modèle existent
        if os.path.exists(self.model_path) and os.path.exists(self.labels_path):
            try:
                self.net = cv2.dnn.readNetFromTensorflow(self.model_path)
                self._load_labels()
                print(f"Modèle chargé avec succès: {self.model_path}")
                print(f"Étiquettes chargées: {len(self.labels)} classes")
            except Exception as e:
                print(f"Erreur lors du chargement du modèle: {str(e)}")
        else:
            print(f"AVERTISSEMENT: Fichiers de modèle non trouvés.")
            print(f"Créez un dossier 'models' avec les fichiers de modèle appropriés.")
            
        # Initialiser OpenCV pour les fonctionnalités de base
        self.initialized = True
    
    def _load_labels(self):
        """Charge les étiquettes à partir du fichier pbtxt"""
        with open(self.labels_path, 'r') as f:
            lines = f.readlines()
            
        current_id = None
        current_name = None
        
        for line in lines:
            line = line.strip()
            if 'id:' in line:
                current_id = int(line.split(':')[-1].strip())
            elif 'name:' in line:
                current_name = line.split(':')[-1].strip().replace("'", "").replace('"', '')
                if current_id is not None:
                    self.labels[current_id] = current_name
                    current_id = None
    
    def analyze_image(self, image_path=None, image_array=None):
        """
        Analyse une image pour détecter et identifier des objets automobiles
        
        Args:
            image_path (str, optional): Chemin vers l'image à analyser
            image_array (numpy.ndarray, optional): Image déjà chargée en mémoire
            
        Returns:
            dict: Résultats de l'analyse avec les objets détectés
        """
        if not self.initialized:
            return {"error": "Moteur d'analyse d'image non initialisé correctement"}
        
        try:
            # Charger l'image
            if image_path:
                image = cv2.imread(image_path)
                if image is None:
                    return {"error": f"Impossible de charger l'image: {image_path}"}
            elif image_array is not None:
                image = image_array
            else:
                return {"error": "Aucune image fournie"}
            
            # Si le modèle n'est pas chargé, utiliser seulement les fonctionnalités de base OpenCV
            if self.net is None:
                return self._basic_image_analysis(image)
            else:
                return self._model_based_analysis(image)
                
        except Exception as e:
            return {"error": f"Erreur lors de l'analyse de l'image: {str(e)}"}
    
    def _basic_image_analysis(self, image):
        """
        Analyse de base d'une image avec OpenCV sans modèle de ML
        
        Args:
            image (numpy.ndarray): Image à analyser
            
        Returns:
            dict: Résultats de l'analyse basique
        """
        height, width, _ = image.shape
        
        # Convertir en niveaux de gris pour l'analyse
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Détection des contours
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Nombre d'objets approximatif basé sur les contours
        significant_contours = [c for c in contours if cv2.contourArea(c) > 500]
        
        # Analyse de couleur
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        color_ranges = {
            "rouge": ([0, 100, 100], [10, 255, 255]),
            "jaune": ([20, 100, 100], [35, 255, 255]),
            "vert": ([35, 50, 50], [85, 255, 255]),
            "bleu": ([85, 50, 50], [130, 255, 255])
        }
        
        color_detection = {}
        for color_name, (lower, upper) in color_ranges.items():
            lower = np.array(lower, dtype=np.uint8)
            upper = np.array(upper, dtype=np.uint8)
            mask = cv2.inRange(hsv, lower, upper)
            ratio = cv2.countNonZero(mask) / (height * width)
            color_detection[color_name] = ratio * 100  # en pourcentage
        
        dominant_color = max(color_detection.items(), key=lambda x: x[1])
        
        return {
            "success": True,
            "type": "basic_analysis",
            "dimensions": {
                "width": width,
                "height": height
            },
            "contours": {
                "total": len(contours),
                "significant": len(significant_contours)
            },
            "colors": {
                "dominant": dominant_color[0] if dominant_color[1] > 5 else "indéterminé",
                "distribution": color_detection
            },
            "possible_diagnoses": [
                "Image analysée avec capacités basiques uniquement",
                "Pour une analyse plus précise, veuillez configurer un modèle de détection"
            ]
        }
    
    def _model_based_analysis(self, image):
        """
        Analyse d'image basée sur un modèle de ML préchargé
        
        Args:
            image (numpy.ndarray): Image à analyser
            
        Returns:
            dict: Résultats de l'analyse avancée
        """
        height, width, _ = image.shape
        
        # Préparer l'image pour le modèle
        blob = cv2.dnn.blobFromImage(image, size=(300, 300), swapRB=True, crop=False)
        self.net.setInput(blob)
        
        # Faire la prédiction
        detections = self.net.forward()
        
        # Traiter les résultats
        results = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > self.confidence_threshold:
                class_id = int(detections[0, 0, i, 1])
                class_name = self.labels.get(class_id, f"Classe {class_id}")
                
                # Coordonnées de la boîte englobante
                box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                x_min, y_min, x_max, y_max = box.astype('int')
                
                results.append({
                    "class": class_name,
                    "confidence": float(confidence),
                    "bounding_box": {
                        "x_min": int(x_min),
                        "y_min": int(y_min),
                        "x_max": int(x_max),
                        "y_max": int(y_max)
                    }
                })
        
        # Générer des diagnostics possibles basés sur les objets détectés
        possible_diagnoses = self._generate_diagnoses(results)
        
        return {
            "success": True,
            "type": "model_based_analysis",
            "dimensions": {
                "width": width,
                "height": height
            },
            "detections": results,
            "detected_count": len(results),
            "possible_diagnoses": possible_diagnoses
        }
    
    def _generate_diagnoses(self, detections):
        """
        Génère des diagnostics possibles basés sur les objets détectés
        
        Args:
            detections (list): Liste des objets détectés
            
        Returns:
            list: Diagnostics possibles
        """
        diagnoses = []
        
        # Exemples de logique de diagnostic simple
        detected_classes = [d["class"].lower() for d in detections]
        
        if not detected_classes:
            diagnoses.append("Aucun objet automobile reconnu dans l'image")
            return diagnoses
        
        # Diagnostics basés sur les pièces détectées
        component_diagnoses = {
            "frein": "Vérifiez l'état des plaquettes et des disques de frein",
            "pneu": "Inspectez l'usure et la pression des pneus",
            "huile": "Contrôlez le niveau et la qualité de l'huile",
            "moteur": "Examinez l'état général du moteur",
            "batterie": "Vérifiez les connections et la charge de la batterie",
            "phare": "Assurez-vous que tous les phares fonctionnent correctement"
        }
        
        for component, diagnosis in component_diagnoses.items():
            if any(component in cls for cls in detected_classes):
                diagnoses.append(diagnosis)
        
        # Diagnostics basés sur les conditions détectées
        if "rouille" in detected_classes or "corrosion" in detected_classes:
            diagnoses.append("Présence de corrosion détectée - vérifiez l'étendue des dommages")
            
        if "fuite" in detected_classes or "liquide" in detected_classes:
            diagnoses.append("Fuite de liquide détectée - vérifiez le type et la source")
            
        if "fissure" in detected_classes:
            diagnoses.append("Fissure détectée - inspectez la gravité et l'emplacement")
            
        # Si aucun diagnostic spécifique n'a été généré
        if not diagnoses:
            diagnoses.append("Composants automobiles détectés, mais aucun problème spécifique identifié")
            
        return diagnoses

# Exemple d'utilisation
def main():
    """Fonction principale pour tester le module de reconnaissance d'image"""
    engine = ImageRecognitionEngine()
    
    # Exemple de test avec une image locale (si disponible)
    test_image = "test_images/car_part_sample.jpg"
    if os.path.exists(test_image):
        print(f"Analyse de l'image de test: {test_image}")
        result = engine.analyze_image(image_path=test_image)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Image de test non trouvée: {test_image}")
        print("Créez un dossier 'test_images' avec des exemples pour tester.")

if __name__ == "__main__":
    main()
