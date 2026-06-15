import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await register(email, password);
            // Auto login or redirect to login
            navigate('/login');
        } catch (err) {
            setError('Registration failed. Email might be taken.');
        }
    };

    return (
        <div className="auth-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="auth-card"
                style={{ background: '#111625', padding: '2rem', borderRadius: '8px', width: '400px', border: '1px solid #1a2138' }}
            >
                <h2 style={{ color: '#00f2ff', marginBottom: '1.5rem', textAlign: 'center' }}>NEW IDENTITY</h2>
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
                        style={{ width: '100%', padding: '0.75rem', background: 'transparent', border: '1px solid #00f2ff', color: '#00f2ff', fontWeight: 'bold', borderRadius: '4px' }}
                    >
                        CREATE RECORD
                    </button>
                </form>
                <p style={{ marginTop: '1rem', textAlign: 'center', color: '#94a3b8' }}>
                    Already registered? <Link to="/login" style={{ color: '#00f2ff' }}>Access System</Link>
                </p>
            </motion.div>
        </div>
    );
};

export default Register;
