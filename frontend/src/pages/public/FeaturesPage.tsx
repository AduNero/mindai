const FEATURE_GROUPS = [
  {
    title: "Track",
    items: [
      { name: "Mood Tracker", description: "8 mood states with 1-10 intensity, notes, and weekly/monthly graphs." },
      { name: "Journal", description: "Private or public entries, tags, search, and automatic sentiment analysis." },
      { name: "Sleep & Meditation", description: "Log sleep quality and guided meditation sessions." },
    ],
  },
  {
    title: "Understand",
    items: [
      { name: "Wellness Score", description: "A 0-100 score blending mood, journaling, assessments, sleep, and chat sentiment." },
      { name: "AI Sentiment & Emotion Analysis", description: "Every journal entry is analyzed for sentiment, stress, anxiety, and emotion." },
      { name: "Assessments", description: "PHQ-9, GAD-7, stress, burnout, and self-esteem — scored with severity and history." },
    ],
  },
  {
    title: "Get Support",
    items: [
      { name: "AI Therapy Chat", description: "LibreChat-powered conversations with searchable history and export." },
      { name: "Recommendations", description: "Personalized suggestions that improve as more data is collected." },
      { name: "Counseling Appointments", description: "Book, reschedule, or cancel sessions with a counselor." },
      { name: "Crisis Resources", description: "Location-aware emergency contacts, always one tap away." },
    ],
  },
];

export default function FeaturesPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white">Features</h1>
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
          Everything you need to notice patterns, understand them, and act on them.
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
