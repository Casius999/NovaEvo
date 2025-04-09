"""
Module NLP - Traitement du Langage Naturel
Ce module permet l'interprétation des commandes utilisateur en langage naturel
"""
import os
import json
import re
from dotenv import load_dotenv
import openai

# Charger les variables d'environnement
load_dotenv()

class AutoAssistantNLP:
    """Assistant NLP pour l'interprétation des commandes auto"""
    
    def __init__(self):
        """Initialise l'assistant NLP"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.model = os.getenv('GPT_MODEL', 'gpt-4-turbo-preview')
            self.initialized = True
        else:
            print("AVERTISSEMENT: Clé API OpenAI non configurée!")
            self.initialized = False
            
        # Charger la base de connaissances automobile
        self.auto_knowledge = {
            "codes_erreur": {
                "P0": "Problème de système de carburant/air",
                "P1": "Problème spécifique au constructeur",
                "P2": "Problème de gestion du carburant/air",
                "P3": "Problème d'allumage",
                "P00": "Système de contrôle d'émission",
                "P01": "Mesure de débit de carburant/d'air",
                "P02": "Circuit d'injection",
                "P03": "Système d'allumage",
                "P04": "Système de contrôle auxiliaire d'émission",
                "P05": "Contrôle de vitesse/régime de ralenti",
                # Exemples spécifiques
                "P0120": "Capteur de position du papillon/pédale - problème de circuit",
                "P0300": "Détection de ratés d'allumage aléatoires",
                "P0420": "Efficacité du système catalytique inférieure au seuil"
            },
            "entretien": {
                "vidange": "À réaliser tous les 10 000 à 15 000 km ou une fois par an",
                "freins": "Vérifier les plaquettes tous les 10 000 km, disques tous les 50 000 km",
                "pneus": "Vérifier la pression mensuelle, remplacer tous les 40 000 km ou 4 ans",
                "filtre_air": "Remplacer tous les 15 000 à 30 000 km",
                "filtre_habitacle": "Remplacer tous les 15 000 km ou une fois par an",
                "courroie_distribution": "Remplacer entre 60 000 et 120 000 km selon le modèle"
            },
            "pièces": {
                "categories": ["freinage", "moteur", "transmission", "suspension", "filtration", "échappement"]
            }
        }
            
    def interpret_command(self, user_query):
        """
        Interprète une commande utilisateur en langage naturel
        
        Args:
            user_query (str): La requête de l'utilisateur
            
        Returns:
            dict: Interprétation de la requête et action suggérée
        """
        if not self.initialized:
            return {"error": "Service NLP non initialisé. Clé API manquante."}
        
        try:
            # Vérifier d'abord si c'est une demande de code erreur avec regex
            code_match = re.search(r'[Pp][0-9]{4}', user_query)
            if code_match:
                code = code_match.group(0).upper()
                return self._handle_error_code(code)
            
            # Rechercher des mots-clés pour le traitement local
            if any(keyword in user_query.lower() for keyword in ["vidange", "entretien", "quand changer"]):
                return self._handle_maintenance_query(user_query)
                
            # Pour les requêtes plus complexes, utiliser l'API OpenAI
            system_prompt = """
            Tu es un assistant spécialisé dans l'automobile qui aide à interpréter les requêtes des utilisateurs.
            Pour chaque requête, tu dois:
            1. La catégoriser (diagnostic, entretien, pièces, etc.)
            2. Extraire les informations clés (modèle de voiture, symptômes, etc.)
            3. Suggérer les prochaines actions à entreprendre
            
            Réponds sous format JSON avec les champs:
            {
                "category": "string", // diagnostic, entretien, pièces, etc.
                "intent": "string", // intention détectée
                "entities": {}, // informations extraites comme le modèle, l'année, etc.
                "suggested_action": "string", // action recommandée
                "module": "string" // module à utiliser: obd, ocr, parts_finder, etc.
            }
            """
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            # Extraire et parser la réponse JSON
            response_text = response.choices[0].message.content
            return json.loads(response_text)
            
        except Exception as e:
            return {
                "error": f"Erreur lors de l'interprétation: {str(e)}",
                "query": user_query
            }
    
    def _handle_error_code(self, code):
        """
        Traite un code d'erreur OBD spécifique
        
        Args:
            code (str): Code d'erreur au format Pxxxx
            
        Returns:
            dict: Informations sur le code d'erreur
        """
        # Vérifier dans notre base de connaissances
        code_prefix_2 = code[:2]  # P0, P1, etc.
        code_prefix_3 = code[:3]  # P00, P01, etc.
        
        description = None
        
        # Vérifier d'abord le code complet
        if code in self.auto_knowledge["codes_erreur"]:
            description = self.auto_knowledge["codes_erreur"][code]
        # Puis vérifier le préfixe à 3 chiffres
        elif code_prefix_3 in self.auto_knowledge["codes_erreur"]:
            description = self.auto_knowledge["codes_erreur"][code_prefix_3]
        # Enfin vérifier le préfixe à 2 chiffres
        elif code_prefix_2 in self.auto_knowledge["codes_erreur"]:
            description = self.auto_knowledge["codes_erreur"][code_prefix_2]
        
        if description:
            return {
                "success": True,
                "category": "diagnostic",
                "intent": "recherche_code_erreur",
                "entities": {
                    "code": code
                },
                "description": description,
                "suggested_action": f"Vérifier le composant lié au code {code}",
                "module": "obd2"
            }
        else:
            return {
                "success": True,
                "category": "diagnostic",
                "intent": "recherche_code_erreur",
                "entities": {
                    "code": code
                },
                "description": "Code non trouvé dans la base de connaissances locale",
                "suggested_action": "Consulter un manuel technique ou utiliser le module OBD pour plus d'informations",
                "module": "obd2"
            }
    
    def _handle_maintenance_query(self, query):
        """
        Traite une requête liée à l'entretien
        
        Args:
            query (str): Requête utilisateur
            
        Returns:
            dict: Informations sur l'entretien
        """
        query_lower = query.lower()
        
        for maintenance_type, info in self.auto_knowledge["entretien"].items():
            if maintenance_type in query_lower:
                return {
                    "success": True,
                    "category": "entretien",
                    "intent": f"information_{maintenance_type}",
                    "description": info,
                    "suggested_action": "Planifier l'entretien selon les recommandations",
                    "module": "maintenance"
                }
        
        # Si aucune correspondance exacte, retourner des informations générales
        return {
            "success": True,
            "category": "entretien",
            "intent": "information_generale",
            "description": "Programme d'entretien général recommandé",
            "items": self.auto_knowledge["entretien"],
            "suggested_action": "Consulter le carnet d'entretien du véhicule",
            "module": "maintenance"
        }

# Exemple d'utilisation
def main():
    """Fonction principale pour tester le module NLP"""
    nlp = AutoAssistantNLP()
    
    # Exemples de requêtes à tester
    test_queries = [
        "Que signifie le code erreur P0420 ?",
        "Quand dois-je faire ma prochaine vidange ?",
        "Ma voiture fait un bruit étrange quand je freine",
        "Comment connecter mon OBD à ma Peugeot 308 2018 ?",
        "Trouve-moi des plaquettes de frein pour Renault Clio 4"
    ]
    
    for query in test_queries:
        print(f"\nTest avec: '{query}'")
        result = nlp.interpret_command(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
