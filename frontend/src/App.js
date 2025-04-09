import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { Container, Nav, Navbar, Card, Row, Col, Button, Dropdown, Alert, Badge } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Import des composants
import OCRCapture from './components/OCRCapture';
import OBD2Dashboard from './components/OBD2Dashboard';
import NLPAssistant from './components/NLPAssistant';
import ImageRecognition from './components/ImageRecognition';
import ECUFlash from './components/ECUFlash';
import PartsFinder from './components/PartsFinder';
import Auth from './components/Auth';

// Page d'accueil avec des cartes pour chaque module
const Home = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const userData = JSON.parse(userStr);
        setUser(userData);
      } catch (e) {
        console.error("Erreur lors du parsing des données utilisateur:", e);
      }
    }
  }, []);

  return (
    <Container className="mt-4">
      <div className="text-center mb-5">
        <h1 className="display-4 mb-3">Assistant Auto Ultime</h1>
        <p className="lead">
          Votre suite complète d'outils pour le diagnostic, l'optimisation et l'entretien de votre véhicule.
        </p>
        {user && (
          <div className="mb-4">
            <Alert variant="info">
              Bienvenue, <strong>{user.name}</strong>! 
              Vous avez un abonnement <Badge bg="primary">{user.subscriptionType}</Badge> 
              valable jusqu'au {user.subscriptionEndDate}.
            </Alert>
          </div>
        )}
      </div>

      <Row>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=OCR" />
            <Card.Body>
              <Card.Title>OCR</Card.Title>
              <Card.Text>
                Scannez votre carte grise et extrayez automatiquement toutes les informations de votre véhicule.
              </Card.Text>
              <Link to="/ocr" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=OBD-II" />
            <Card.Body>
              <Card.Title>OBD-II</Card.Title>
              <Card.Text>
                Connectez-vous à votre véhicule et obtenez des diagnostics en temps réel et des codes d'erreur.
              </Card.Text>
              <Link to="/obd2" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=NLP" />
            <Card.Body>
              <Card.Title>Assistant NLP</Card.Title>
              <Card.Text>
                Posez vos questions en langage naturel et obtenez des réponses précises sur votre véhicule.
              </Card.Text>
              <Link to="/nlp" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=Image" />
            <Card.Body>
              <Card.Title>Reconnaissance d'image</Card.Title>
              <Card.Text>
                Analysez visuellement des pannes ou anomalies en soumettant simplement une photo.
              </Card.Text>
              <Link to="/image-recognition" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=ECU" />
            <Card.Body>
              <Card.Title>ECU Flash</Card.Title>
              <Card.Text>
                Optimisez les performances de votre véhicule en reprogrammant l'ECU avec des paramètres personnalisés.
              </Card.Text>
              <Link to="/ecu-flash" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4} className="mb-4">
          <Card className="h-100 shadow-sm">
            <Card.Img variant="top" src="https://via.placeholder.com/300x150?text=Parts" />
            <Card.Body>
              <Card.Title>Parts Finder</Card.Title>
              <Card.Text>
                Trouvez facilement des pièces détachées pour votre véhicule à partir de multiples sources.
              </Card.Text>
              <Link to="/parts-finder" className="btn btn-primary">Accéder</Link>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

// Composant principal de l'application
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  
  // Vérifier l'authentification au chargement de l'application
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      setIsAuthenticated(true);
      try {
        setUser(JSON.parse(userStr));
      } catch (e) {
        console.error("Erreur lors du parsing des données utilisateur:", e);
      }
    }
  }, []);
  
  // Gérer la déconnexion
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <Router>
      <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
        <Container>
          <Navbar.Brand as={Link} to="/">
            <img
              src="/logo192.png"
              width="30"
              height="30"
              className="d-inline-block align-top me-2"
              alt="Assistant Auto Ultime"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "https://via.placeholder.com/30?text=AAU";
              }}
            />
            Assistant Auto Ultime
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/">Accueil</Nav.Link>
              <Nav.Link as={Link} to="/ocr">OCR</Nav.Link>
              <Nav.Link as={Link} to="/obd2">OBD-II</Nav.Link>
              <Nav.Link as={Link} to="/nlp">NLP</Nav.Link>
              <Nav.Link as={Link} to="/image-recognition">Reconnaissance d'image</Nav.Link>
              <Nav.Link as={Link} to="/ecu-flash">ECU Flash</Nav.Link>
              <Nav.Link as={Link} to="/parts-finder">Parts Finder</Nav.Link>
            </Nav>
            
            {isAuthenticated ? (
              <Dropdown align="end">
                <Dropdown.Toggle variant="outline-light" id="dropdown-user">
                  {user?.name || 'Profil'}
                </Dropdown.Toggle>
                <Dropdown.Menu>
                  <Dropdown.Item as={Link} to="/profile">Mon Profil</Dropdown.Item>
                  <Dropdown.Item as={Link} to="/settings">Paramètres</Dropdown.Item>
                  <Dropdown.Divider />
                  <Dropdown.Item onClick={handleLogout}>Déconnexion</Dropdown.Item>
                </Dropdown.Menu>
              </Dropdown>
            ) : (
              <Button variant="outline-light" as={Link} to="/auth">
                Connexion
              </Button>
            )}
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ocr" element={isAuthenticated ? <OCRCapture /> : <Navigate to="/auth" />} />
        <Route path="/obd2" element={isAuthenticated ? <OBD2Dashboard /> : <Navigate to="/auth" />} />
        <Route path="/nlp" element={isAuthenticated ? <NLPAssistant /> : <Navigate to="/auth" />} />
        <Route path="/image-recognition" element={isAuthenticated ? <ImageRecognition /> : <Navigate to="/auth" />} />
        <Route path="/ecu-flash" element={isAuthenticated ? <ECUFlash /> : <Navigate to="/auth" />} />
        <Route path="/parts-finder" element={isAuthenticated ? <PartsFinder /> : <Navigate to="/auth" />} />
        <Route path="/auth" element={<Auth setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      
      <footer className="bg-light py-4 mt-5">
        <Container>
          <Row>
            <Col md={6}>
              <h5>Assistant Auto Ultime</h5>
              <p className="text-muted">
                © 2025 Assistant Auto Ultime. Tous droits réservés.
              </p>
            </Col>
            <Col md={6} className="text-md-end">
              <Button variant="link" className="text-muted">Conditions d'utilisation</Button>
              <Button variant="link" className="text-muted">Politique de confidentialité</Button>
              <Button variant="link" className="text-muted">Contact</Button>
            </Col>
          </Row>
        </Container>
      </footer>
    </Router>
  );
}

export default App;