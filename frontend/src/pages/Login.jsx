import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await login(email, password);
            navigate('/dashboard');
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    return (
        <div className="auth-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="auth-card"
                style={{ background: '#111625', padding: '2rem', borderRadius: '8px', width: '400px', border: '1px solid #1a2138' }}
            >
                <h2 style={{ color: '#00f2ff', marginBottom: '1.5rem', textAlign: 'center' }}>SYSTEM ACCESS</h2>
                {error && <p style={{ color: '#ff2a2a', marginBottom: '1rem' }}>{error}</p>}
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', color: '#94a3b8', marginBottom: '0.5rem' }}>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            style={{ width: '100%', padding: '0.75rem', background: '#0a0e17', border: '1px solid #1a2138', color: '#fff', borderRadius: '4px' }}
                            required
                        />
                    </div>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <label style={{ display: 'block', color: '#94a3b8', marginBottom: '0.5rem' }}>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            style={{ width: '100%', padding: '0.75rem', background: '#0a0e17', border: '1px solid #1a2138', color: '#fff', borderRadius: '4px' }}
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        style={{ width: '100%', padding: '0.75rem', background: '#00f2ff', color: '#000', fontWeight: 'bold', borderRadius: '4px' }}
                    >
                        INITIATE SESSION
                    </button>
                </form>
                <p style={{ marginTop: '1rem', textAlign: 'center', color: '#94a3b8' }}>
                    New User? <Link to="/register" style={{ color: '#00f2ff' }}>Register Identity</Link>
                </p>
            </motion.div>
        </div>
    );
};

export default Login;
