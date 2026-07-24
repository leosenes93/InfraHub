import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useContext, useState, type ReactNode } from "react";

import { type CurrentUser, fetchCurrentUser, login as loginRequest } from "@/api/auth";
import { clearStoredToken, getStoredToken, storeToken } from "@/api/client";

interface AuthContextValue {
  user: CurrentUser | undefined;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [hasToken, setHasToken] = useState(() => Boolean(getStoredToken()));

  const {
    data: user,
    isLoading,
    isFetching,
  } = useQuery({
    queryKey: ["current-user"],
    queryFn: fetchCurrentUser,
    enabled: hasToken,
    retry: false,
  });

  async function login(email: string, password: string) {
    const { access_token } = await loginRequest(email, password);
    storeToken(access_token);
    setHasToken(true);
    await queryClient.invalidateQueries({ queryKey: ["current-user"] });
  }

  function logout() {
    clearStoredToken();
    setHasToken(false);
    queryClient.removeQueries({ queryKey: ["current-user"] });
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading: hasToken && (isLoading || isFetching),
        isAuthenticated: hasToken && Boolean(user),
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de um AuthProvider");
  }
  return context;
}
