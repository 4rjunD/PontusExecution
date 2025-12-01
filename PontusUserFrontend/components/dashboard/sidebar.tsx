"use client"

import * as React from "react"
import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Route,
  Wallet,
  Globe,
  TrendingUp,
  Shield,
  FileText,
  BarChart3,
  Menu,
  ChevronRight,
  Database,
  Code,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Sidebar, SidebarHeader, SidebarContent, SidebarFooter } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"

interface SidebarItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  badge?: string
}

const menuItems: SidebarItem[] = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Route & Execute",
    href: "/dashboard/routing",
    icon: Route,
  },
  {
    title: "Treasury",
    href: "/dashboard/treasury",
    icon: Wallet,
  },
  {
    title: "Global Payouts",
    href: "/dashboard/payouts",
    icon: Globe,
  },
  {
    title: "FX Intelligence",
    href: "/dashboard/fx",
    icon: TrendingUp,
  },
  {
    title: "Compliance",
    href: "/dashboard/compliance",
    icon: Shield,
  },
  {
    title: "Reconciliation",
    href: "/dashboard/reconciliation",
    icon: FileText,
  },
  {
    title: "Analytics",
    href: "/dashboard/analytics",
    icon: BarChart3,
  },
  {
    title: "Integrations",
    href: "/dashboard/integrations",
    icon: Database,
  },
  {
    title: "Developer API",
    href: "/dashboard/developer",
    icon: Code,
  },
]

export function AppSidebar() {
  const [isCollapsed, setIsCollapsed] = React.useState(false)
  const pathname = usePathname()

  return (
    <Sidebar isCollapsed={isCollapsed}>
      <SidebarHeader>
        <Link href="/dashboard" className={cn("flex items-center gap-3", isCollapsed && "justify-center")}>
          {!isCollapsed ? (
            <>
              <div className="relative h-8 w-8 flex-shrink-0">
                <Image
                  src="/PontusIcon.png"
                  alt="Pontus Logo"
                  fill
                  className="object-contain"
                  priority
                />
              </div>
              <span className="font-bold text-xl tracking-tight text-foreground">Pontus</span>
            </>
          ) : (
            <div className="relative h-8 w-8 flex-shrink-0">
              <Image
                src="/PontusIcon.png"
                alt="Pontus Logo"
                fill
                className="object-contain"
                priority
              />
            </div>
          )}
        </Link>
      </SidebarHeader>
      <SidebarContent>
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href || pathname?.startsWith(item.href + "/")
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-foreground text-background shadow-sm"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground",
                  isCollapsed && "justify-center"
                )}
              >
                <Icon className="h-5 w-5" />
                {!isCollapsed && (
                  <>
                    <span>{item.title}</span>
                    {item.badge && (
                      <span className="ml-auto rounded-full bg-primary/10 px-2 py-0.5 text-xs">
                        {item.badge}
                      </span>
                    )}
                  </>
                )}
              </Link>
            )
          })}
        </nav>
      </SidebarContent>
      <SidebarFooter>
        <Button
          variant="ghost"
          size="icon"
          className="w-full"
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <Menu className="h-4 w-4" />
          )}
        </Button>
      </SidebarFooter>
    </Sidebar>
  )
}

