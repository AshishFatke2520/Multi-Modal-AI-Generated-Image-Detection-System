import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

const Header = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <motion.header
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5 }}
            style={{
                position: 'fixed',
                top: 0,
                width: '100%',
                padding: '1.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                zIndex: 10,
                backdropFilter: 'blur(10px)',
                background: 'rgba(10, 14, 23, 0.7)'
            }}
            className="flex-col-mobile header-nav"
        >
            <div className="header-logo" style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fff', letterSpacing: '1px' }}>
                DEEP<span style={{ color: '#00f2ff' }}>MEDIA</span>CHECK
            </div>

            <nav className="flex-col-mobile" style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                <a href="#about" style={{ color: '#e0e6ed', fontSize: '0.9rem', fontWeight: 500 }}>ABOUT</a>

                {user ? (
                    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                        <Link to="/profile" style={{ color: '#00f2ff', textDecoration: 'none', fontWeight: 'bold' }}>
                            PROFILE
                        </Link>
                        <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid #ff2a2a', color: '#ff2a2a', padding: '0.5rem 1rem', borderRadius: '4px' }}>
                            LOGOUT
                        </button>
                    </div>
                ) : (
                    <div style={{ display: 'flex', gap: '1rem' }}>
                        <Link to="/login" style={{ color: '#e0e6ed', marginRight: '1rem' }}>LOGIN</Link>
                        <Link to="/register" style={{
                            background: '#00f2ff',
                            color: '#000',
                            padding: '0.5rem 1.5rem',
                            borderRadius: '20px',
                            fontWeight: 600,
                            fontSize: '0.9rem'
                        }}>
                            REGISTER
                        </Link>
                    </div>
                )}
            </nav>
        </motion.header>
    );
};

export default Header;
