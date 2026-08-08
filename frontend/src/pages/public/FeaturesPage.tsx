const FEATURE_GROUPS = [
  {
    title: "Track",
    items: [
      { name: "Mood Tracker", description: "8 mood states with 1-10 intensity, notes, and weekly/monthly graphs." },
      { name: "Journal", description: "Private-by-default entries, tags, and search." },
    ],
  },
  {
    title: "Tentative AI Label",
    items: [
      {
        name: "Sentiment Label",
        description:
          "Each journal entry gets a positive/negative/neutral label from a TF-IDF + logistic regression classifier — a single, bounded text-classification feature, not a general AI assistant.",
      },
      {
        name: "Accept, reject, or correct",
        description: "The label is always marked tentative and AI-suggested — you control whether it's accepted, rejected, or corrected.",
      },
    ],
  },
  {
    title: "Support",
    items: [
      {
        name: "Crisis Resources",
        description: "Emergency and crisis resources are always visible on the Resources page — never gated behind AI output.",
      },
      {
        name: "Deterministic safety check",
        description:
          "A fixed, rule-based phrase check (not AI, not the sentiment model) can surface a support-resource card on a journal entry. It never claims real-time monitoring and never contacts anyone on your behalf.",
      },
    ],
  },
];

export default function FeaturesPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white">Features</h1>
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
          A deliberately small, bounded feature set — mood, journaling, and one tentative AI label.
        </p>
      </div>

      <div className="mt-16 space-y-14">
        {FEATURE_GROUPS.map((group) => (
          <div key={group.title}>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">{group.title}</h2>
            <div className="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {group.items.map((item) => (
                <div key={item.name} className="card">
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100">{item.name}</h3>
                  <p className="mt-1.5 text-sm text-gray-500 dark:text-gray-400">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
