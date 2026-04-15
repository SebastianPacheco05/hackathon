"use client"

import * as React from "react"
import { useState, useEffect } from "react"
import { useTheme } from "next-themes"
import { Menu, X, Heart, Moon, Sun, ShoppingCart } from "lucide-react"
import { Button } from "@/components/ui"
import MiniCartHover from "@/components/cart/minicart-hover"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui"
import { type NavItem } from "@/lib/menu-config"
import { MobileMenu, SearchBar, ProductSearchBar, UserMenu } from "./components"
import Link from "next/link"
import { defaultMenuItems } from "@/lib/menu-config"
import { useCartInfo } from "@/hooks/use-cart"
import { useFavorites } from "@/hooks/use-favorites"
import { useAuth } from "@/hooks/use-auth"
import { useRouter, usePathname } from "next/navigation"
import Image from "next/image"
import mainLogo from "@/public/main_logo.svg"

interface EcommerceHeaderProps {
  logo?: React.ReactNode
  menuItems?: NavItem[]
  cartCount?: number
  className?: string
}

const EcommerceHeader: React.FC<EcommerceHeaderProps> = ({
  logo,
  menuItems = [],
  cartCount, // Ahora será opcional, usaremos el hook
  className = ""
}) => {
  const router = useRouter()
  const pathname = usePathname()
  const { itemCount, isLoading } = useCartInfo()
  const { favorites } = useFavorites()
  const { user } = useAuth()
  const { theme, setTheme } = useTheme()

  const [mounted, setMounted] = useState(false)
  const [displayCartCount, setDisplayCartCount] = useState(0)
  const [favoritesCount, setFavoritesCount] = useState(0)

  useEffect(() => {
    setMounted(true)
    setDisplayCartCount(cartCount ?? itemCount)
    setFavoritesCount(favorites.length)
  }, [cartCount, itemCount, favorites.length])

  useEffect(() => {
    if (mounted) {
      setDisplayCartCount(cartCount ?? itemCount)
    }
  }, [cartCount, itemCount, mounted])

  useEffect(() => {
    if (mounted) {
      setFavoritesCount(favorites.length)
    }
  }, [favorites.length, mounted])

  const handleCartClick = () => router.push('/cart')
  const handleFavoritesClick = () => router.push('/favorites')
  const toggleTheme = () => setTheme(theme === "light" ? "dark" : "light")

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  const navigationItems = menuItems.length > 0 ? menuItems : defaultMenuItems

  return (
    <header className={`sticky top-0 z-40 w-full ${className}`}>
      {/* Main Navigation Header */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 transition-colors duration-300">
        <div className="container mx-auto px-3 sm:px-4">
          <div className="flex items-center justify-between h-14 sm:h-16">
            {/* Logo */}
            <div className="flex items-center space-x-2 sm:space-x-4">
              <Link href="/" prefetch={false}>
                {logo || (
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center">
                      <Image src={mainLogo} alt="Logo principal" width={32} height={32} />
                    </div>
                    <span className="text-lg sm:text-2xl lg:text-3xl font-bold text-[#000000] dark:text-white transition-colors duration-300">AGROSALE</span>
                  </div>
                )}
              </Link>

              {/* Navigation - Solo visible en desktop */}
              <nav className="hidden lg:flex items-center space-x-8 ml-8">
                {navigationItems.map((item, index) => (
                  <Link
                    key={index}
                    href={item.href || "#"}
                    prefetch={false}
                    className={`text-sm font-medium transition-colors duration-300 ${pathname === item.href
                      ? "text-[#00B207] dark:text-[#00B207] border-b-2 border-[#00B207] dark:border-[#00B207] pb-2"
                      : "text-gray-900 dark:text-white hover:text-[#00B207] dark:hover:text-[#00B207]"
                      }`}
                  >
                    {item.text}
                  </Link>
                ))}
              </nav>
            </div>

            {/* Right Side: en responsive solo carrito + menú; en desktop todo */}
            <div className="flex items-center space-x-2 sm:space-x-4 lg:space-x-6">
              {/* Desktop: búsqueda */}
              <div className="hidden lg:block w-40 sm:w-48 lg:w-64">
                <ProductSearchBar />
              </div>

              <div className="flex items-center space-x-1 sm:space-x-2 lg:space-x-4">
                {/* Solo en desktop: wishlist, notificaciones, tema, user menu */}
                {user && (
                  <div className="hidden lg:block">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="relative p-1.5 sm:p-2 text-gray-700 dark:text-gray-300 hover:text-[#00B207] dark:hover:text-[#00B207] hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-300"
                            onClick={handleFavoritesClick}
                            aria-label="Lista de deseos"
                          >
                            <Heart className="w-4 h-4 sm:w-5 sm:h-5" />
                            {mounted && favoritesCount > 0 && (
                              <span className="absolute -top-1 -right-1 bg-[#00B207] dark:bg-[#00B207] text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                                {favoritesCount > 99 ? "99+" : favoritesCount}
                              </span>
                            )}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent><p>Lista de deseos</p></TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                )}
                <div className="hidden lg:block">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="p-1.5 sm:p-2 text-gray-700 dark:text-gray-300 hover:text-[#00B207] dark:hover:text-[#00B207] hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-300"
                          onClick={toggleTheme}
                          aria-label="Cambiar tema"
                        >
                          <Sun className="w-4 h-4 sm:w-5 sm:h-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                          <Moon className="absolute w-4 h-4 sm:w-5 sm:h-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent><p>Cambiar tema</p></TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>

                {/* Carrito: siempre visible */}
                <MiniCartHover
                  trigger={
                    <Button
                      variant="ghost"
                      size="sm"
                      className="relative p-1.5 sm:p-2 text-gray-700 dark:text-gray-300 hover:text-[#00B207] dark:hover:text-[#00B207] hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-300 cursor-pointer"
                      onClick={handleCartClick}
                      disabled={isLoading}
                      aria-label={mounted && displayCartCount > 0 ? `Carrito (${displayCartCount} ${displayCartCount === 1 ? "producto" : "productos"})` : "Carrito"}
                    >
                      <ShoppingCart className="w-4 h-4 sm:w-5 sm:h-5" />
                      {mounted && displayCartCount > 0 && (
                        <span className="absolute -top-1 -right-1 bg-[#00B207] dark:bg-[#00B207] text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                          {displayCartCount > 99 ? "99+" : displayCartCount}
                        </span>
                      )}
                    </Button>
                  }
                />

                {/* Solo en desktop: menú de usuario */}
                <div className="hidden lg:block">
                  <UserMenu />
                </div>
              </div>

              {/* Solo en responsive: botón menú hamburguesa */}
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleMobileMenu}
                className="lg:hidden p-1.5 sm:p-2 ml-1 text-gray-700 dark:text-gray-300 hover:text-[#00B207] dark:hover:text-[#00B207] hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-300"
                aria-label={isMobileMenuOpen ? "Cerrar menú" : "Abrir menú"}
                aria-expanded={isMobileMenuOpen}
              >
                {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </Button>
            </div>
          </div>

          {/* Mobile Search - Solo visible en móvil */}
          <div className="sm:hidden pb-4">
            <SearchBar />
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <MobileMenu
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        items={navigationItems}
        pathname={pathname}
      />
    </header>
  )
}

export default EcommerceHeader 