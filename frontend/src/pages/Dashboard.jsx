import React from 'react';
import ParticleBackground from '../components/ParticleBackground';
import Header from '../components/Header';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
    const { user } = useAuth();

    return (
        <div style={{ position: 'relative', height: '100vh', width: '100vw', overflow: 'hidden' }}>
            <ParticleBackground />
            <Header />

            <div className="hero-content" style={{
                position: 'relative',
                zIndex: 5,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                textAlign: 'center',
                padding: '0 2rem'
            }}>
                <motion.h1
                    className="hero-title"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    style={{
                        fontSize: '4rem',
                        fontWeight: 800,
                        background: 'linear-gradient(90deg, #fff, #94a3b8)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        marginBottom: '1.5rem',
                        lineHeight: 1.1
                    }}
                >
                    DETECT AI-GENERATED<br />
                    <span style={{ color: '#00f2ff', WebkitTextFillColor: '#00f2ff' }}>MEDIA WITH PRECISION</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                    style={{
                        maxWidth: '600px',
                        fontSize: '1.2rem',
                        color: '#94a3b8',
                        marginBottom: '3rem',
                        lineHeight: 1.6
                    }}
                >
                    DeepMedia Check analyzes images to detect deepfakes and manipulated media
                    using advanced AI models. Secure your digital reality today.
                </motion.p>

                <motion.div
                    className="hero-buttons flex-col-mobile"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.5, delay: 0.8 }}
                    style={{ display: 'flex', gap: '1rem' }}
                >
                    {user ? (
                        <Link to="/upload" style={{
                            background: 'linear-gradient(90deg, #00f2ff, #00c8d4)',
                            color: '#000',
                            padding: '1rem 3rem',
                            fontSize: '1.2rem',
                            borderRadius: '30px',
                            fontWeight: 'bold',
                            boxShadow: '0 0 20px rgba(0, 242, 255, 0.4)',
                            display: 'inline-block'
                        }}>
                            CHECK IMAGE NOW &rarr;
                        </Link>
                    ) : (
                        <Link to="/login" style={{
                            background: 'transparent',
                            border: '2px solid #00f2ff',
                            color: '#00f2ff',
                            padding: '1rem 3rem',
                            fontSize: '1.2rem',
                            borderRadius: '30px',
                            fontWeight: 'bold',
                            boxShadow: '0 0 15px rgba(0, 242, 255, 0.2)',
                            display: 'inline-block'
                        }}>
                            LOGIN TO START
                        </Link>
                    )}
                </motion.div>

            </div>
        </div>
    );
};

export default Dashboard;
