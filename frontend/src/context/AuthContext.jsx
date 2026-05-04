import { createContext, useState, useContext, useEffect } from 'react';
import { decodeToken } from '../utils/jwtDecode';

//1. bir iletisim kanali olusturuyoruz. bu kanal sayesinde uygulamanin herhangi bir yerinden kullanici bilgilerine erisebilecegiz.
const AuthContext = createContext();

//bu provider, uygulamanin herhangi bir yerinde kullanici bilgilerine erisebilmemizi saglar. 
export const AuthProvider = ({ children }) => {
     const [token, setToken] = useState(localStorage.getItem('token'));
     const [user, setUser] = useState(() => {
          const savedUser = localStorage.getItem('user');
          const savedToken = localStorage.getItem('token');
          
          // Eğer localStorage'da user varsa onu kullan
          if (savedUser) {
               return JSON.parse(savedUser);
          }
          
          // Eğer token varsa ama user yoksa, token'dan user'i decode et
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

     //giris yapma fonksiyonu
     const login = (userData, userToken) => {
          // Eğer role yoksa, token'dan decode et
          let userToSave = { ...userData };
          if (!userToSave.role && userToken) {
               const decodedToken = decodeToken(userToken);
               userToSave.role = decodedToken?.role || "student";
               userToSave.user_id = userToSave.user_id || decodedToken?.user_id;
          }
          
          setToken(userToken);
          setUser(userToSave);
          localStorage.setItem('token', userToken);
          localStorage.setItem('user', JSON.stringify(userToSave));
          localStorage.setItem('role', userToSave.role); // role bilgisini de ayri kaydet
          localStorage.setItem('user_id', userToSave.user_id); // user_id bilgisini de ayri kaydet
          
            console.log("User başarıyla giriş yaptı:", userToSave);
     };

     // Debug: log token/user changes
     useEffect(() => {
          console.log('AuthContext changed - token:', token, 'user:', user);
     }, [token, user]);

     //cikis yapma fonksiyonu
     const logout = () => {
          setToken(null);
          setUser(null);
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

//diger sayfalarda bu bilgilere kolayca ulasmak icin bir kisayol
export const useAuth = () => useContext(AuthContext);