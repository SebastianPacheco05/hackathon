"use client"

import * as React from "react"
import {
  IconChartBar,
  IconDashboard,
  IconHelp,
  IconInnerShadowTop,
  IconCategory,
  IconListDetails,
  IconTags,
  IconBuildingFactory2,
  IconSearch,
  IconSettings,
  IconShoppingCart,
  IconPackage,
  IconUsers,
  IconTruck,
  IconMail,
  IconHeart,
  IconBrandGoogle,
  IconCreditCard,
  IconDiscount,
  IconCoins,
  IconSparkles
} from "@tabler/icons-react"

import { NavMain } from "@/components/layout/dashboard/nav-main"
import { NavSecondary } from "@/components/layout/dashboard/nav-secondary"
import { NavUser } from "@/components/layout/dashboard/nav-user"
import Image from "next/image"
import mainLogo from "@/public/main_logo.svg"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui"

const data = {
  navMain: [
    {
      title: "Dashboard",
      url: "/admin",
      icon: IconDashboard,
      section: "principal"
    },
    {
      title: "Órdenes",
      url: "/admin/orders",
      icon: IconShoppingCart,
      section: "principal"
    },
    {
      title: "Categorías",
      url: "/admin/categories",
      icon: IconCategory,
      section: "catalogo"
    },
    {
      title: "Atributos",
      url: "/admin/attributes",
      icon: IconListDetails,
      section: "catalogo"
    },
    {
      title: "Marcas",
      url: "/admin/brands",
      icon: IconTags,
      section: "catalogo"
    },
    {
      title: "Proveedores",
      url: "/admin/providers",
      icon: IconBuildingFactory2,
      section: "catalogo"
    },
    {
      title: "Productos",
      url: "/admin/products",
      icon: IconPackage,
      section: "catalogo"
    },
    {
      title: "Usuarios",
      url: "/admin/users",
      icon: IconUsers,
      section: "gestion"
    },
    {
      title: "Descuentos",
      url: "/admin/discounts",
      icon: IconDiscount,
      section: "gestion"
    },
    {
      title: "Puntos",
      url: "/admin/points",
      icon: IconCoins,
      section: "gestion"
    },
    {
      title: "Barra Informativa",
      url: "/admin/info-bar",
      icon: IconInnerShadowTop,
      section: "gestion"
    },
    {
      title: "Analíticas",
      url: "/admin/analytics",
      icon: IconChartBar,
      section: "otros"
    },
    {
      title: "Centro de decisiones IA",
      url: "/admin/ai",
      icon: IconSparkles,
      section: "otros"
    }
  ],
  navSecondary: [
    {
      title: "Configuración",
      url: "/admin/settings",
      icon: IconSettings,
    },
    {
      title: "Marketing por Email",
      url: "/admin/emails",
      icon: IconMail,
    },
    {
      title: "Favoritos",
      url: "/admin/favorites",
      icon: IconHeart,
    },
    {
      title: "Pagos",
      url: "/admin/payments",
      icon: IconCreditCard,
    },
    {
      title: "SEO y Marketing",
      url: "/admin/seo",
      icon: IconBrandGoogle,
    },
    {
      title: "Ayuda",
      url: "#",
      icon: IconHelp,
    },
    {
      title: "Buscar",
      url: "#",
      icon: IconSearch,
    },
  ],
}

export function AppSidebar({ variant }: { variant: "sidebar" | "inset" }) {
  return (
    <Sidebar
      variant={variant}
      collapsible="icon"
      className="border-r border-sidebar-border bg-sidebar transition-colors duration-300"
      data-tour-id="admin-sidebar"
    >
      <SidebarHeader className="border-b border-sidebar-border transition-colors duration-300">
        <div className="flex h-[--header-height] shrink-0 items-center gap-2 px-4 lg:px-6 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-2">
          <div className="flex items-center gap-2 group-data-[collapsible=icon]:w-full group-data-[collapsible=icon]:justify-center">
            <div className="w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center group-data-[collapsible=icon]:w-7 group-data-[collapsible=icon]:h-7">
              <Image src={mainLogo} alt="Logo principal" width={40} height={40} className="w-8 h-8 sm:w-10 sm:h-10 group-data-[collapsible=icon]:w-7 group-data-[collapsible=icon]:h-7" />
            </div>
            <span className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#ec2538] dark:text-red-500 transition-colors duration-300 group-data-[collapsible=icon]:hidden">AGROSALE</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          <NavMain items={data.navMain} />
          {/* <NavSecondary items={data.navSecondary} /> */}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter className="border-t border-gray-200 dark:border-gray-700 transition-colors duration-300">
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  )
}
