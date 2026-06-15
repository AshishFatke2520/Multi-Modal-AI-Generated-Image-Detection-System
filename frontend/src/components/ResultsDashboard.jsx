import React from 'react';
import { motion } from 'framer-motion';
import SignalRadar from './SignalRadar';
import ConfidenceGauge from './ConfidenceGauge';
import SignalBarChart from './SignalBarChart';

const ResultsDashboard = ({ result, onReset }) => {
    if (!result) return null;

    const verdict = result.verdict || "Unknown";
    const confidence_score = result.final_score || 0;
    const signals = result.breakdown?.normalized_scores || { metadata: 0, artifacts: 0, classifier: 0 };
    const explanationText = typeof result.explanation === 'object' 
        ? result.explanation?.explanation_text 
        : result.explanation;

    return (
        <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{
                width: '100%',
                padding: '2rem',
                background: 'rgba(10, 14, 23, 0.8)',
                border: '1px solid #1a2138',
                borderRadius: '20px',
                backdropFilter: 'blur(10px)',
                marginTop: '2rem'
            }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '2rem' }}>

                {/* Left: Verdict & Gauge */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '250px' }}>
                    <h2 style={{
                        fontSize: '3rem',
                        margin: 0,
                        color: verdict === 'High' ? '#ff2a2a' : verdict === 'Medium' ? '#ffcc00' : '#00ff88',
                        textShadow: '0 0 20px rgba(0,0,0,0.5)'
                    }}>
                        {verdict.toUpperCase()}
                    </h2>
                    <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>SUSPICION LEVEL</p>
                    <ConfidenceGauge score={confidence_score} />
                    <div style={{ marginTop: '1.5rem', fontSize: '0.85rem', color: '#94a3b8', textAlign: 'center', maxWidth: '220px', lineHeight: '1.4' }}>
                        <span style={{ color: '#ffcc00' }}>Note:</span> A probability <strong>&gt; 50%</strong> suggests the image is likely fake (AI-generated or manipulated). Scores <strong>&lt; 50%</strong> indicate it is highly likely to be real.
                    </div>
                </div>

                {/* Center: Radar Chart */}
                <div style={{ flex: 1, minWidth: '300px', maxWidth: '400px' }}>
                    <h3 style={{ textAlign: 'center', color: '#e0e6ed', marginBottom: '1rem' }}>Signal Analysis</h3>
                    <SignalRadar signals={signals} />
                </div>

                {/* Right: Explanation */}
                <div style={{ flex: 1, minWidth: '250px', background: '#111625', padding: '1.5rem', borderRadius: '16px' }}>
                    <h3 style={{ color: '#00f2ff', marginBottom: '1rem' }}>AI Explanation</h3>
                    <p style={{ color: '#e0e6ed', lineHeight: '1.6', fontSize: '0.95rem' }}>
                        {explanationText || "The system analyzed metadata integrity, compression artifacts, and visual anomalies. Based on the fusion model, this image shows strong indicators of being AI-generated."}
                    </p>

                    {/* Metadata Table Snippet */}
                    <div style={{ marginTop: '1.5rem' }}>
                        <h4 style={{ color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase' }}>Key Metadata</h4>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '0.5rem' }}>
                            <div style={{ background: '#0a0e17', padding: '0.5rem', borderRadius: '4px', fontSize: '0.8rem', color: '#fff' }}>Software: Adobe Photoshop</div>
                            <div style={{ background: '#0a0e17', padding: '0.5rem', borderRadius: '4px', fontSize: '0.8rem', color: '#ff2a2a' }}>Missing EXIF</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Detailed Signal Bar Graph Comparison */}
            <SignalBarChart signals={signals} />

            <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <button
                    onClick={onReset}
                    style={{
                        background: 'transparent',
                        border: '1px solid #00f2ff',
                        color: '#00f2ff',
                        padding: '1rem 3rem',
                        borderRadius: '30px',
                        fontWeight: 'bold',
                        fontSize: '1rem',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease'
                    }}
                    onMouseOver={(e) => { e.target.style.background = 'rgba(0, 242, 255, 0.1)' }}
                    onMouseOut={(e) => { e.target.style.background = 'transparent' }}
                >
                    ANALYZE NEW IMAGE
                </button>
            </div>

        </motion.div>
    );
};

export default ResultsDashboard;
