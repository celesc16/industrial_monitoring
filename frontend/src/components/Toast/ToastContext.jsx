import {
  createContext,
  useCallback,
  useContext,
  useState,
} from "react";

import ToastView from "./ToastView";

const ToastContext = createContext(null);

const TOAST_VISIBLE_MS = 4000;

let nextId = 1;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts((current) =>
      current.filter((toast) => toast.id !== id)
    );
  }, []);

  const showToast = useCallback(
    (message, type = "error") => {
      const id = nextId;
      nextId += 1;

      setToasts((current) => [
        ...current,
        { id, message, type },
      ]);

      window.setTimeout(() => dismiss(id), TOAST_VISIBLE_MS);
    },
    [dismiss]
  );

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      <ToastView toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);

  if (context === null) {
    throw new Error("useToast debe usarse dentro de un ToastProvider");
  }

  return context;
}