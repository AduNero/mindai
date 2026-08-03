import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { authApi } from "@/api";
import { Spinner } from "@/components/common/Spinner";
import { extractErrorMessage } from "@/utils/errors";

type Status = "verifying" | "success" | "error";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<Status>("verifying");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Missing verification token.");
      return;
    }
    authApi
      .verifyEmail(token)
      .then(() => setStatus("success"))
      .catch((err) => {
        setStatus("error");
        setMessage(extractErrorMessage(err, "This verification link is invalid or expired."));
      });
  }, [token]);

  return (
    <div className="card animate-slide-up text-center">
      {status === "verifying" && (
        <>
          <Spinner />
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">Verifying your email...</p>
        </>
      )}
      {status === "success" && (
        <>
          <div className="text-4xl">✅</div>
          <h1 className="mt-4 text-xl font-bold text-gray-900 dark:text-white">Email verified</h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Your account is now fully active.</p>
          <Link to="/login" className="btn-primary mt-6 w-full">
            Continue to login
          </Link>
        </>
      )}
      {status === "error" && (
        <>
          <div className="text-4xl">⚠️</div>
          <h1 className="mt-4 text-xl font-bold text-gray-900 dark:text-white">Verification failed</h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{message}</p>
          <Link to="/login" className="btn-outline mt-6 w-full">
            Back to login
          </Link>
        </>
      )}
    </div>
  );
}
