import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if token exists in localStorage
        const token = localStorage.getItem('token');
        if (token) {
            // Ideally verify token validity here, for now assume valid if present
            setUser({ token });
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const response = await authService.login({ email, password });
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        setUser({ token: access_token });
        return true;
    };

    const register = async (email, password) => {
        await authService.register({ email, password });
        return true; // Redirect to login after register
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
