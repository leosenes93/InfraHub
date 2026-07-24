import { type ReactNode } from "react";

import { useAuth } from "@/contexts/AuthContext";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/", active: true },
  { label: "Inventário", href: "#", active: false },
  { label: "Wiki Técnica", href: "#", active: false },
  { label: "Monitoramento", href: "#", active: false },
  { label: "Auditoria", href: "#", active: false },
];

export function AppLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="flex h-screen bg-slate-50">
      <aside className="flex w-64 flex-col border-r border-slate-200 bg-white">
        <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-6">
          <div className="h-8 w-8 rounded-md bg-brand-600" />
          <span className="text-lg font-semibold text-slate-900">InfraHub</span>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className={`block rounded-md px-3 py-2 text-sm font-medium ${
                item.active
                  ? "bg-brand-50 text-brand-700"
                  : "text-slate-400 cursor-not-allowed"
              }`}
              title={item.active ? undefined : "Disponível em uma próxima fase"}
            >
              {item.label}
            </a>
          ))}
        </nav>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
          <h1 className="text-sm font-medium text-slate-500">Painel de Infraestrutura</h1>
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
