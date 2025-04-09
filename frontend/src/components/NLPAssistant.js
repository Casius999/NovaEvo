import React, { useState, useRef, useEffect } from 'react';
import { Container, Card, Button, Form, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';

const NLPAssistant = () => {
  const [command, setCommand] = useState('');
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);

  // Liste d'exemples de commandes
  const exampleCommands = [
    "Que signifie le code erreur P0300 ?",
    "Comment réparer un problème de démarrage ?",
    "Quelle est la meilleure huile pour ma voiture ?",
    "Comment changer les plaquettes de frein ?",
    "Quels sont les symptômes d'une pompe à eau défectueuse ?"
  ];

  // Pour faire défiler automatiquement vers le bas de la conversation
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversations]);

  // Fonction pour envoyer une commande
  const sendCommand = async (commandText = command) => {
    if (!commandText.trim()) return;

    try {
      setLoading(true);
      setError(null);
      
      // Ajouter la commande de l'utilisateur à la conversation
      setConversations(prev => [...prev, { type: 'user', text: commandText }]);
      
      // Appel à l'API NLP
      const response = await axios.post('/nlp', {
        command: commandText
      });
      
      // Ajouter la réponse à la conversation
      setConversations(prev => [...prev, { 
        type: 'assistant', 
        text: response.data.response || 'Je ne sais pas comment répondre à cette question.'
      }]);
      
      // Vider le champ de saisie
      setCommand('');
      
    } catch (err) {
      console.error("Erreur lors de l'envoi de la commande NLP:", err);
      setError("Une erreur s'est produite lors du traitement de votre commande. Veuillez réessayer.");
      
      // Ajouter le message d'erreur à la conversation
      setConversations(prev => [...prev, { 
        type: 'system', 
        text: "Désolé, je n'ai pas pu traiter votre demande en raison d'une erreur technique."
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour utiliser une commande d'exemple
  const useExampleCommand = (example) => {
    setCommand(example);
    sendCommand(example);
  };

  // Gérer la soumission du formulaire
  const handleSubmit = (e) => {
    e.preventDefault();
    sendCommand();
  };

  return (
    <Container className="my-4">
      <h2 className="mb-4">Assistant Automobile</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {/* Zone de conversation */}
      <Card className="mb-3">
        <Card.Body style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {conversations.length === 0 ? (
            <div className="text-center text-muted my-5">
              <p>Posez une question ou utilisez un exemple ci-dessous</p>
            </div>
          ) : (
            <div className="conversation">
              {conversations.map((msg, index) => (
                <div 
                  key={index} 
                  className={`message ${msg.type}`}
                  style={{
                    marginBottom: '15px',
                    padding: '10px 15px',
                    borderRadius: '15px',
                    maxWidth: '80%',
                    backgroundColor: msg.type === 'user' ? '#007bff' : msg.type === 'assistant' ? '#f8f9fa' : '#ffc107',
                    color: msg.type === 'user' ? 'white' : 'black',
                    alignSelf: msg.type === 'user' ? 'flex-end' : 'flex-start',
                    marginLeft: msg.type === 'user' ? 'auto' : '0',
                  }}
                >
                  {msg.text}
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
          )}
        </Card.Body>
      </Card>
      
      {/* Formulaire de saisie */}
      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Control
            type="text"
            placeholder="Posez votre question ici..."
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            disabled={loading}
          />
        </Form.Group>
        <Button 
          variant="primary" 
          type="submit" 
          disabled={loading || !command.trim()}
          className="w-100"
        >
          {loading ? (
            <>
              <Spinner animation="border" size="sm" className="me-2" />
              Traitement en cours...
            </>
          ) : (
            'Envoyer'
          )}
        </Button>
      </Form>
      
      {/* Exemples de commandes */}
      <Card className="mt-4">
        <Card.Header>Exemples de questions</Card.Header>
        <Card.Body>
          <div className="d-flex flex-wrap gap-2">
            {exampleCommands.map((example, index) => (
              <Button 
                key={index} 
                variant="outline-secondary" 
                size="sm" 
                onClick={() => useExampleCommand(example)}
                disabled={loading}
              >
                {example}
              </Button>
            ))}
          </div>
        </Card.Body>
      </Card>
      
      {/* Informations sur les capacités */}
      <Card className="mt-4">
        <Card.Header>Capacités de l'Assistant</Card.Header>
        <Card.Body>
          <ul>
            <li>Interpréter les codes d'erreur OBD-II</li>
            <li>Fournir des conseils de maintenance et de réparation</li>
            <li>Répondre aux questions sur les caractéristiques des véhicules</li>
            <li>Suggérer des options de tuning et d'optimisation</li>
            <li>Orienter vers les pièces nécessaires pour les réparations</li>
          </ul>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default NLPAssistant;