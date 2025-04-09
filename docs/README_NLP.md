# Module NLP - Documentation

## Description

Le module NLP (Natural Language Processing) de l'Assistant Auto Ultime permet d'interpréter les commandes et requêtes des utilisateurs en langage naturel. Il utilise l'API OpenAI GPT-4 pour comprendre et générer des réponses pertinentes aux questions liées à l'automobile.

## Objectifs

- Permettre aux utilisateurs de soumettre des requêtes en langage naturel
- Analyser et classifier les requêtes par type (diagnostic, entretien, performance, etc.)
- Extraire les informations pertinentes (comme les codes d'erreur, modèles de véhicule, etc.)
- Générer des réponses informatives et pertinentes
- Suggérer des actions appropriées selon le type de requête

## Prérequis

### API Key OpenAI

Pour utiliser ce module, vous devez disposer d'une clé API OpenAI. Cette clé doit être configurée via une variable d'environnement :

```
OPENAI_API_KEY=votre_clé_api_ici
```

Vous pouvez obtenir une clé API sur le [site d'OpenAI](https://platform.openai.com/).

### Modèle GPT

Par défaut, le module utilise le modèle `gpt-4-turbo-preview`. Vous pouvez spécifier un modèle différent via la variable d'environnement :

```
GPT_MODEL=gpt-3.5-turbo
```

### Dépendances

- Python 3.7+
- Bibliothèque `openai` (`pip install openai`)
- Bibliothèque `python-dotenv` pour la gestion des variables d'environnement

## Installation

1. Installez les dépendances nécessaires :

```bash
pip install -r requirements.txt
```

2. Créez un fichier `.env` à la racine du projet et ajoutez votre clé API OpenAI :

```
OPENAI_API_KEY=votre_clé_api_ici
GPT_MODEL=gpt-4-turbo-preview
```

## Utilisation

### Via l'API REST

Le module NLP est accessible via l'endpoint REST `/nlp` de l'API. Vous pouvez envoyer une requête POST contenant une commande en langage naturel :

```bash
curl -X POST http://localhost:5000/nlp \
  -H "Content-Type: application/json" \
  -d '{"command": "Que signifie le code erreur P0300 sur ma BMW 330D ?"}'
```

Réponse typique :

```json
{
  "status": "success",
  "response": "Le code P0300 indique une 'détection de ratés d'allumage aléatoires'. Cela signifie que le calculateur moteur a détecté des ratés sur plusieurs cylindres différents. Causes possibles : bougies usées, bobines défectueuses, injecteurs encrassés, ou problèmes d'alimentation en carburant. Sur votre BMW 330D, vérifiez en priorité les injecteurs et le système d'alimentation en carburant."
}
```

### En tant que module Python

Vous pouvez également utiliser le module directement dans votre code Python :

```python
from nlp.nlp_main import AutoAssistantNLP

# Créer une instance de l'assistant NLP
nlp_assistant = AutoAssistantNLP()

# Interpréter une commande
result = nlp_assistant.interpret_command("Quand dois-je remplacer ma courroie de distribution ?")
print(result)
```

La fonction `interpret_command` retourne un dictionnaire contenant l'interprétation de la requête. Par exemple :

```python
{
  "success": True,
  "category": "entretien",
  "intent": "information_courroie_distribution",
  "description": "Remplacer entre 60 000 et 120 000 km selon le modèle",
  "suggested_action": "Planifier l'entretien selon les recommandations",
  "module": "maintenance"
}
```

## Exemples de commandes et réponses

### Codes d'erreur OBD

**Commande :** "Que signifie le code erreur P0420 ?"

**Réponse :**
```
Le code P0420 indique une "Efficacité du système catalytique inférieure au seuil". Cela signifie que le catalyseur ne fonctionne pas correctement pour réduire les émissions polluantes. Cela peut être causé par un catalyseur endommagé, une fuite dans le système d'échappement, ou des problèmes avec les sondes lambda.
```

### Entretien

**Commande :** "Quand dois-je faire ma prochaine vidange ?"

**Réponse :**
```
Pour la vidange d'huile, elle est généralement à réaliser tous les 10 000 à 15 000 km ou une fois par an, selon la première échéance atteinte. Consultez le carnet d'entretien de votre véhicule pour les recommandations spécifiques du constructeur.
```

### Diagnostic

**Commande :** "Ma voiture fait un bruit étrange quand je freine"

**Réponse :**
```
Un bruit lors du freinage peut indiquer plusieurs problèmes : plaquettes de frein usées (grincement aigu), disques déformés (vibration), ou pièces desserrées (claquement). Pour un diagnostic précis, vérifiez visuellement l'état des plaquettes et disques, ou consultez un professionnel. Ce symptôme ne doit pas être ignoré car il concerne votre sécurité.
```

### Performances

**Commande :** "Comment améliorer les performances de ma Renault Clio RS ?"

**Réponse :**
```
Pour améliorer les performances de votre Renault Clio RS, vous pouvez envisager : optimisation de la cartographie moteur (reprogrammation ECU), amélioration de l'admission d'air (filtre performance), ligne d'échappement sport, suspension plus ferme. Gardez à l'esprit que certaines modifications peuvent affecter la garantie et l'homologation. Privilégiez des pièces de qualité et faites réaliser les travaux par des spécialistes.
```

## Fonctionnalités techniques

Le module NLP intègre plusieurs fonctionnalités techniques :

1. **Traitement local** pour certaines requêtes simples (codes d'erreur, entretien basique)
2. **Base de connaissances intégrée** pour les codes d'erreur et entretiens courants
3. **Analyse par regex** pour détecter les codes d'erreur OBD dans les requêtes
4. **Interprétation complète** via l'API GPT-4 pour les requêtes complexes
5. **Génération de réponses structurées** avec suggestions d'actions

## Tests

Des tests unitaires sont disponibles pour le module NLP. Vous pouvez les exécuter avec :

```bash
python -m unittest tests.test_nlp
```

ou avec pytest :

```bash
pytest tests/test_nlp.py -v
```

Les tests utilisent des mocks pour simuler les appels à l'API OpenAI, donc aucune clé API réelle n'est nécessaire pour les exécuter.

## Intégration

Le module NLP est intégré au backend principal via l'endpoint `/nlp`. Il peut être utilisé depuis le frontend en envoyant une requête POST avec un champ `command` contenant la requête en langage naturel.

## Limitations actuelles

- Le module utilise une base de connaissances limitée pour le traitement local
- Les réponses peuvent varier selon le modèle GPT utilisé
- L'utilisation intensive de l'API OpenAI peut engendrer des coûts
- Nécessite une connexion internet pour les requêtes complexes

## Évolutions futures

- Ajout d'une base de connaissances plus complète pour le traitement local
- Mise en cache des réponses pour les questions fréquentes
- Intégration d'un système d'apprentissage pour améliorer les réponses
- Support de modèles open-source alternatifs

## Support et dépannage

### Vérification de l'accès à l'API

Pour vérifier que votre clé API OpenAI fonctionne correctement :

```python
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Test de connexion simple
try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello world"}
        ]
    )
    print("Connexion réussie à l'API OpenAI")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Erreur lors de la connexion à l'API OpenAI: {str(e)}")
```

### Problèmes courants

1. **Erreur de clé API** : Vérifiez que votre clé API est correcte et active dans votre compte OpenAI.
2. **Limite d'utilisation** : Si vous atteignez votre limite d'utilisation, les requêtes échoueront.
3. **Timeout** : Les requêtes peuvent échouer en cas de latence réseau élevée.

## Licence

Ce module est distribué sous la même licence que le projet Assistant Auto Ultime.
