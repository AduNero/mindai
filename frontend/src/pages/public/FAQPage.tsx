import { useState } from "react";

const FAQS = [
  {
    q: "Is MindCare AI a substitute for therapy or medical care?",
    a: "No. MindCare AI is a self-monitoring mood and journal log. It does not diagnose conditions and is not a substitute for a licensed mental health professional. If you're in crisis, contact local emergency services or a crisis hotline immediately.",
  },
  {
    q: "How does the AI analyze my journal entries?",
    a: "Each journal entry is run through a single, bounded classifier — TF-IDF feature extraction plus multinomial logistic regression — trained and evaluated on a public benchmark dataset (TweetEval). It estimates text polarity (positive/negative/neutral) only. It is not a general-purpose AI, not an emotion detector, and not a diagnostic tool.",
  },
  {
    q: "Is the sentiment label the same as an emotional assessment?",
    a: "No. It's always shown as a tentative, AI-suggested label with a one-line disclaimer, and you can accept, reject, or correct it. It's never presented as a diagnosis, emotion, or severity score.",
  },
  {
    q: "What happens if the app detects concerning language?",
    a: "A separate, deterministic (non-AI) phrase check — not the sentiment classifier — can surface a support-resource card. It never claims to monitor you in real time, never notifies anyone on your behalf, and never claims emergency services have been contacted. Only the risk tier is logged, never the text that triggered it.",
  },
  {
    q: "Who can see my journal entries?",
    a: "Journal entries are private by default and always private — only you can see them. There is no public-sharing or moderation feature.",
  },
  {
    q: "Can I delete my entries or my account?",
    a: "Yes. Individual entries can be deleted at any time — this is a real, permanent deletion. You can also delete your entire account from Settings, which immediately and permanently removes your account and all associated data.",
  },
];

export default function FAQPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white">Frequently asked questions</h1>
      </div>

      <div className="mt-12 divide-y divide-gray-200 dark:divide-gray-800">
        {FAQS.map((item, index) => {
          const isOpen = openIndex === index;
          return (
            <div key={item.q} className="py-4">
              <button
                type="button"
                onClick={() => setOpenIndex(isOpen ? null : index)}
                className="flex w-full items-center justify-between text-left"
                aria-expanded={isOpen}
              >
                <span className="font-medium text-gray-900 dark:text-gray-100">{item.q}</span>
                <span className="ml-4 text-xl text-gray-400">{isOpen ? "−" : "+"}</span>
              </button>
              {isOpen && <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">{item.a}</p>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
