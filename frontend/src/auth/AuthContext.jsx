import {
  createContext,
  useCallback,
  useContext,
  useState,
} from "react";

import {
  DEMO_CREDENTIALS,
  clearSession,
  loadSession,
  login,
  saveSession,
} from "./auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => loadSession());

  const loginAs = useCallback(async (role) => {
    const credentials = DEMO_CREDENTIALS[role];

    if (!credentials) {
      throw new Error(`Rol no soportado: ${role}`);
    }

    const nextSession = await login(credentials);

    saveSession(nextSession);
    setSession(nextSession);

    return nextSession;
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setSession(null);
  }, []);

  return (
    <AuthContext.Provider value={{ session, loginAs, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (context === null) {
    throw new Error("useAuth debe usarse dentro de un AuthProvider");
  }

  return context;
}