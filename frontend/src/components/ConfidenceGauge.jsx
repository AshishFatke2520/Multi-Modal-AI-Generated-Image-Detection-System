import React from 'react';
import { motion } from 'framer-motion';

const ConfidenceGauge = ({ score }) => {
    // Score from backend is already 0 to 100
    const percentage = score > 1 ? score : score * 100;

    // Determine color based on score
    const getColor = (p) => {
        if (p < 30) return '#00ff88'; // Safe
        if (p < 70) return '#ffcc00'; // Warning
        return '#ff2a2a'; // Danger
    };

    const color = getColor(percentage);

    return (
        <div style={{ position: 'relative', width: '200px', height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="100%" height="100%" viewBox="0 0 100 100">
                <circle
                    cx="50" cy="50" r="45"
                    fill="transparent"
                    stroke="#1a2138"
                    strokeWidth="8"
                />
                <motion.circle
                    cx="50" cy="50" r="45"
                    fill="transparent"
                    stroke={color}
                    strokeWidth="8"
                    strokeDasharray="283" // 2 * pi * 45
                    strokeDashoffset="283"
                    transform="rotate(-90 50 50)"
                    animate={{ strokeDashoffset: 283 - (283 * percentage) / 100 }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    style={{ strokeLinecap: 'round' }}
                />
            </svg>
            <div style={{ position: 'absolute', textAlign: 'center' }}>
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                    style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#fff' }}
                >
                    {percentage.toFixed(2)}%
                </motion.div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>FAKE PROBABILITY</div>
            </div>
        </div>
    );
};

export default ConfidenceGauge;
