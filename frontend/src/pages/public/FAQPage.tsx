import { useState } from "react";

const FAQS = [
  {
    q: "Is MindCare AI a substitute for therapy or medical care?",
    a: "No. MindCare AI is a self-monitoring and support tool. It does not diagnose conditions and is not a substitute for a licensed mental health professional. If you're in crisis, contact local emergency services or a crisis hotline immediately.",
  },
  {
    q: "How does the AI analyze my journal entries?",
    a: "Journal entries are processed with sentiment and emotion classification models (via Hugging Face Transformers) to estimate sentiment, stress, anxiety, and emotional tone. Results are stored privately and used to power your dashboard and recommendations.",
  },
  {
    q: "What happens if the AI detects concerning language?",
    a: "MindCare AI never pretends to be a therapist or guarantees confidentiality in an emergency. If crisis-indicating language is detected, you'll be shown location-aware emergency resources and encouraged to contact local services or a trusted person. We do not notify third parties without your explicit consent.",
  },
  {
    q: "Who can see my journal entries?",
    a: "Journal entries are private by default and visible only to you. You can optionally mark an entry public; public entries can be reported by other users for moderation.",
  },
  {
    q: "Can I export my AI chat history?",
    a: "Yes — every AI Therapy chat session can be exported as a text transcript from the chat page.",
  },
  {
    q: "Are the assessments (PHQ-9, GAD-7, etc.) clinically validated?",
    a: "PHQ-9 and GAD-7 use their standard, published items and clinical severity cut-offs. The stress, burnout, and self-esteem instruments are original items inspired by well-known scales; none of these produce a diagnosis.",
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
