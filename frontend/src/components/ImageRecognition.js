import React, { useState, useRef } from 'react';
import { Container, Card, Button, Form, Alert, Spinner, Row, Col, Badge } from 'react-bootstrap';
import axios from 'axios';

const ImageRecognition = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisType, setAnalysisType] = useState('standard'); // 'standard' ou 'advanced'
  const fileInputRef = useRef(null);

  // Gérer la sélection de fichier
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setAnalysisResults(null); // Réinitialiser les résultats précédents
      setError(null);
    }
  };

  // Analyser l'image
  const analyzeImage = async () => {
    if (!selectedFile) return;

    try {
      setLoading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('image', selectedFile);
      
      // Ajouter le type d'analyse comme paramètre de requête
      const response = await axios.post(`/image_recognition?type=${analysisType}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setAnalysisResults(response.data);
    } catch (err) {
      console.error("Erreur lors de l'analyse de l'image:", err);
      setError("Une erreur s'est produite lors de l'analyse. Veuillez réessayer avec une autre image.");
    } finally {
      setLoading(false);
    }
  };

  // Réinitialiser l'état
  const resetImage = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setAnalysisResults(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Utiliser l'appareil photo (pour les appareils mobiles)
  const useCamera = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Formatter les résultats d'analyse
  const renderAnalysisResults = () => {
    if (!analysisResults) return null;
    
    // Vérifier s'il y a une erreur
    if (analysisResults.error) {
      return <Alert variant="danger">{analysisResults.error}</Alert>;
    }
    
    // Vérifier le format des résultats
    const labels = analysisResults.labels || [];
    const detections = analysisResults.detections || [];
    const anomalies = analysisResults.anomalies || [];
    
    return (
      <Card className="mt-3">
        <Card.Header as="h5">Résultats de l'analyse</Card.Header>
        <Card.Body>
          {/* Afficher les labels détectés */}
          {labels.length > 0 && (
            <div className="mb-4">
              <h5>Éléments détectés:</h5>
              <div className="d-flex flex-wrap gap-2 mb-3">
                {labels.map((label, index) => (
                  <Badge 
                    key={index} 
                    bg="primary" 
                    className="p-2"
                    style={{ fontSize: '1rem' }}
                  >
                    {label.description || label.name || label} 
                    {label.score && ` (${Math.round(label.score * 100)}%)`}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          
          {/* Afficher les éventuelles anomalies */}
          {anomalies.length > 0 && (
            <div className="mb-4">
              <h5>Anomalies potentielles:</h5>
              <Alert variant="warning">
                <ul className="mb-0">
                  {anomalies.map((anomaly, index) => (
                    <li key={index}>{anomaly.description || anomaly}</li>
                  ))}
                </ul>
              </Alert>
            </div>
          )}
          
          {/* Afficher les détections spécifiques */}
          {detections.length > 0 && (
            <div>
              <h5>Détections spécifiques:</h5>
              <ul>
                {detections.map((detection, index) => (
                  <li key={index}>
                    <strong>{detection.name || 'Élément'}</strong>: {detection.description || 'Détecté'}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Afficher un diagnostic si disponible */}
          {analysisResults.diagnostic && (
            <Alert variant="info" className="mt-3">
              <h5>Diagnostic préliminaire:</h5>
              <p>{analysisResults.diagnostic}</p>
            </Alert>
          )}
          
          {/* Recommandations éventuelles */}
          {analysisResults.recommendations && (
            <div className="mt-3">
              <h5>Recommandations:</h5>
              <ul>
                {Array.isArray(analysisResults.recommendations) ? 
                  analysisResults.recommendations.map((rec, index) => <li key={index}>{rec}</li>) : 
                  <li>{analysisResults.recommendations}</li>
                }
              </ul>
            </div>
          )}
        </Card.Body>
      </Card>
    );
  };

  return (
    <Container className="my-4">
      <h2 className="mb-4">Analyse Visuelle</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Card>
        <Card.Body>
          <Row>
            <Col md={6}>
              {/* Zone de sélection de fichier */}
              <div className="mb-3">
                <Form.Group>
                  <Form.Label>Sélectionnez une image du composant ou du problème</Form.Label>
                  <Form.Control 
                    ref={fileInputRef}
                    type="file" 
                    accept="image/*"
                    onChange={handleFileChange}
                    className="mb-2"
                  />
                </Form.Group>
                <div className="d-flex gap-2">
                  <Button variant="secondary" onClick={useCamera}>
                    <i className="bi bi-camera"></i> Utiliser l'appareil photo
                  </Button>
                  {previewUrl && (
                    <Button variant="outline-danger" onClick={resetImage}>
                      <i className="bi bi-trash"></i> Supprimer
                    </Button>
                  )}
                </div>
              </div>

              {/* Options d'analyse */}
              <Form.Group className="mb-3">
                <Form.Label>Type d'analyse</Form.Label>
                <div>
                  <Form.Check
                    inline
                    type="radio"
                    id="standard-analysis"
                    label="Standard"
                    name="analysisType"
                    value="standard"
                    checked={analysisType === 'standard'}
                    onChange={() => setAnalysisType('standard')}
                  />
                  <Form.Check
                    inline
                    type="radio"
                    id="advanced-analysis"
                    label="Avancée"
                    name="analysisType"
                    value="advanced"
                    checked={analysisType === 'advanced'}
                    onChange={() => setAnalysisType('advanced')}
                  />
                </div>
                <Form.Text className="text-muted">
                  L'analyse avancée permet de détecter les anomalies et d'obtenir un diagnostic plus précis.
                </Form.Text>
              </Form.Group>

              {/* Bouton d'analyse */}
              <Button 
                variant="primary" 
                onClick={analyzeImage} 
                disabled={!selectedFile || loading}
                className="w-100"
              >
                {loading ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Analyse en cours...
                  </>
                ) : (
                  'Analyser l\'image'
                )}
              </Button>
            </Col>
            
            <Col md={6}>
              {/* Aperçu de l'image */}
              <div className="preview-container text-center">
                {previewUrl ? (
                  <img 
                    src={previewUrl} 
                    alt="Aperçu" 
                    className="img-fluid rounded" 
                    style={{ maxHeight: '300px', maxWidth: '100%' }}
                  />
                ) : (
                  <div 
                    className="border rounded d-flex align-items-center justify-content-center"
                    style={{ height: '300px', backgroundColor: '#f8f9fa' }}
                  >
                    <p className="text-muted">Aucune image sélectionnée</p>
                  </div>
                )}
              </div>
            </Col>
          </Row>
        </Card.Body>
      </Card>
      
      {/* Affichage des résultats d'analyse */}
      {renderAnalysisResults()}
      
      {/* Conseils pour de meilleures analyses */}
      <Card className="mt-4">
        <Card.Header>Conseils pour de meilleures analyses</Card.Header>
        <Card.Body>
          <ul>
            <li>Assurez-vous que l'élément à analyser est bien visible et centré</li>
            <li>Prenez la photo avec un bon éclairage</li>
            <li>Évitez les reflets et les ombres fortes</li>
            <li>Pour les pièces mécaniques, nettoyez-les avant de les photographier</li>
            <li>Si possible, incluez plusieurs angles du même problème</li>
          </ul>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default ImageRecognition;