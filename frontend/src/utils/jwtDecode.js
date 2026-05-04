// JWT token'dan user bilgisini decode etmek icin utility
export const decodeToken = (token) => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid token format');
    }

    // JWT token'in ortadaki kısmı (payload) base64 encode'lu
    const payload = parts[1];
    
    // Base64 decode
    const decoded = JSON.parse(atob(payload));
    
    return decoded;
  } catch (error) {
    console.error('Token decode hatası:', error);
    return null;
  }
};
