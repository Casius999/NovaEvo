# Module NLP - Traitement du Langage Naturel

Ce module permet à l'Assistant Auto Ultime d'interpréter les commandes et requêtes des utilisateurs en langage naturel et de générer des réponses pertinentes.

## Fonctionnalités

- Analyse des requêtes en langage naturel
- Catégorisation des requêtes (diagnostic, entretien, performance, etc.)
- Extraction d'entités (codes d'erreur, modèles de véhicules, symptômes, etc.)
- Génération de réponses informatives et contextuelles
- Traitement local des requêtes simples (codes d'erreur, entretien de base)
- Utilisation de l'API OpenAI GPT-4 pour les requêtes complexes

## Structure du module

```
/nlp/
  ├── __init__.py          # Fichier d'initialisation du package
  ├── nlp_main.py          # Module principal NLP
  └── README.md            # Documentation sommaire
```

## Implémentation

Le module est implémenté avec la classe `AutoAssistantNLP`, qui gère :
- La connexion avec l'API OpenAI
- L'interprétation des requêtes et commandes
- Le traitement local des requêtes simples
- La génération de réponses via l'API OpenAI

## API REST

Le module est accessible via l'endpoint `/nlp` de l'API REST, qui accepte les requêtes POST contenant une commande en langage naturel et retourne une réponse générée.

## Configuration

Le module nécessite une clé API OpenAI, qui doit être configurée dans le fichier `.env` :

```
OPENAI_API_KEY=votre_clé_api_ici
GPT_MODEL=gpt-4-turbo-preview
```

## Exemples d'utilisation

```python
from nlp.nlp_main import AutoAssistantNLP

# Initialiser l'assistant NLP
nlp_assistant = AutoAssistantNLP()

# Interpréter une commande
result = nlp_assistant.interpret_command("Que signifie le code erreur P0300 ?")
print(result)
```

## Documentation détaillée

Une documentation complète est disponible dans le fichier [docs/README_NLP.md](../docs/README_NLP.md), qui inclut :

- Guide d'installation et de configuration
- Exemples de commandes et réponses
- Détails techniques sur l'implémentation
- Dépannage et support

## Tests

Des tests unitaires pour le module se trouvent dans [tests/test_nlp.py](../tests/test_nlp.py) et peuvent être exécutés avec pytest :

```bash
pytest tests/test_nlp.py -v
```
