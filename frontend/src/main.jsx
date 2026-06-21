/**
 * Entry point bootstrap file for the entire Frontend React application.
 * Initializes the Virtual DOM tree and binds it natively to the HTML root container element.
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx';

createRoot(document.getElementById('root')).render(
  // StrictMode: Activates development-only checks and logs to catch bugs early
  <StrictMode>
    {/* Global State Context Hydration Layer Wrapper */}
    <AuthProvider>    
      <App />
    </AuthProvider>
  </StrictMode>,
)