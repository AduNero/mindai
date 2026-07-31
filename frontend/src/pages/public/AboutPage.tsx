const VALUES = [
  { title: "Evidence-based", description: "Assessments use validated instruments like PHQ-9 and GAD-7, scored with published clinical cut-offs." },
  { title: "Privacy-first", description: "Your journals are private by default. AI analysis stays within the platform and is never sold." },
  { title: "Human-in-the-loop", description: "We surface AI insights and recommendations — licensed counselors and emergency services remain the safety net." },
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <span className="badge bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300">About Us</span>
      <h1 className="mt-4 text-4xl font-extrabold text-gray-900 dark:text-white">
        Built to make mental wellness tracking accessible
      </h1>
      <p className="mt-6 text-lg text-gray-600 dark:text-gray-300">
        MindCare AI started as a final-year IT project with a simple premise: most people never
        notice a rough patch until it's already hard to manage. We wanted a platform that makes
        the small, daily signals — mood, sleep, journaling — visible over time, and pairs them
        with AI-assisted insight and a clear path to professional help when it's needed.
      </p>
      <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
        MindCare AI is <strong>not a diagnostic tool and not a replacement for a licensed mental
        health professional</strong>. It's a companion for everyday self-awareness, with
        guardrails that always point toward real support in a crisis.
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
