import React, { useState } from 'react';
import { Form, Button, Alert, Card, Spinner } from 'react-bootstrap';
import axios from 'axios';

/**
 * Composant de collecte de feedback utilisateur
 * Permet aux utilisateurs de soumettre des commentaires, signaler des bugs
 * ou suggérer des améliorations
 */
const Feedback = () => {
  // États
  const [feedbackType, setFeedbackType] = useState('comment');
  const [feedbackText, setFeedbackText] = useState('');
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [alert, setAlert] = useState({ show: false, variant: '', message: '' });

  // Fonction pour soumettre le feedback
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation de base
    if (!feedbackText.trim()) {
      setAlert({
        show: true,
        variant: 'danger',
        message: 'Veuillez saisir un message de feedback.'
      });
      return;
    }
    
    // Préparation des données
    const feedbackData = {
      type: feedbackType,
      message: feedbackText,
      email: email || 'anonymous', // email optionnel
      timestamp: new Date().toISOString(),
      source: 'web_app',
      userAgent: navigator.userAgent
    };
    
    setSubmitting(true);
    
    try {
      // Envoi au backend
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL || ''}/feedback`,
        feedbackData,
        { headers: { 'Content-Type': 'application/json' } }
      );
      
      if (response.status === 200 || response.status === 201) {
        // Feedback soumis avec succès
        setAlert({
          show: true,
          variant: 'success',
          message: 'Merci pour votre feedback ! Nous l\'avons bien reçu.'
        });
        
        // Réinitialiser le formulaire
        setFeedbackText('');
        setEmail('');
      } else {
        throw new Error('Erreur lors de l\'envoi du feedback');
      }
    } catch (error) {
      console.error('Erreur lors de la soumission du feedback:', error);
      setAlert({
        show: true,
        variant: 'danger',
        message: 'Une erreur est survenue lors de l\'envoi de votre feedback. Veuillez réessayer.'
      });
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <Card className="mb-4 shadow-sm">
      <Card.Header className="bg-primary text-white">
        <h5 className="mb-0">Votre avis nous intéresse</h5>
      </Card.Header>
      <Card.Body>
        {alert.show && (
          <Alert 
            variant={alert.variant} 
            dismissible 
            onClose={() => setAlert({...alert, show: false})}
          >
            {alert.message}
          </Alert>
        )}
        
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Type de feedback</Form.Label>
            <Form.Select 
              value={feedbackType} 
              onChange={(e) => setFeedbackType(e.target.value)}
            >
              <option value="comment">Commentaire général</option>
              <option value="bug">Signalement de bug</option>
              <option value="feature">Suggestion d'amélioration</option>
              <option value="question">Question</option>
            </Form.Select>
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Votre message</Form.Label>
            <Form.Control 
              as="textarea" 
              rows={4} 
              value={feedbackText} 
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Décrivez votre feedback, bug rencontré ou suggestion d'amélioration..."
              required
            />
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Email (optionnel)</Form.Label>
            <Form.Control 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              placeholder="votre@email.com"
            />
            <Form.Text className="text-muted">
              Facultatif. Utile si vous souhaitez être recontacté.
            </Form.Text>
          </Form.Group>
          
          <Button 
            variant="primary" 
            type="submit" 
            disabled={submitting}
            className="d-flex align-items-center"
          >
            {submitting && (
              <Spinner 
                as="span"
                animation="border" 
                size="sm" 
                role="status" 
                aria-hidden="true"
                className="me-2"
              />
            )}
            Envoyer mon feedback
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default Feedback;
