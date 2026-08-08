const VALUES = [
  { title: "Bounded scope", description: "One AI feature — a tentative sentiment label — not a general AI assistant or a clinical tool." },
  { title: "Privacy-first", description: "Pseudonymous by design. Journals are private by default and never sold or shared." },
  { title: "Never a substitute for care", description: "Support resources are always visible, and we're always clear this app isn't therapy, diagnosis, or emergency response." },
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <span className="badge bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300">About Us</span>
      <h1 className="mt-4 text-4xl font-extrabold text-gray-900 dark:text-white">
        A small, bounded self-monitoring tool
      </h1>
      <p className="mt-6 text-lg text-gray-600 dark:text-gray-300">
        MindCare AI started as a final-year IT project. Its scope is deliberately narrow: a
        pseudonymous mood and journal log with exactly one AI/ML component — a three-class
        sentiment classifier (TF-IDF + logistic regression) trained and evaluated on a public
        benchmark dataset. That's it.
      </p>
      <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
        MindCare AI is <strong>not a diagnostic tool, not therapy, and not a replacement for a
        licensed mental health professional</strong>. It's a private log for everyday
        self-awareness, with support resources always visible and never gated behind AI output.
      </p>

      <div className="mt-14 grid grid-cols-1 gap-6 sm:grid-cols-3">
        {VALUES.map((v) => (
          <div key={v.title} className="card">
            <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100">{v.title}</h3>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{v.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
