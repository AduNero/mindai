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
const FAQPage = lazy(() => import("@/pages/public/FAQPage"));
const ContactPage = lazy(() => import("@/pages/public/ContactPage"));
const PrivacyNoticePage = lazy(() => import("@/pages/public/PrivacyNoticePage"));

const LoginPage = lazy(() => import("@/pages/auth/LoginPage"));
const RegisterPage = lazy(() => import("@/pages/auth/RegisterPage"));
const VerifyEmailPage = lazy(() => import("@/pages/auth/VerifyEmailPage"));
const ForgotPasswordPage = lazy(() => import("@/pages/auth/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("@/pages/auth/ResetPasswordPage"));

const DashboardPage = lazy(() => import("@/pages/app/DashboardPage"));
const MoodTrackerPage = lazy(() => import("@/pages/app/MoodTrackerPage"));
const JournalPage = lazy(() => import("@/pages/app/JournalPage"));
const ResourcesPage = lazy(() => import("@/pages/app/ResourcesPage"));
const SettingsPage = lazy(() => import("@/pages/app/SettingsPage"));
const ProfilePage = lazy(() => import("@/pages/app/ProfilePage"));

const AdminOverviewPage = lazy(() => import("@/pages/admin/AdminOverviewPage"));
const AdminUsersPage = lazy(() => import("@/pages/admin/AdminUsersPage"));
const AdminRiskAlertsPage = lazy(() => import("@/pages/admin/AdminRiskAlertsPage"));
const AdminResourcesPage = lazy(() => import("@/pages/admin/AdminResourcesPage"));
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
                <Route path="/faq" element={<FAQPage />} />
                <Route path="/contact" element={<ContactPage />} />
                <Route path="/privacy" element={<PrivacyNoticePage />} />
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
                  <Route path="/resources" element={<ResourcesPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                </Route>

                <Route element={<AdminRoute />}>
                  <Route element={<AdminLayout />}>
                    <Route path="/admin" element={<AdminOverviewPage />} />
                    <Route path="/admin/users" element={<AdminUsersPage />} />
                    <Route path="/admin/risk-alerts" element={<AdminRiskAlertsPage />} />
                    <Route path="/admin/resources" element={<AdminResourcesPage />} />
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
