"use client"

import { useState, useEffect } from "react"
import dynamic from "next/dynamic"
import { Button } from "@/components/ui/button"
import { Star, TrendingUp, Shield, Zap } from "lucide-react"
import { motion } from "framer-motion"
import Link from "next/link"
import BgDecorativeElements from "./components/bg-decorative-elements"
import Image from "next/image"
import mainLogo from "@/public/main_logo.svg"

const RotatingText = dynamic(() => import("@/components/ui/rotating-text"), {
  ssr: false,
  loading: () => (
    <span className="bg-linear-to-r from-[#00B207] to-[#7BC47F] bg-clip-text text-secondary inline-block">
      mejores ofertas
    </span>
  ),
})

const EcommerceHeroCarousel: React.FC = () => {
  // Animation variants for text
  const textVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut" as const }
    }
  }

  const subtitleVariants = {
    hidden: { opacity: 0, x: 50 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.8, ease: "easeOut" as const, delay: 0.3 }
    }
  }

  const buttonVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut" as const }
    }
  }

  const trustVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.5, ease: "easeOut" as const }
    }
  }

  // Animation variants for the right section (SVG and cards)
  const cartSvgVariants = {
    hidden: { opacity: 0, scale: 0.8, x: 50 },
    visible: {
      opacity: 1,
      scale: 1,
      x: 0,
      transition: { duration: 0.8, ease: "easeOut" as const, delay: 0.8 } // Appears after left content starts
    }
  }

  const statCardVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: "easeOut" as const, delay: 1.5 + i * 0.2 } // Staggered appearance after cart
    })
  }

  const [showParticles, setShowParticles] = useState(false)

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setShowParticles(true)
    }, 1200)

    return () => window.clearTimeout(timeoutId)
  }, [])

  // Floating particles component
  const FloatingParticles = () => {
    const [particles, setParticles] = useState<Array<{
      id: number;
      left: number;
      top: number;
      xOffset: number;
      duration: number;
      delay: number;
    }>>([]);

    useEffect(() => {
      // Generate particles only on client side to avoid hydration mismatch
      const generateParticles = () => {
        const newParticles = Array.from({ length: 8 }, (_, i) => ({
          id: i,
          left: Math.random() * 100,
          top: Math.random() * 100,
          xOffset: Math.random() * 10 - 5,
          duration: 3 + Math.random() * 4,
          delay: Math.random() * 2,
        }));
        setParticles(newParticles);
      };

      generateParticles();
    }, []);

    return (
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-2 h-2 bg-linear-to-r from-green-200 to-emerald-200 dark:from-green-300 dark:to-emerald-300 rounded-full opacity-60"
            style={{
              left: `${particle.left}%`,
              top: `${particle.top}%`,
            }}
            animate={{
              x: [0, particle.xOffset, 0],
              y: [0, -20, 0],
              opacity: [0.6, 0.8, 0.6],
            }}
            transition={{
              duration: particle.duration,
              delay: particle.delay,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>
    );
  };

  return (
    <section className="relative min-h-[calc(100vh-80px)] lg:min-h-screen flex items-center justify-center overflow-hidden bg-linear-to-r from-green-50 via-white to-emerald-50 dark:from-gray-950 dark:via-gray-900 dark:to-green-950/20 transition-colors duration-300 py-12 md:py-16 lg:py-0">
      {/* Background decorative elements */}
      <BgDecorativeElements />

      {/* Floating particles */}
      {showParticles ? <FloatingParticles /> : null}

      {/* Main content container */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid lg:grid-cols-2 gap-8 md:gap-12 lg:gap-16 items-center">
          {/* Left Content - Text and CTA */}
          <div className="text-center lg:text-left space-y-6 md:space-y-8">
            {/* Trending Badge */}
            <motion.div
              className="inline-flex items-center gap-2 bg-linear-to-r from-[#00B207] to-[#34A853] text-white px-3 py-1.5 md:px-4 md:py-2 rounded-full text-xs md:text-sm lg:text-base font-semibold shadow-lg"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            >
              <TrendingUp className="w-3 h-3 md:w-4 md:h-4 lg:w-5 lg:h-5" />
              Ofertas en Tendencia
            </motion.div>

            {/* Main Title */}
            <h1
              className="text-md sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-gray-900 dark:text-white leading-tight"
            >
              <span className="block text-md ">Del campo Santandereano al mercado global</span>

              {/* <RotatingText
                texts={[
                  "mejores ofertas",
                  "ofertas únicas",
                  "ofertas increíbles",
                  "ofertas especiales",
                  "ofertas premium"
                ]}
                className="bg-linear-to-r from-[#00B207] to-[#7BC47F] bg-clip-text text-secondary inline-block"
                mainClassName="inline-flex justify-center lg:justify-start w-full"
                rotationInterval={3000}
                staggerDuration={0.05}
                staggerFrom="center"
                transition={{
                  type: "spring",
                  damping: 20,
                  stiffness: 100
                }}
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: -50, opacity: 0 }}
                auto={true}
                loop={true}
              /> */}
            </h1>
            <p className="text-xl">Conectamos a las PYMES agroindustriales de Santander con tecnología, facilitando sus ventas digitales y derribando las barreras de exportación. </p>


            <motion.div
              className="flex flex-col sm:flex-row gap-3 md:gap-4 justify-center lg:justify-start"
              variants={buttonVariants}
              initial="hidden"
              animate="visible"
              transition={{ delay: 0.9 }}
            >
              <Button
                size="lg"
                className="w-full sm:w-auto px-6 md:px-8 bg-linear-to-r from-[#00B207] to-[#34A853] hover:from-[#009a06] hover:to-[#2F8F46] text-white font-bold py-3 md:py-5 text-base md:text-lg lg:text-xl rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 flex items-center justify-center"
              >
                <Link href="/products">Ver productos</Link>
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="w-full sm:w-auto px-6 md:px-8 border-2 border-[#00B207] dark:border-[#00B207] bg-transparent text-[#00B207] dark:text-[#00B207] hover:bg-[#00B207] hover:text-white dark:hover:bg-[#00B207] dark:hover:text-white font-semibold py-3 md:py-5 text-base md:text-lg lg:text-xl rounded-xl transition-all duration-300 flex items-center justify-center"
                asChild
              >
                <Link href="/categories">Ver Categorías</Link>
              </Button>
            </motion.div>



          </div>

          {/* Right Content - Enhanced Shopping Cart */}
          <div className="flex justify-center lg:justify-end relative mt-8 lg:mt-0">
            <div className="relative group w-full max-w-sm md:max-w-md lg:max-w-none">
              {/* Main cart with glow effect */}
              <motion.div
                className="relative"
                variants={cartSvgVariants}
                initial="hidden"
                animate="visible"
              >
                <Image
                  src={mainLogo}
                  alt="Logo principal"
                  className="w-48 h-48 sm:w-56 sm:h-56 md:w-64 md:h-64 lg:w-80 lg:h-80 xl:w-96 xl:h-96 mx-auto drop-shadow-2xl group-hover:scale-105 transition-transform duration-300"
                />

                {/* Floating elements around the cart */}
                <div className="absolute -top-4 md:-top-6 -right-4 md:-right-6 bg-white dark:bg-gray-800 rounded-full p-2 md:p-4 shadow-lg dark:shadow-gray-900/25 animate-bounce border border-gray-200 dark:border-gray-700">
                  <div className="w-6 h-6 md:w-8 md:h-8 bg-[#00B207] dark:bg-[#00B207] rounded-full flex items-center justify-center">
                    <span className="text-white text-xs md:text-sm font-bold">%</span>
                  </div>
                </div>

                <div className="absolute -bottom-4 md:-bottom-6 -left-4 md:-left-6 bg-white dark:bg-gray-800 rounded-full p-2 md:p-4 shadow-lg dark:shadow-gray-900/25 animate-pulse border border-gray-200 dark:border-gray-700">
                  <div className="w-6 h-6 md:w-8 md:h-8 bg-[#7BC47F] dark:bg-[#6FB873] rounded-full flex items-center justify-center">
                    <span className="text-black dark:text-gray-900 text-xs md:text-sm font-bold">$</span>
                  </div>
                </div>

                <div className="absolute top-1/2 -right-8 md:-right-12 bg-white dark:bg-gray-800 rounded-full p-2 md:p-3 shadow-lg dark:shadow-gray-900/25 animate-bounce border border-gray-200 dark:border-gray-700" style={{ animationDelay: '0.5s' }}>
                  <div className="w-4 h-4 md:w-6 md:h-6 bg-[#34A853] dark:bg-[#2F8F46] rounded-full"></div>
                </div>
              </motion.div>

              {/* Stats below the cart */}
              {/* <div className="mt-8 md:mt-12 grid grid-cols-3 gap-2 sm:gap-4 md:gap-6 lg:gap-8 text-center px-4 sm:px-0">
                <motion.div
                  className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg p-2 md:p-4 shadow-lg dark:shadow-gray-900/25 border border-gray-200 dark:border-gray-700 transition-colors duration-300"
                  variants={statCardVariants}
                  initial="hidden"
                  animate="visible"
                  custom={0}
                >
                  <div className="text-xl sm:text-2xl md:text-3xl font-bold text-[#00B207] dark:text-[#00B207]">50K+</div>
                  <div className="text-[10px] sm:text-xs md:text-sm text-gray-600 dark:text-gray-300 mt-1">Clientes</div>
                </motion.div>
                <motion.div
                  className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg p-2 md:p-4 shadow-lg dark:shadow-gray-900/25 border border-gray-200 dark:border-gray-700 transition-colors duration-300"
                  variants={statCardVariants}
                  initial="hidden"
                  animate="visible"
                  custom={1}
                >
                  <div className="text-xl sm:text-2xl md:text-3xl font-bold text-[#34A853] dark:text-[#34A853]">10K+</div>
                  <div className="text-[10px] sm:text-xs md:text-sm text-gray-600 dark:text-gray-300 mt-1">Productos</div>
                </motion.div>
                <motion.div
                  className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-lg p-2 md:p-4 shadow-lg dark:shadow-gray-900/25 border border-gray-200 dark:border-gray-700 transition-colors duration-300"
                  variants={statCardVariants}
                  initial="hidden"
                  animate="visible"
                  custom={2}
                >
                  <div className="text-xl sm:text-2xl md:text-3xl font-bold text-[#7BC47F] dark:text-[#7BC47F]">24/7</div>
                  <div className="text-[10px] sm:text-xs md:text-sm text-gray-600 dark:text-gray-300 mt-1">Soporte</div>
                </motion.div>
              </div> */}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default EcommerceHeroCarousel