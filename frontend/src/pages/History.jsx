import React, { useEffect, useState } from 'react';
import Header from '../components/Header';
import { historyService } from '../services/api';
import { motion } from 'framer-motion';

const History = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await historyService.getAll();
                setHistory(response.data);
            } catch (error) {
                console.error("Failed to load history", error);
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const getVerdictColor = (verdict) => {
        if (verdict === 'High') return '#ff2a2a';
        if (verdict === 'Medium') return '#ffcc00';
        return '#00ff88';
    };

    return (
        <div style={{ background: '#0a0e17', minHeight: '100vh', color: '#fff', paddingBottom: '3rem' }}>
            <Header />
            <div className="container" style={{ paddingTop: '100px', maxWidth: '1000px' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: '#00f2ff' }}>
                    ANALYSIS HISTORY
                </h1>

                {loading ? (
                    <div style={{ textAlign: 'center', color: '#94a3b8' }}>Loading archives...</div>
                ) : history.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '3rem', background: 'rgba(255,255,255,0.05)', borderRadius: '16px' }}>
                        <h3 style={{ color: '#94a3b8' }}>No records found.</h3>
                        <p>Go to Dashboard to analyze your first image.</p>
                    </div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        style={{ background: '#111625', borderRadius: '16px', border: '1px solid #1a2138' }}
                    >
                        <div style={{ overflowX: 'auto', width: '100%' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '600px' }}>
                                <thead>
                                    <tr style={{ background: '#1a2138', textAlign: 'left' }}>
                                        <th style={{ padding: '1rem', color: '#94a3b8' }}>Date</th>
                                        <th style={{ padding: '1rem', color: '#94a3b8' }}>File Name</th>
                                        <th style={{ padding: '1rem', color: '#94a3b8' }}>Verdict</th>
                                        <th style={{ padding: '1rem', color: '#94a3b8' }}>Fake Probability</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {history.map((item) => (
                                        <tr key={item.id} style={{ borderBottom: '1px solid #1a2138' }}>
                                            <td style={{ padding: '1rem', whiteSpace: 'nowrap' }}>{new Date(item.timestamp).toLocaleString()}</td>
                                            <td style={{ padding: '1rem', color: '#e0e6ed' }}>{item.filename}</td>
                                            <td style={{ padding: '1rem' }}>
                                                <span style={{
                                                    color: getVerdictColor(item.verdict),
                                                    padding: '0.2rem 0.8rem',
                                                    border: `1px solid ${getVerdictColor(item.verdict)}`,
                                                    borderRadius: '12px',
                                                    fontSize: '0.8rem',
                                                    fontWeight: 'bold',
                                                    whiteSpace: 'nowrap'
                                                }}>
                                                    {item.verdict.toUpperCase()}
                                                </span>
                                            </td>
                                            <td style={{ padding: '1rem', fontWeight: 'bold' }}>
                                                {(item.final_score).toFixed(1)}%
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </motion.div>
                )}
            </div>
        </div>
    );
};

export default History;
