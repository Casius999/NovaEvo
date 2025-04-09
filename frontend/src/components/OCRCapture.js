import React, { useState, useRef, useEffect } from 'react';
import { Container, Card, Button, Row, Col, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';

const OCRCapture = () => {
  const [stream, setStream] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [ocrResult, setOcrResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Initialiser et nettoyer le stream de la caméra
  useEffect(() => {
    const initCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'environment' } // Utiliser la caméra arrière si disponible
        });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (err) {
        console.error("Erreur d'accès à la caméra:", err);
        setError("Impossible d'accéder à la caméra. Veuillez vérifier les permissions.");
      }
    };

    initCamera();

    return () => {
      // Nettoyer le stream quand le composant est démonté
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Capturer l'image depuis la vidéo
  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      // Définir les dimensions du canvas pour correspondre à celles de la vidéo
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      // Dessiner l'image sur le canvas
      context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      // Convertir en URL de données
      const imageDataURL = canvas.toDataURL('image/jpeg', 0.8);
      setCapturedImage(imageDataURL);
      setOcrResult(null); // Réinitialiser les résultats précédents
    }
  };

  // Réinitialiser et reprendre la capture
  const resetCapture = () => {
    setCapturedImage(null);
    setOcrResult(null);
  };

  // Envoyer l'image au backend pour analyse OCR
  const analyzeImage = async () => {
    if (!capturedImage) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Convertir l'URL de données en Blob
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      
      // Créer un objet FormData
      const formData = new FormData();
      formData.append('image', blob, 'carte_grise.jpg');
      
      // Envoyer l'image au backend
      const result = await axios.post('/ocr', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setOcrResult(result.data);
    } catch (err) {
      console.error("Erreur lors de l'analyse OCR:", err);
      setError("Erreur lors de l'analyse de l'image. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  // Formater les résultats OCR pour l'affichage
  const renderOcrResults = () => {
    if (!ocrResult) return null;
    
    if (ocrResult.error) {
      return <Alert variant="danger">{ocrResult.error}</Alert>;
    }

    // Afficher les informations du véhicule si disponibles
    if (ocrResult.vehicle_info) {
      const { registration, make, model, vin, first_registration_date, owner } = ocrResult.vehicle_info;
      
      return (
        <Card className="mt-3">
          <Card.Header as="h5">Informations détectées</Card.Header>
          <Card.Body>
            <Row>
              <Col md={6}>
                <p><strong>Immatriculation:</strong> {registration || 'Non détecté'}</p>
                <p><strong>Marque:</strong> {make || 'Non détecté'}</p>
                <p><strong>Modèle:</strong> {model || 'Non détecté'}</p>
              </Col>
              <Col md={6}>
                <p><strong>N° de série (VIN):</strong> {vin || 'Non détecté'}</p>
                <p><strong>Date de 1ère immatriculation:</strong> {first_registration_date || 'Non détecté'}</p>
                <p><strong>Propriétaire:</strong> {owner || 'Non détecté'}</p>
              </Col>
            </Row>
            <Alert variant="info">
              Ces informations ont été extraites automatiquement. Veuillez vérifier leur exactitude.
            </Alert>
          </Card.Body>
        </Card>
      );
    }
    
    // Affichage par défaut si aucune information spécifique n'a été extraite
    return (
      <Alert variant="warning">
        L'analyse OCR a été effectuée, mais aucune information de carte grise n'a pu être extraite avec certitude. 
        Veuillez réessayer avec une meilleure image.
      </Alert>
    );
  };

  return (
    <Container className="my-4">
      <h2 className="mb-4">Scanner de Carte Grise</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card>
        <Card.Body>
          {!capturedImage ? (
            // Affichage du flux vidéo pour la capture
            <div className="text-center">
              <div className="position-relative d-inline-block">
                <video 
                  ref={videoRef} 
                  autoPlay 
                  playsInline 
                  className="img-fluid rounded" 
                  style={{ maxWidth: '100%', maxHeight: '60vh' }}
                />
                <div className="position-absolute" style={{ top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none' }}>
                  <div className="h-100 d-flex align-items-center justify-content-center">
                    <div style={{ 
                      border: '2px dashed white', 
                      width: '80%', 
                      height: '65%', 
                      boxShadow: '0 0 0 1000px rgba(0,0,0,0.4)',
                      borderRadius: '5px'
                    }}></div>
                  </div>
                </div>
              </div>
              <p className="text-muted mt-2">Alignez votre carte grise dans le cadre</p>
              <Button variant="primary" onClick={captureImage} className="mt-2">
                <i className="bi bi-camera"></i> Prendre la photo
              </Button>
            </div>
          ) : (
            // Affichage de l'image capturée
            <div className="text-center">
              <img 
                src={capturedImage} 
                alt="Carte grise capturée" 
                className="img-fluid rounded" 
                style={{ maxWidth: '100%', maxHeight: '60vh' }}
              />
              <div className="mt-3">
                <Button variant="secondary" onClick={resetCapture} className="me-2">
                  <i className="bi bi-arrow-counterclockwise"></i> Reprendre
                </Button>
                <Button 
                  variant="success" 
                  onClick={analyzeImage} 
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Analyse en cours...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-search"></i> Analyser la carte grise
                    </>
                  )}
                </Button>
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
      
      {/* Canvas caché pour capturer l'image */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      
      {/* Affichage des résultats OCR */}
      {ocrResult && renderOcrResults()}
      
      {/* Conseils pour une meilleure capture */}
      <Card className="mt-4">
        <Card.Header>Conseils pour une meilleure capture</Card.Header>
        <Card.Body>
          <ul>
            <li>Assurez-vous que la lumière est suffisante</li>
            <li>Évitez les reflets sur la carte grise</li>
            <li>Capturez l'ensemble de la carte grise</li>
            <li>Maintenez l'appareil stable lors de la prise de photo</li>
          </ul>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default OCRCapture;
