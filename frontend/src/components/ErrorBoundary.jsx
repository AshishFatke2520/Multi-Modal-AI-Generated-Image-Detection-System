import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // You can also log the error to an error reporting service
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div style={{
            minHeight: '100vh',
            background: '#0a0e17',
            color: '#fff',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            padding: '2rem'
        }}>
          <h1 style={{ color: '#ff2a2a', fontSize: '3rem', marginBottom: '1rem' }}>SYSTEM MALFUNCTION</h1>
          <p style={{ color: '#94a3b8', maxWidth: '600px', marginBottom: '2rem' }}>
            We encountered an unexpected error rendering this view. The neural link has been temporarily severed.
          </p>
          <pre style={{
              background: '#111625',
              padding: '1rem',
              borderRadius: '8px',
              border: '1px solid #1a2138',
              color: '#ffcc00',
              overflowX: 'auto',
              maxWidth: '800px',
              textAlign: 'left',
              fontSize: '0.9rem'
          }}>
              {this.state.error?.toString()}
          </pre>
          <button
            onClick={() => window.location.href = '/'}
            style={{
                marginTop: '2rem',
                background: '#00f2ff',
                color: '#000',
                padding: '1rem 3rem',
                borderRadius: '30px',
                fontWeight: 'bold',
                cursor: 'pointer'
            }}
          >
            RETURN TO DASHBOARD
          </button>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;
