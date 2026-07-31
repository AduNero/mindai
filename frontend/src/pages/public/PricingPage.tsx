import { Link } from "react-router-dom";

const PLANS = [
  {
    name: "Free",
    price: "$0",
    description: "Everything you need to start tracking your wellbeing.",
    features: ["Mood & journal tracking", "1 assessment per month", "AI chat (limited history)", "Community resources"],
    cta: "Get started",
    highlighted: false,
  },
  {
    name: "Plus",
    price: "$7/mo",
    description: "For consistent, deeper self-tracking with full AI support.",
    features: [
      "Everything in Free",
      "Unlimited assessments",
      "Full AI chat history & export",
      "Wellness score & trend predictions",
      "Priority counselor booking",
    ],
    cta: "Start free trial",
    highlighted: true,
  },
  {
    name: "Campus / Organization",
    price: "Contact us",
    description: "For universities and clinics deploying MindCare AI at scale.",
    features: ["Everything in Plus", "Admin analytics dashboard", "Counselor management", "Custom onboarding"],
    cta: "Contact sales",
    highlighted: false,
  },
];

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white">Simple, transparent pricing</h1>
        <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
          Placeholder pricing for demonstration purposes — this is an academic project, not a live commercial product.
        </p>
      </div>

      <div className="mt-14 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {PLANS.map((plan) => (
          <div
            key={plan.name}
            className={
              plan.highlighted
                ? "card border-2 border-brand-600 shadow-lg"
                : "card"
            }
          >
            {plan.highlighted && (
              <span className="badge mb-3 bg-brand-600 text-white">Most popular</span>
            )}
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{plan.name}</h3>
            <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-white">{plan.price}</p>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">{plan.description}</p>
            <ul className="mt-6 space-y-2.5">
              {plan.features.map((f) => (
                <li key={f} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
                  <span className="mt-0.5 text-brand-600">✓</span>
                  {f}
                </li>
              ))}
            </ul>
            <Link
              to={plan.name === "Campus / Organization" ? "/contact" : "/register"}
              className={plan.highlighted ? "btn-primary mt-8 w-full" : "btn-outline mt-8 w-full"}
            >
              {plan.cta}
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
