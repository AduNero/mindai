import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          <div className="col-span-2">
            <p className="flex items-center gap-2 text-lg font-bold text-brand-600">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
                M
              </span>
              MindCare AI
            </p>
            <p className="mt-3 max-w-sm text-sm text-gray-500 dark:text-gray-400">
              A private, pseudonymous mood and journal log with one AI feature: a tentative
              sentiment label on your entries. Not a substitute for professional care — if you're
              in crisis, contact local emergency services.
            </p>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">Product</p>
            <ul className="mt-3 space-y-2 text-sm text-gray-500 dark:text-gray-400">
              <li><Link to="/features" className="hover:text-brand-600">Features</Link></li>
              <li><Link to="/faq" className="hover:text-brand-600">FAQ</Link></li>
              <li><Link to="/privacy" className="hover:text-brand-600">Privacy notice</Link></li>
            </ul>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">Company</p>
            <ul className="mt-3 space-y-2 text-sm text-gray-500 dark:text-gray-400">
              <li><Link to="/about" className="hover:text-brand-600">About</Link></li>
              <li><Link to="/contact" className="hover:text-brand-600">Contact</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-10 border-t border-gray-200 pt-6 text-xs text-gray-400 dark:border-gray-800">
          &copy; {new Date().getFullYear()} MindCare AI. Final-year academic project — not a licensed
          medical service.
        </div>
      </div>
    </footer>
  );
}
