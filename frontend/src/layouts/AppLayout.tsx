import { useState } from "react";
import { Outlet } from "react-router-dom";

import { DashboardSidebar, SidebarNavItem } from "@/components/common/DashboardSidebar";
import { DashboardTopbar } from "@/components/common/DashboardTopbar";
import { BookIcon, CompassIcon, GearIcon, HeartIcon, HomeIcon, UserIcon } from "@/components/common/icons";

const NAV_ITEMS: SidebarNavItem[] = [
  { to: "/dashboard", label: "Dashboard", icon: HomeIcon, end: true },
  { to: "/mood-tracker", label: "Mood Tracker", icon: HeartIcon },
  { to: "/journal", label: "Journal", icon: BookIcon },
  { to: "/resources", label: "Resources", icon: CompassIcon },
  { to: "/settings", label: "Settings", icon: GearIcon },
  { to: "/profile", label: "Profile", icon: UserIcon },
];

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-gray-950">
      <DashboardSidebar items={NAV_ITEMS} open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <DashboardTopbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
