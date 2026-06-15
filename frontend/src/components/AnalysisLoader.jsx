import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const AnalysisLoader = () => {
    const [step, setStep] = useState(0);
    const steps = [
        "Initializing Neural Networks...",
        "Extracting Metadata Signals...",
        "Scanning for Compression Artifacts...",
        "Running Frequency Analysis...",
        "Generating Explanations..."
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
        }, 1500);
        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ textAlign: 'center', marginTop: '3rem' }}>
            <div style={{
                width: '60px',
                height: '60px',
                border: '4px solid rgba(0, 242, 255, 0.3)',
                borderTop: '4px solid #00f2ff',
                borderRadius: '50%',
                margin: '0 auto 2rem',
                animation: 'spin 1s linear infinite'
            }} />
            <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>

            <motion.h3
                key={step}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                style={{ color: '#00f2ff', fontSize: '1.2rem' }}
            >
                {steps[step]}
            </motion.h3>
        </div>
    );
};

export default AnalysisLoader;
