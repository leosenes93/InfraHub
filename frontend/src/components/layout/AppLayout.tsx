import { type ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";
import { GlobalSearch } from "@/components/layout/GlobalSearch";
import { isAdmin } from "@/lib/permissions";

const NAV_LINKS = [
  { label: "Dashboard", to: "/" },
  { label: "Inventário", to: "/inventory" },
  { label: "Docker Local", to: "/docker" },
];

const DISABLED_NAV_ITEMS = ["Wiki Técnica", "Monitoramento"];

export function AppLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navLinks = isAdmin(user?.role)
    ? [...NAV_LINKS, { label: "Auditoria", to: "/audit" }]
    : NAV_LINKS;

  return (
    <div className="flex h-screen bg-slate-50">
      <aside className="flex w-64 flex-col border-r border-slate-200 bg-white">
        <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-6">
          <div className="h-8 w-8 rounded-md bg-brand-600" />
          <span className="text-lg font-semibold text-slate-900">InfraHub</span>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navLinks.map((item) => (
            <NavLink
              key={item.label}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `block rounded-md px-3 py-2 text-sm font-medium ${
                  isActive ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-50"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
          {DISABLED_NAV_ITEMS.map((label) => (
            <span
              key={label}
              className="block cursor-not-allowed rounded-md px-3 py-2 text-sm font-medium text-slate-400"
              title="Disponível em uma próxima fase"
            >
              {label}
            </span>
          ))}
        </nav>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
          <GlobalSearch />
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-slate-900">{user?.full_name}</p>
              <p className="text-xs uppercase tracking-wide text-slate-400">{user?.role}</p>
            </div>
            <button
              onClick={logout}
              className="rounded-md border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50"
            >
              Sair
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
