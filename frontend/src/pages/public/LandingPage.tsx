import { motion } from "framer-motion";
import { Link } from "react-router-dom";

const FEATURES = [
  { emoji: "😊", title: "Mood Tracking", description: "Log your mood in seconds and see how it trends over weeks and months." },
  { emoji: "📓", title: "Private Journaling", description: "Write freely in a journal that's private by default — search, tag, and delete entries any time." },
  { emoji: "🏷️", title: "Tentative Sentiment Label", description: "Each entry gets an AI-suggested positive/negative/neutral label you can accept, reject, or correct." },
  { emoji: "🆘", title: "Support Resources", description: "Emergency and crisis resources are always visible, never AI-gated, and never claim to monitor you in real time." },
];

const STEPS = [
  { step: "1", title: "Check in daily", description: "Log your mood and jot a quick journal entry — it takes under a minute." },
  { step: "2", title: "See a tentative label", description: "Each journal entry gets an AI-suggested sentiment label you can accept, reject, or correct." },
  { step: "3", title: "Watch your trend", description: "Your dashboard shows raw mood and journal data over time — no scores, no recommendations, just your own record." },
];

export default function LandingPage() {
  return (
    <div>
      <section className="relative overflow-hidden bg-gradient-to-b from-brand-50 to-white dark:from-gray-900 dark:to-gray-950">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mx-auto max-w-3xl text-center"
          >
            <span className="badge bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300">
              Mood &amp; Journal Log
            </span>
            <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-gray-900 sm:text-6xl dark:text-white">
              A private place to track<br className="hidden sm:block" /> your mood and thoughts.
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-lg text-gray-600 dark:text-gray-300">
              MindCare AI is a simple, pseudonymous mood and journaling log. Log your mood, write
              freely, and get a tentative AI sentiment label you can accept, reject, or correct —
              nothing more.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link to="/register" className="btn-primary px-6 py-3 text-base">
                Start for free
              </Link>
              <Link to="/features" className="btn-outline px-6 py-3 text-base">
                See how it works
              </Link>
            </div>
            <p className="mt-4 text-xs text-gray-400">
              Not a substitute for professional care. If you're in crisis, contact local emergency services.
            </p>
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">A bounded set of features, on purpose</h2>
          <p className="mt-3 text-gray-500 dark:text-gray-400">Mood, journaling, one tentative AI label, and support resources — nothing else.</p>
        </div>
        <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
              className="card"
            >
              <div className="text-3xl">{f.emoji}</div>
              <h3 className="mt-3 text-lg font-semibold text-gray-900 dark:text-gray-100">{f.title}</h3>
              <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">{f.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <section className="bg-gray-50 py-20 dark:bg-gray-900/40">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">How it works</h2>
          </div>
          <div className="mt-14 grid grid-cols-1 gap-8 sm:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.step} className="text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-brand-600 text-lg font-bold text-white">
                  {s.step}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900 dark:text-gray-100">{s.title}</h3>
                <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">{s.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-4 py-20 text-center sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Ready to check in with yourself?</h2>
        <p className="mt-3 text-gray-500 dark:text-gray-400">Free to get started. No credit card required.</p>
        <div className="mt-8">
          <Link to="/register" className="btn-primary px-8 py-3 text-base">
            Create your account
          </Link>
        </div>
      </section>
    </div>
  );
}
