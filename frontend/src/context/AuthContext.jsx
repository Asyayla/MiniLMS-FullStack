import { createContext, useState, useContext, useEffect } from 'react';
import { decodeToken } from '../utils/jwtDecode';

// Create a global communication channel to share authentication state across the component tree
const AuthContext = createContext();

/**
 * Authentication State Provider component.
 * Synchronizes local component state with localStorage layers to preserve user sessions.
 */
export const AuthProvider = ({ children }) => {
     const [token, setToken] = useState(localStorage.getItem('token'));
     const [user, setUser] = useState(() => {
          const savedUser = localStorage.getItem('user');
          const savedToken = localStorage.getItem('token');
          
          // Use the persisted user metadata profile if it is explicitly cached in localStorage
          if (savedUser) {
               return JSON.parse(savedUser);
          }
          
          // Session Recovery Fallback: Decode claims directly from the cached JWT if user object is missing
          if (savedToken) {
               const decodedToken = decodeToken(savedToken);
               if (decodedToken) {
                    return {
                         username: decodedToken.sub || "User",
                         role: decodedToken.role || "student",
                         user_id: decodedToken.user_id || null,
                    };
               }
          }
          
          return null;
     });

     const login = (userData, userToken) => {
          // Dynamic Hydration Guard: Extract user attributes from claims if missing in payload
          let userToSave = { ...userData };
          if (!userToSave.role && userToken) {
               const decodedToken = decodeToken(userToken);
               userToSave.role = decodedToken?.role || "student";
               userToSave.user_id = userToSave.user_id || decodedToken?.user_id;
          }
          
          // Update volatile application state boundaries
          setToken(userToken);
          setUser(userToSave);
          
          // Persist credentials securely down into browser local storage layers
          localStorage.setItem('token', userToken);
          localStorage.setItem('user', JSON.stringify(userToSave));
          localStorage.setItem('role', userToSave.role); 
          localStorage.setItem('user_id', userToSave.user_id); 
          
          console.log("Session authenticated successfully:", userToSave);
     };

     // Debug operational lifecycle tracker: log token/user mutations
     useEffect(() => {
          console.log('AuthContext changed - token:', token, 'user:', user);
     }, [token, user]);

     const logout = () => {
          // Flush intermediate state records entirely
          setToken(null);
          setUser(null);
          
          // Purge keys systematically to close active security contexts
          localStorage.removeItem('token'); 
          localStorage.removeItem('user');
          localStorage.removeItem('role');
          localStorage.removeItem('user_id');
     };

     return (
          <AuthContext.Provider value={{ user, token, login, logout }}>
               {children}
          </AuthContext.Provider>
     );
}

// Custom abstraction hook shortcut for consuming authentication contexts safely inside pages
export const useAuth = () => useContext(AuthContext);