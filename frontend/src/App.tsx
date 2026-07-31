import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router-dom";

import { FullPageSpinner } from "@/components/common/Spinner";
import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { ToastProvider } from "@/context/ToastContext";
import { AdminLayout } from "@/layouts/AdminLayout";
import { AppLayout } from "@/layouts/AppLayout";
import { AuthLayout } from "@/layouts/AuthLayout";
import { PublicLayout } from "@/layouts/PublicLayout";
import { AdminRoute } from "@/routes/AdminRoute";
import { ProtectedRoute } from "@/routes/ProtectedRoute";

const NotFoundPage = lazy(() => import("@/pages/NotFoundPage"));

const LandingPage = lazy(() => import("@/pages/public/LandingPage"));
const AboutPage = lazy(() => import("@/pages/public/AboutPage"));
const FeaturesPage = lazy(() => import("@/pages/public/FeaturesPage"));
const PricingPage = lazy(() => import("@/pages/public/PricingPage"));
const FAQPage = lazy(() => import("@/pages/public/FAQPage"));
const ContactPage = lazy(() => import("@/pages/public/ContactPage"));

const LoginPage = lazy(() => import("@/pages/auth/LoginPage"));
const RegisterPage = lazy(() => import("@/pages/auth/RegisterPage"));
const VerifyEmailPage = lazy(() => import("@/pages/auth/VerifyEmailPage"));
const ForgotPasswordPage = lazy(() => import("@/pages/auth/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("@/pages/auth/ResetPasswordPage"));

const DashboardPage = lazy(() => import("@/pages/app/DashboardPage"));
const MoodTrackerPage = lazy(() => import("@/pages/app/MoodTrackerPage"));
const JournalPage = lazy(() => import("@/pages/app/JournalPage"));
const AIChatPage = lazy(() => import("@/pages/app/AIChatPage"));
const AssessmentsPage = lazy(() => import("@/pages/app/AssessmentsPage"));
const AssessmentTakePage = lazy(() => import("@/pages/app/AssessmentTakePage"));
const ReportsPage = lazy(() => import("@/pages/app/ReportsPage"));
const AppointmentsPage = lazy(() => import("@/pages/app/AppointmentsPage"));
const ResourcesPage = lazy(() => import("@/pages/app/ResourcesPage"));
const SettingsPage = lazy(() => import("@/pages/app/SettingsPage"));
const ProfilePage = lazy(() => import("@/pages/app/ProfilePage"));

const AdminOverviewPage = lazy(() => import("@/pages/admin/AdminOverviewPage"));
const AdminUsersPage = lazy(() => import("@/pages/admin/AdminUsersPage"));
const AdminJournalReportsPage = lazy(() => import("@/pages/admin/AdminJournalReportsPage"));
const AdminRiskAlertsPage = lazy(() => import("@/pages/admin/AdminRiskAlertsPage"));
const AdminCounselorsPage = lazy(() => import("@/pages/admin/AdminCounselorsPage"));
const AdminAppointmentsPage = lazy(() => import("@/pages/admin/AdminAppointmentsPage"));
const AdminResourcesPage = lazy(() => import("@/pages/admin/AdminResourcesPage"));
const AdminReportsPage = lazy(() => import("@/pages/admin/AdminReportsPage"));
const AdminAuditLogsPage = lazy(() => import("@/pages/admin/AdminAuditLogsPage"));

function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <Suspense fallback={<FullPageSpinner />}>
            <Routes>
              <Route element={<PublicLayout />}>
                <Route path="/" element={<LandingPage />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="/features" element={<FeaturesPage />} />
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/faq" element={<FAQPage />} />
                <Route path="/contact" element={<ContactPage />} />
              </Route>

              <Route element={<AuthLayout />}>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/verify-email" element={<VerifyEmailPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />
              </Route>

              <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/mood-tracker" element={<MoodTrackerPage />} />
                  <Route path="/journal" element={<JournalPage />} />
                  <Route path="/ai-chat" element={<AIChatPage />} />
                  <Route path="/assessments" element={<AssessmentsPage />} />
                  <Route path="/assessments/:code" element={<AssessmentTakePage />} />
                  <Route path="/reports" element={<ReportsPage />} />
                  <Route path="/appointments" element={<AppointmentsPage />} />
                  <Route path="/resources" element={<ResourcesPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                </Route>

                <Route element={<AdminRoute />}>
                  <Route element={<AdminLayout />}>
                    <Route path="/admin" element={<AdminOverviewPage />} />
                    <Route path="/admin/users" element={<AdminUsersPage />} />
                    <Route path="/admin/journal-reports" element={<AdminJournalReportsPage />} />
                    <Route path="/admin/risk-alerts" element={<AdminRiskAlertsPage />} />
                    <Route path="/admin/counselors" element={<AdminCounselorsPage />} />
                    <Route path="/admin/appointments" element={<AdminAppointmentsPage />} />
                    <Route path="/admin/resources" element={<AdminResourcesPage />} />
                    <Route path="/admin/reports" element={<AdminReportsPage />} />
                    <Route path="/admin/audit-logs" element={<AdminAuditLogsPage />} />
                  </Route>
                </Route>
              </Route>

              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
