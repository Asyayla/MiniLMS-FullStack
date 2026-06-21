/**
 * Lightweight utility to manually parse and decode signed JSON Web Tokens (JWT).
 * Extracts raw payload claims without introducing heavy external package dependencies.
 */
export const decodeToken = (token) => {
  try {
    const parts = token.split('.');
    
    // Structure Guard: Standard JWT parameters must explicitly contain 3 separate dot-delimited string vectors
    if (parts.length !== 3) {
      throw new Error('Invalid token format');
    }

    // Unpack the intermediate payload data frame segment containing user identity and role scopes attributes
    const payload = parts[1];
    
    // Execute browser-native Base64 decoding (atob) and deserialize the outcome plaintext directly into a JSON entity
    const decoded = JSON.parse(atob(payload));
    
    return decoded;
  } catch (error) {
    console.error('Token verification error caught in utility execution context:', error);
    return null;
  }
};