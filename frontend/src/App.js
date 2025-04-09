import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Container, Nav, Navbar, Card, Row, Col } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Import du composant OCRCapture
import OCRCapture from './components/OCRCapture';

// Composants pour les modules
const OCR = () => <OCRCapture />;

const OBD2 = () => (
  <Container className="mt-4">
    <h2>Module OBD-II</h2>
    <Card>
      <Card.Body>
        <Card.Title>Diagnostic Véhicule</Card.Title>
        <Card.Text>
          Connectez-vous à votre véhicule via un dongle OBD-II pour obtenir des diagnostics en temps réel.
        </Card.Text>
        <button className="btn btn-primary">Connecter</button>
      </Card.Body>
    </Card>
  </Container>
);

const NLP = () => (
  <Container className="mt-4">
    <h2>Module NLP</h2>
    <Card>
      <Card.Body>
        <Card.Title>Assistant Automobile</Card.Title>
        <Card.Text>
          Posez vos questions en langage naturel sur votre véhicule ou les problèmes rencontrés.
        </Card.Text>
        <div className="mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="Ex: Que signifie le code erreur P0300 ?"
          />
        </div>
        <button className="btn btn-primary">Envoyer</button>
      </Card.Body>
    </Card>
  </Container>
);

const ImageRecognition = () => (
  <Container className="mt-4">
    <h2>Module Reconnaissance d'Image</h2>
    <Card>
      <Card.Body>
        <Card.Title>Diagnostic Visuel</Card.Title>
        <Card.Text>
          Envoyez une photo d'un composant ou d'un problème pour obtenir un diagnostic visuel.
        </Card.Text>
        <div className="mb-3">
          <input type="file" className="form-control" accept="image/*" />
        </div>
        <button className="btn btn-primary">Analyser</button>
      </Card.Body>
    </Card>
  </Container>
);

const ECUFlash = () => (
  <Container className="mt-4">
    <h2>Module ECU Flash</h2>
    <Card>
      <Card.Body>
        <Card.Title>Reprogrammation ECU</Card.Title>
        <Card.Text>
          Consultez et modifiez les cartographies de votre véhicule pour optimiser ses performances.
        </Card.Text>
        <button className="btn btn-primary">Consulter les Cartographies</button>
      </Card.Body>
    </Card>
  </Container>
);

const PartsFinder = () => (
  <Container className="mt-4">
    <h2>Module Parts Finder</h2>
    <Card>
      <Card.Body>
        <Card.Title>Recherche de Pièces</Card.Title>
        <Card.Text>
          Trouvez les pièces compatibles avec votre véhicule par catégorie ou recherche textuelle.
        </Card.Text>
        <div className="mb-3">
          <input type="text" className="form-control" placeholder="Ex: plaquettes frein..." />
        </div>
        <button className="btn btn-primary">Rechercher</button>
      </Card.Body>
    </Card>
  </Container>
);

// Page d'accueil avec des cartes pour chaque module
const Home = () => (
  <Container className="mt-4">
    <h1 className="text-center mb-4">Assistant Auto Ultime</h1>
    <Row>
      <Col md={4} className="mb-4">
        <Card>
          <Card.Body>
            <Card.Title>OCR</Card.Title>
            <Card.Text>Scanner de carte grise</Card.Text>
            <Link to="/ocr" className="btn btn-primary">Accéder</Link>
          </Card.Body>
        </Card>
      </Col>
      <Col md={4} className="mb-4">
        <Card>
          <Card.Body>
            <Card.Title>OBD-II</Card.Title>
            <Card.Text>Diagnostic véhicule</Card.Text>
            <Link to="/obd2" className="btn btn-primary">Accéder</Link>
          </Card.Body>
        </Card>
      </Col>
      <Col md={4} className="mb-4">
        <Card>
          <Card.Body>
            <Card.Title>NLP</Card.Title>
            <Card.Text>Assistant automobile</Card.Text>
            <Link to="/nlp" className="btn btn-primary">Accéder</Link>
          </Card.Body>
        </Card>
      </Col>
      <Col md={4} className="mb-4">
        <Card>
          <Card.Body>
            <Card.Title>Reconnaissance d'image</Card.Title>
            <Card.Text>Diagnostic visuel</Card.Text>
            <Link to="/image-recognition" className="btn btn-primary">Accéder</Link>
          </Card.Body>
        </Card>
      </Col>
      <Col md={4} className="mb-4">
        <Card>
          <Card.Body>
            <Card.Title>ECU Flash</Card.Title>
            <Card.Text>Reprogrammation ECU</Card.Text>
            <Link to="/ecu-flash" className="btn btn-primary">Accéder</Link>
          </Card.Body>
        </Card>
      </Col>
      <Col md={4} className="mb-4">
        <Card>
          <Card.Body>
            <Card.Title>Parts Finder</Card.Title>
            <Card.Text>Recherche de pièces</Card.Text>
            <Link to="/parts-finder" className="btn btn-primary">Accéder</Link>
          </Card.Body>
        </Card>
      </Col>
    </Row>
  </Container>
);

function App() {
  return (
    <Router>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand as={Link} to="/">Assistant Auto Ultime</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/ocr">OCR</Nav.Link>
              <Nav.Link as={Link} to="/obd2">OBD-II</Nav.Link>
              <Nav.Link as={Link} to="/nlp">NLP</Nav.Link>
              <Nav.Link as={Link} to="/image-recognition">Reconnaissance d'image</Nav.Link>
              <Nav.Link as={Link} to="/ecu-flash">ECU Flash</Nav.Link>
              <Nav.Link as={Link} to="/parts-finder">Parts Finder</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ocr" element={<OCR />} />
        <Route path="/obd2" element={<OBD2 />} />
        <Route path="/nlp" element={<NLP />} />
        <Route path="/image-recognition" element={<ImageRecognition />} />
        <Route path="/ecu-flash" element={<ECUFlash />} />
        <Route path="/parts-finder" element={<PartsFinder />} />
      </Routes>
    </Router>
  );
}

export default App;
