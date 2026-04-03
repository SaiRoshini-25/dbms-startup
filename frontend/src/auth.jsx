import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { apiRequest, clearStoredAuth } from "./api";

const AuthContext = createContext(null);

function decodeTokenClaims(token) {
  if (!token) return null;
  try {
    const [, payload] = token.split(".");
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
    return JSON.parse(window.atob(padded));
  } catch {
    return null;
  }
}

function isExpired(claims) {
  if (!claims?.exp) return false;
  return claims.exp * 1000 <= Date.now();
}

function getInitialUser() {
  const token = window.sessionStorage.getItem("accessToken") || window.localStorage.getItem("accessToken");
  const stored = window.sessionStorage.getItem("currentUser") || window.localStorage.getItem("currentUser");
  if (!token || !stored) return null;

  try {
    const parsedUser = JSON.parse(stored);
    const claims = decodeTokenClaims(token);
    if (!claims || isExpired(claims)) {
      clearStoredAuth();
      return null;
    }

    return {
      ...parsedUser,
      email: claims.email || parsedUser.email,
      role: claims.role || parsedUser.role
    };
  } catch {
    clearStoredAuth();
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getInitialUser);

  useEffect(() => {
    function handleUnauthorized() {
      setUser(null);
    }

    window.addEventListener("auth:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("auth:unauthorized", handleUnauthorized);
  }, []);

  const value = useMemo(
    () => ({
      user,
      async login(credentials) {
        const response = await apiRequest("/auth/login", {
          method: "POST",
          body: JSON.stringify(credentials)
        });
        window.sessionStorage.setItem("accessToken", response.accessToken);
        window.sessionStorage.setItem("currentUser", JSON.stringify(response.user));
        window.localStorage.removeItem("accessToken");
        window.localStorage.removeItem("currentUser");
        setUser(response.user);
      },
      async register(payload) {
        await apiRequest("/auth/register", {
          method: "POST",
          body: JSON.stringify(payload)
        });
      },
      logout() {
        clearStoredAuth();
        setUser(null);
      }
    }),
    [user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
