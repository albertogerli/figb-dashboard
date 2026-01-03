import { ReactNode, useState } from "react";
import { Link, useLocation } from "wouter";
import {
  LayoutDashboard,
  TrendingUp,
  Map,
  Users,
  Award,
  RefreshCw,
  UserX,
  FileText,
  BarChart3,
  Menu,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { APP_TITLE } from "@/const";

interface NavItem {
  path: string;
  label: string;
  icon: ReactNode;
}

const navItems: NavItem[] = [
  { path: "/", label: "Overview", icon: <LayoutDashboard className="w-5 h-5" /> },
  { path: "/temporale", label: "Analisi Temporale", icon: <TrendingUp className="w-5 h-5" /> },
  { path: "/regionale", label: "Analisi Regionale", icon: <Map className="w-5 h-5" /> },
  { path: "/demografia", label: "Demografia", icon: <Users className="w-5 h-5" /> },
  { path: "/categorie", label: "Categorie", icon: <Award className="w-5 h-5" /> },
  { path: "/retention", label: "Retention Rate", icon: <RefreshCw className="w-5 h-5" /> },
  { path: "/churn", label: "Churn Analysis", icon: <UserX className="w-5 h-5" /> },
  { path: "/tessere", label: "Tipologie Tessera", icon: <FileText className="w-5 h-5" /> },
  { path: "/statistiche", label: "Statistiche Avanzate", icon: <BarChart3 className="w-5 h-5" /> },
];

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [location] = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <h1 className="text-xl font-bold text-primary">{APP_TITLE}</h1>
          </div>
          <div className="text-sm text-muted-foreground">
            Periodo: 2017-2024
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside
          className={`
            fixed lg:sticky top-16 left-0 z-40 h-[calc(100vh-4rem)]
            w-64 border-r bg-card transition-transform duration-300 ease-in-out
            ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          `}
        >
          <nav className="flex flex-col gap-1 p-4">
            {navItems.map((item) => {
              const isActive = location === item.path;
              return (
                <Link key={item.path} href={item.path}>
                  <a
                    className={`
                      flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium
                      transition-colors hover:bg-accent hover:text-accent-foreground
                      ${
                        isActive
                          ? "bg-primary text-primary-foreground hover:bg-primary/90"
                          : "text-muted-foreground"
                      }
                    `}
                    onClick={() => setSidebarOpen(false)}
                  >
                    {item.icon}
                    {item.label}
                  </a>
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Overlay per mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/50 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          <div className="container py-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
