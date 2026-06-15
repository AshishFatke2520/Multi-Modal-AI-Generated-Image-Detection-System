import React, { useState } from 'react';
import Header from '../components/Header';
import { useAuth } from '../context/AuthContext';
import { historyService } from '../services/api';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [clearing, setClearing] = useState(false);
    const [message, setMessage] = useState('');

    const handleClearHistory = async () => {
        if (!window.confirm("Are you sure you want to permanently delete all your analysis history?")) return;
        
        setClearing(true);
        try {
            const res = await historyService.clearAll();
            setMessage(res.data.message);
        } catch (error) {
            console.error("Failed to clear history", error);
            setMessage("Failed to clear history. Please try again.");
        } finally {
            setClearing(false);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    if (!user) return null;

    return (
        <div style={{ background: '#0a0e17', minHeight: '100vh', color: '#fff', paddingBottom: '3rem' }}>
            <Header />
            <div className="container" style={{ paddingTop: '100px', maxWidth: '600px', margin: '0 auto' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '2rem', color: '#00f2ff' }}>
                    USER PROFILE
                </h1>

                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{ background: '#111625', padding: '2rem', borderRadius: '16px', border: '1px solid #1a2138' }}
                >
                    <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
                        <div style={{ 
                            width: '80px', height: '80px', borderRadius: '50%', background: '#1a2138', 
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            margin: '0 auto 1rem', fontSize: '2rem', color: '#00f2ff', border: '2px solid #00f2ff'
                        }}>
                            {user?.email ? user.email.charAt(0).toUpperCase() : '?'}
                        </div>
                        <h2 style={{ margin: 0 }}>{user?.email || 'Guest User'}</h2>
                        <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>DeepMediaCheck Investigator</p>
                    </div>

                    <div style={{ borderTop: '1px solid #1a2138', paddingTop: '2rem' }}>
                        <h3 style={{ marginBottom: '1rem', color: '#e0e6ed' }}>Account Management</h3>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <button 
                                onClick={handleClearHistory} 
                                disabled={clearing}
                                style={{ 
                                    background: 'transparent', border: '1px solid #ffcc00', color: '#ffcc00', 
                                    padding: '1rem', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer',
                                    transition: 'all 0.3s ease', opacity: clearing ? 0.5 : 1
                                }}
                            >
                                {clearing ? "CLEARING..." : "CLEAR ANALYSIS HISTORY"}
                            </button>

                            <button 
                                onClick={handleLogout} 
                                style={{ 
                                    background: 'transparent', border: '1px solid #ff2a2a', color: '#ff2a2a', 
                                    padding: '1rem', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer',
                                    transition: 'all 0.3s ease'
                                }}
                            >
                                LOGOUT ACCOUNT
                            </button>
                        </div>
                        {message && (
                            <div style={{ marginTop: '1rem', textAlign: 'center', color: '#00ff88', fontSize: '0.9rem' }}>
                                {message}
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default Profile;
