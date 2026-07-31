import { Outlet } from "react-router-dom";

import { Footer } from "@/components/common/Footer";
import { PublicNavbar } from "@/components/common/PublicNavbar";

export function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <PublicNavbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
