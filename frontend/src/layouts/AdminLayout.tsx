import { useState } from "react";
import { Outlet } from "react-router-dom";

import { DashboardSidebar, SidebarNavItem } from "@/components/common/DashboardSidebar";
import { DashboardTopbar } from "@/components/common/DashboardTopbar";
import { CompassIcon, HeartIcon, HomeIcon, ShieldIcon, UserIcon } from "@/components/common/icons";

const NAV_ITEMS: SidebarNavItem[] = [
  { to: "/admin", label: "Overview", icon: HomeIcon, end: true },
  { to: "/admin/users", label: "Users", icon: UserIcon },
  { to: "/admin/risk-alerts", label: "Risk Alerts", icon: HeartIcon },
  { to: "/admin/resources", label: "Resources", icon: CompassIcon },
  { to: "/admin/audit-logs", label: "Audit Logs", icon: ShieldIcon },
];

export function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950">
      <DashboardSidebar
        items={NAV_ITEMS}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        title="MindCare Admin"
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <DashboardTopbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
