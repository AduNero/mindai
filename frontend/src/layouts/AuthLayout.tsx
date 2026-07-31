import { Link, Outlet } from "react-router-dom";

import { ThemeToggle } from "@/components/common/ThemeToggle";

export function AuthLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50 dark:bg-gray-950">
      <header className="flex items-center justify-between px-4 py-4 sm:px-8">
        <Link to="/" className="flex items-center gap-2 text-lg font-bold text-brand-600">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">M</span>
          MindCare AI
        </Link>
        <ThemeToggle />
      </header>
      <main className="flex flex-1 items-center justify-center px-4 py-8">
        <div className="w-full max-w-md animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
