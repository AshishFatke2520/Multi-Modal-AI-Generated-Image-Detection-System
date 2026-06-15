import React, { useState } from 'react';
import Header from '../components/Header';
import ImageUpload from '../components/ImageUpload';
import AnalysisLoader from '../components/AnalysisLoader';
import ResultsDashboard from '../components/ResultsDashboard';
import { analysisService } from '../services/api';

const CheckImage = () => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileSelect = (uploadedFile, previewUrl) => {
        setFile(uploadedFile);
        setPreview(previewUrl);
        setResult(null);
        setError(null);
    };

    const handleAnalyze = async () => {
        if (!file) return;
        setLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append('file', file);
            const response = await analysisService.uploadFusion(formData);
            setResult(response.data);
        } catch (err) {
            console.error(err);
            if (err.message && err.message.includes("401")) {
                setError("Session Expired: For security, please click PROFILE or LOGOUT at the top right and log back in.");
            } else {
                setError(err.message || "Analysis failed. Please check backend connection.");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
    };

    return (
        <div style={{ background: '#0a0e17', minHeight: '100vh', color: '#fff', paddingBottom: '3rem' }}>
            <Header />
            <div className="container" style={{ paddingTop: '100px', maxWidth: '1200px' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: '#00f2ff' }}>
                    IMAGE FORENSICS TOOL
                </h1>

                {!file && !result ? (
                    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                        <ImageUpload onFileSelect={handleFileSelect} />
                    </div>
                ) : (
                    <>
                        {/* Only show preview and buttons if no result yet */}
                        {!result && (
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ 
                                    marginBottom: '2rem', 
                                    borderRadius: '16px', 
                                    overflow: 'hidden', 
                                    boxShadow: '0 0 20px rgba(0, 242, 255, 0.2)',
                                    maxHeight: '400px',
                                    display: 'inline-block'
                                }}>
                                    <img src={preview} alt="Upload Preview" style={{ maxWidth: '100%', maxHeight: '400px', display: 'block' }} />
                                </div>
                                
                                {!loading && (
                                    <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
                                        <button onClick={handleAnalyze} style={{
                                            background: 'linear-gradient(90deg, #00f2ff, #00c8d4)',
                                            color: '#000', padding: '1rem 3rem', borderRadius: '30px', fontWeight: 'bold', fontSize: '1.2rem',
                                            boxShadow: '0 0 15px rgba(0, 242, 255, 0.4)'
                                        }}>
                                            START ANALYSIS
                                        </button>
                                        <button onClick={handleReset} style={{
                                            background: 'transparent', border: '1px solid #ff2a2a', color: '#ff2a2a',
                                            padding: '1rem 2rem', borderRadius: '30px', fontWeight: 'bold'
                                        }}>
                                            CANCEL
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </>
                )}

                {loading && <AnalysisLoader />}

                {error && (
                    <div style={{ marginTop: '2rem', padding: '1rem', background: 'rgba(255, 42, 42, 0.1)', border: '1px solid #ff2a2a', borderRadius: '8px', color: '#ff2a2a', textAlign: 'center' }}>
                        {error}
                    </div>
                )}

                {result && (
                    <ResultsDashboard result={result} onReset={handleReset} />
                )}
            </div>
        </div>
    );
};

export default CheckImage;
