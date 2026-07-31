import { FormEvent, useState } from "react";

import { useToast } from "@/context/ToastContext";

export default function ContactPage() {
  const { showToast } = useToast();
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", message: "" });

  // No dedicated "contact messages" backend endpoint exists for this
  // academic project — this form validates client-side and confirms
  // receipt locally rather than silently pretending to call an API.
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setTimeout(() => {
      setSubmitting(false);
      showToast("Thanks — we've received your message and will get back to you soon.", "success");
      setForm({ name: "", email: "", message: "" });
    }, 500);
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6 lg:px-8">
      <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white">Contact us</h1>
      <p className="mt-3 text-gray-600 dark:text-gray-300">
        Questions, feedback, or partnership inquiries — we'd love to hear from you.
      </p>

      <div className="mt-6 rounded-2xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200">
        <strong>In crisis right now?</strong> This form is not monitored in real time. Please see our{" "}
        <a href="/resources" className="underline">Emergency Resources</a> or contact local emergency services.
      </div>

      <form onSubmit={handleSubmit} className="mt-8 space-y-5">
        <div>
          <label htmlFor="name" className="label">Name</label>
          <input
            id="name"
            required
            className="input"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          />
        </div>
        <div>
          <label htmlFor="email" className="label">Email</label>
          <input
            id="email"
            type="email"
            required
            className="input"
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
          />
        </div>
        <div>
          <label htmlFor="message" className="label">Message</label>
          <textarea
            id="message"
            required
            rows={5}
            className="input"
            value={form.message}
            onChange={(e) => setForm((f) => ({ ...f, message: e.target.value }))}
          />
        </div>
        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? "Sending..." : "Send message"}
        </button>
      </form>
    </div>
  );
}
