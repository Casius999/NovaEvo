import React, { useState, useEffect } from 'react';
import { Container, Card, Button, Form, Alert, Row, Col, Nav, Tab } from 'react-bootstrap';

const Auth = ({ setIsAuthenticated }) => {
  // État pour la gestion des formulaires
  const [activeTab, setActiveTab] = useState('login');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerConfirmPassword, setRegisterConfirmPassword] = useState('');
  const [registerName, setRegisterName] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Vérifier si l'utilisateur est déjà connecté au chargement du composant
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
      setIsAuthenticated(true);
    }
  }, [setIsAuthenticated]);

  // Gérer la soumission du formulaire de connexion
  const handleLogin = (e) => {
    e.preventDefault();
    setError(null);
    
    // Validation de base
    if (!loginEmail || !loginPassword) {
      setError("Veuillez remplir tous les champs");
      return;
    }
    
    // Simulation d'API pour démonstration
    // Dans une vraie application, vous feriez un appel à l'API backend ici
    if (loginEmail === 'demo@example.com' && loginPassword === 'password') {
      // Stocker le jeton et les informations utilisateur dans localStorage
      const userData = {
        email: loginEmail,
        name: 'Utilisateur Démo',
        subscriptionType: 'premium',
        subscriptionEndDate: '2025-12-31'
      };
      
      localStorage.setItem('auth_token', 'demo_token_123456');
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Mettre à jour l'état d'authentification
      setIsAuthenticated(true);
      
      // Message de succès
      setSuccess("Connexion réussie!");
    } else {
      setError("Email ou mot de passe incorrect");
    }
  };

  // Gérer la soumission du formulaire d'inscription
  const handleRegister = (e) => {
    e.preventDefault();
    setError(null);
    
    // Validation de base
    if (!registerEmail || !registerPassword || !registerConfirmPassword || !registerName) {
      setError("Veuillez remplir tous les champs");
      return;
    }
    
    if (registerPassword !== registerConfirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }
    
    if (registerPassword.length < 6) {
      setError("Le mot de passe doit contenir au moins 6 caractères");
      return;
    }
    
    // Simuler une inscription réussie
    setSuccess("Inscription réussie! Vous pouvez maintenant vous connecter.");
    setActiveTab('login');
    setLoginEmail(registerEmail);
    setLoginPassword('');
  };

  // Simuler les abonnements disponibles
  const subscriptionPlans = [
    {
      id: 'basic',
      name: 'Basique',
      price: '9,99 €/mois',
      features: [
        'Scan de carte grise illimité',
        'Diagnostics OBD-II en temps réel',
        'Assistant NLP standard',
        'Reconnaissance d\'image basique'
      ]
    },
    {
      id: 'premium',
      name: 'Premium',
      price: '19,99 €/mois',
      features: [
        'Toutes les fonctionnalités Basiques',
        'Flash ECU (limité)',
        'Recherche de pièces multi-sources',
        'Diagnostics avancés'
      ]
    },
    {
      id: 'ultimate',
      name: 'Ultimate',
      price: '29,99 €/mois',
      features: [
        'Toutes les fonctionnalités Premium',
        'Flash ECU illimité',
        'Diagnostics professionnels',
        'Support technique prioritaire',
        'Accès aux mises à jour en avant-première'
      ]
    }
  ];

  return (
    <Container className="my-4">
      <h2 className="mb-4">Espace Utilisateur</h2>

      <Tab.Container activeKey={activeTab} onSelect={(k) => setActiveTab(k)}>
        <Row>
          <Col md={4}>
            <Card>
              <Card.Header>
                <Nav variant="tabs" className="flex-column">
                  <Nav.Item>
                    <Nav.Link eventKey="login">Connexion</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="register">Inscription</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link eventKey="subscription">Abonnements</Nav.Link>
                  </Nav.Item>
                </Nav>
              </Card.Header>
              <Card.Body>
                <div className="text-center mb-4">
                  <img 
                    src="/logo192.png" 
                    alt="Assistant Auto Ultime" 
                    height="80" 
                    className="mb-3"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = "https://via.placeholder.com/80?text=AAU";
                    }}
                  />
                  <h5>Assistant Auto Ultime</h5>
                  <p className="text-muted">Votre partenaire automobile intelligent</p>
                </div>
                
                <Alert variant="info">
                  <strong>Démo</strong><br />
                  Email: demo@example.com<br />
                  Mot de passe: password
                </Alert>
              </Card.Body>
            </Card>
          </Col>
          
          <Col md={8}>
            <Card>
              <Card.Body>
                {error && <Alert variant="danger">{error}</Alert>}
                {success && <Alert variant="success">{success}</Alert>}
                
                <Tab.Content>
                  {/* Onglet Connexion */}
                  <Tab.Pane eventKey="login">
                    <h4 className="mb-4">Connexion</h4>
                    <Form onSubmit={handleLogin}>
                      <Form.Group className="mb-3">
                        <Form.Label>Email</Form.Label>
                        <Form.Control 
                          type="email" 
                          placeholder="votre@email.com" 
                          value={loginEmail} 
                          onChange={(e) => setLoginEmail(e.target.value)}
                        />
                      </Form.Group>
                      
                      <Form.Group className="mb-3">
                        <Form.Label>Mot de passe</Form.Label>
                        <Form.Control 
                          type="password" 
                          placeholder="Votre mot de passe" 
                          value={loginPassword} 
                          onChange={(e) => setLoginPassword(e.target.value)}
                        />
                      </Form.Group>
                      
                      <Form.Group className="mb-3">
                        <Form.Check 
                          type="checkbox" 
                          label="Se souvenir de moi" 
                        />
                      </Form.Group>
                      
                      <div className="d-grid">
                        <Button variant="primary" type="submit">
                          Se connecter
                        </Button>
                      </div>
                      
                      <div className="text-center mt-3">
                        <Button 
                          variant="link" 
                          className="px-0" 
                          onClick={() => setActiveTab('register')}
                        >
                          Pas encore inscrit ? Créer un compte
                        </Button>
                      </div>
                    </Form>
                  </Tab.Pane>
                  
                  {/* Onglet Inscription */}
                  <Tab.Pane eventKey="register">
                    <h4 className="mb-4">Inscription</h4>
                    <Form onSubmit={handleRegister}>
                      <Form.Group className="mb-3">
                        <Form.Label>Nom complet</Form.Label>
                        <Form.Control 
                          type="text" 
                          placeholder="Votre nom" 
                          value={registerName} 
                          onChange={(e) => setRegisterName(e.target.value)}
                        />
                      </Form.Group>
                      
                      <Form.Group className="mb-3">
                        <Form.Label>Email</Form.Label>
                        <Form.Control 
                          type="email" 
                          placeholder="votre@email.com" 
                          value={registerEmail} 
                          onChange={(e) => setRegisterEmail(e.target.value)}
                        />
                      </Form.Group>
                      
                      <Form.Group className="mb-3">
                        <Form.Label>Mot de passe</Form.Label>
                        <Form.Control 
                          type="password" 
                          placeholder="Choisissez un mot de passe" 
                          value={registerPassword} 
                          onChange={(e) => setRegisterPassword(e.target.value)}
                        />
                        <Form.Text className="text-muted">
                          Le mot de passe doit contenir au moins 6 caractères.
                        </Form.Text>
                      </Form.Group>
                      
                      <Form.Group className="mb-3">
                        <Form.Label>Confirmer le mot de passe</Form.Label>
                        <Form.Control 
                          type="password" 
                          placeholder="Répétez votre mot de passe" 
                          value={registerConfirmPassword} 
                          onChange={(e) => setRegisterConfirmPassword(e.target.value)}
                        />
                      </Form.Group>
                      
                      <Form.Group className="mb-3">
                        <Form.Check 
                          type="checkbox" 
                          label="J'accepte les conditions d'utilisation" 
                          required
                        />
                      </Form.Group>
                      
                      <div className="d-grid">
                        <Button variant="success" type="submit">
                          Créer un compte
                        </Button>
                      </div>
                      
                      <div className="text-center mt-3">
                        <Button 
                          variant="link" 
                          className="px-0" 
                          onClick={() => setActiveTab('login')}
                        >
                          Déjà inscrit ? Se connecter
                        </Button>
                      </div>
                    </Form>
                  </Tab.Pane>
                  
                  {/* Onglet Abonnements */}
                  <Tab.Pane eventKey="subscription">
                    <h4 className="mb-4">Nos Abonnements</h4>
                    <Row>
                      {subscriptionPlans.map((plan) => (
                        <Col md={4} key={plan.id} className="mb-3">
                          <Card className={`h-100 ${plan.id === 'premium' ? 'border-primary' : ''}`}>
                            <Card.Header className={plan.id === 'premium' ? 'bg-primary text-white' : ''}>
                              <h5 className="mb-0">{plan.name}</h5>
                            </Card.Header>
                            <Card.Body>
                              <h4 className="mb-3">{plan.price}</h4>
                              <ul className="list-unstyled">
                                {plan.features.map((feature, index) => (
                                  <li key={index} className="mb-2">
                                    <i className="bi bi-check-circle-fill text-success me-2"></i>
                                    {feature}
                                  </li>
                                ))}
                              </ul>
                            </Card.Body>
                            <Card.Footer>
                              <div className="d-grid">
                                <Button 
                                  variant={plan.id === 'premium' ? 'primary' : 'outline-primary'}
                                  onClick={() => setActiveTab('register')}
                                >
                                  Sélectionner
                                </Button>
                              </div>
                            </Card.Footer>
                          </Card>
                        </Col>
                      ))}
                    </Row>
                  </Tab.Pane>
                </Tab.Content>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Tab.Container>
      
      {/* Avantages du compte */}
      <Card className="mt-4">
        <Card.Header>Avantages de votre compte</Card.Header>
        <Card.Body>
          <Row>
            <Col md={3} className="text-center mb-3">
              <i className="bi bi-cloud-arrow-up fs-1 text-primary"></i>
              <h5 className="mt-2">Sauvegarde cloud</h5>
              <p className="text-muted">Accédez à vos données depuis n'importe quel appareil</p>
            </Col>
            <Col md={3} className="text-center mb-3">
              <i className="bi bi-file-earmark-text fs-1 text-primary"></i>
              <h5 className="mt-2">Historique complet</h5>
              <p className="text-muted">Consultez l'historique de vos diagnostics et réparations</p>
            </Col>
            <Col md={3} className="text-center mb-3">
              <i className="bi bi-bell fs-1 text-primary"></i>
              <h5 className="mt-2">Alertes personnalisées</h5>
              <p className="text-muted">Recevez des notifications pour l'entretien de votre véhicule</p>
            </Col>
            <Col md={3} className="text-center mb-3">
              <i className="bi bi-gear fs-1 text-primary"></i>
              <h5 className="mt-2">Fonctionnalités avancées</h5>
              <p className="text-muted">Accédez à toutes les fonctionnalités selon votre abonnement</p>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Auth;