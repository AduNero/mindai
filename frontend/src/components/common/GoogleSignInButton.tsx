import { useEffect, useRef } from "react";

interface GoogleCredentialResponse {
  credential: string;
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: GoogleCredentialResponse) => void;
          }) => void;
          renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
        };
      };
    };
  }
}

// Loaded once per page and reused — Google Identity Services renders its
// own button UI into the target element, no npm package needed.
let scriptLoadPromise: Promise<void> | null = null;

function loadGoogleIdentityScript(): Promise<void> {
  if (window.google?.accounts?.id) return Promise.resolve();
  if (!scriptLoadPromise) {
    scriptLoadPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Failed to load Google Sign-In."));
      document.head.appendChild(script);
    });
  }
  return scriptLoadPromise;
}

interface GoogleSignInButtonProps {
  onSuccess: (credential: string) => void;
  onError?: (message: string) => void;
}

/**
 * Renders nothing if VITE_GOOGLE_CLIENT_ID isn't set, so pages using this
 * don't need their own conditional — it degrades cleanly for anyone
 * running the app without Google Sign-In configured.
 */
export function GoogleSignInButton({ onSuccess, onError }: GoogleSignInButtonProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  useEffect(() => {
    if (!clientId || !containerRef.current) return;

    let cancelled = false;
    loadGoogleIdentityScript()
      .then(() => {
        if (cancelled || !containerRef.current || !window.google) return;
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: (response) => onSuccess(response.credential),
        });
        window.google.accounts.id.renderButton(containerRef.current, {
          theme: "outline",
          size: "large",
          width: 336,
          text: "continue_with",
        });
      })
      .catch((err) => onError?.(err instanceof Error ? err.message : "Failed to load Google Sign-In."));

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- onSuccess/onError are recreated each render; re-initializing the GIS button on every keystroke elsewhere on the page would just re-render the same button.
  }, [clientId]);

  if (!clientId) return null;

  return <div ref={containerRef} className="flex justify-center" />;
}
