'use client';

import { usePathname } from "next/navigation";
import { SidebarProvider, SidebarInset } from "@/components/ui"
import { AppSidebar } from "@/components/layout/dashboard/sidebar";
import AdminHeader from "@/components/layout/dashboard/admin-header";
import { AdminGuard } from "@/components/auth/route-guard";
import { AdminTourProvider } from "./_tour/useAdminDriverTour";
import { isAdminAiPublicChatEnabled } from "@/lib/admin-ai-public";

export default function AdminLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const basePath = pathname?.split("?")[0]?.split("#")[0] ?? "";
  const publicAiChat =
    isAdminAiPublicChatEnabled &&
    (basePath === "/admin/ai" || basePath.startsWith("/admin/ai/"));

  const isAiAssistantPage =
    basePath === "/admin/ai" || basePath.startsWith("/admin/ai/");

  const shell = (
    <AdminTourProvider>
      <SidebarProvider
        style={
          {
            "--sidebar-width": "calc(var(--spacing) * 72)",
            "--header-height": "calc(var(--spacing) * 12)",
          } as React.CSSProperties
        }
      >
        <AppSidebar variant="inset" />
        <SidebarInset
          className={
            isAiAssistantPage
              ? "min-h-0 overflow-hidden md:peer-data-[variant=inset]:m-0 md:peer-data-[variant=inset]:rounded-none md:peer-data-[variant=inset]:shadow-none"
              : "md:peer-data-[variant=inset]:m-0 md:peer-data-[variant=inset]:rounded-none md:peer-data-[variant=inset]:shadow-none"
          }
        >
          <AdminHeader />
          <div
            className={
              isAiAssistantPage
                ? "flex min-h-0 flex-1 flex-col overflow-hidden bg-background transition-colors duration-300"
                : "flex flex-1 flex-col bg-background transition-colors duration-300"
            }
          >
            <div
              className={
                isAiAssistantPage
                  ? "@container/main flex min-h-0 flex-1 flex-col overflow-hidden"
                  : "@container/main flex flex-1 flex-col gap-2"
              }
            >
              <div
                className={
                isAiAssistantPage
                  ? "flex min-h-0 flex-1 flex-col gap-2 overflow-hidden py-2 md:py-3"
                  : "flex flex-col gap-4 py-4 md:gap-6 md:py-6"
                }
              >
                <div
                  className={
                isAiAssistantPage
                  ? "flex min-h-0 flex-1 flex-col overflow-hidden px-3 lg:px-4"
                  : "px-4 lg:px-6"
                  }
                >
                  {children}
                </div>
              </div>
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    </AdminTourProvider>
  );

  if (publicAiChat) {
    return shell;
  }

  return <AdminGuard>{shell}</AdminGuard>;
}
