import { MenuIcon } from "./icons";
import { NotificationBell } from "./NotificationBell";
import { ThemeToggle } from "./ThemeToggle";
import { UserMenu } from "./UserMenu";

interface DashboardTopbarProps {
  onMenuClick: () => void;
  title?: string;
}

export function DashboardTopbar({ onMenuClick, title }: DashboardTopbarProps) {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-gray-200 bg-white/80 px-4 backdrop-blur sm:px-6 dark:border-gray-800 dark:bg-gray-900/80">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 md:hidden dark:text-gray-300"
          aria-label="Open menu"
        >
          <MenuIcon className="h-5 w-5" />
        </button>
        {title && <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h1>}
      </div>
      <div className="flex items-center gap-2">
        <NotificationBell />
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}
