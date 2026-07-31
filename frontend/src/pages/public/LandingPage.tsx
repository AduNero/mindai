import { motion } from "framer-motion";
import { Link } from "react-router-dom";

const FEATURES = [
  { emoji: "😊", title: "Mood Tracking", description: "Log your mood in seconds and see how it trends over weeks and months." },
  { emoji: "📓", title: "Smart Journaling", description: "Write freely — AI sentiment analysis helps surface patterns you might miss." },
  { emoji: "💬", title: "AI Therapy Chat", description: "Talk things through anytime with an AI companion, with full conversation history." },
  { emoji: "🧠", title: "Validated Assessments", description: "PHQ-9, GAD-7, stress, burnout, and self-esteem screening — all in one place." },
  { emoji: "📅", title: "Counseling Appointments", description: "Book, reschedule, or cancel sessions with licensed counselors." },
  { emoji: "📈", title: "Wellness Score", description: "A single, explainable score combining mood, journaling, sleep, and more." },
];

const STEPS = [
  { step: "1", title: "Check in daily", description: "Log your mood and jot a quick journal entry — it takes under a minute." },
  { step: "2", title: "Get personalized insight", description: "AI analyzes your entries and assessment results to spot trends early." },
  { step: "3", title: "Take action", description: "Follow tailored recommendations, or book time with a counselor when it matters." },
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
              AI-Powered Mental Wellness
            </span>
            <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-gray-900 sm:text-6xl dark:text-white">
              Understand your mind,<br className="hidden sm:block" /> one day at a time.
            </h1>
            <p className="mx-auto mt-6 max-w-xl text-lg text-gray-600 dark:text-gray-300">
              MindCare AI helps you track your mood, journal with purpose, and get AI-informed
              support — so you can spot what's working before it becomes a problem.
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
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Everything you need to stay on top of your mental health</h2>
          <p className="mt-3 text-gray-500 dark:text-gray-400">One platform for tracking, reflection, AI support, and professional care.</p>
        </div>
        <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
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
