import { RefreshCw, ShoppingBag } from 'lucide-react'
import React from 'react'

const FeaturedCategoriesError = ({ error, refetch }: { error: any, refetch: () => void }) => {
  return (
    <section className="relative min-h-screen bg-gradient-to-br from-[#00B207]/10 via-white to-[#00B207]/20 dark:from-[#00B207]/20 dark:via-gray-900 dark:to-[#00B207]/20 overflow-hidden flex items-center justify-center transition-colors duration-300">
        <div className="text-center p-8">
          <div className="w-20 h-20 bg-[#00B207]/20 dark:bg-[#00B207]/30 rounded-full flex items-center justify-center mx-auto mb-6">
            <ShoppingBag className="w-10 h-10 text-[#00B207] dark:text-[#00B207]" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 transition-colors duration-300">
            ¡Ups! Algo salió mal
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-md mx-auto transition-colors duration-300">
            {error?.message || 'Error al cargar las categorías'}
          </p>
          <button
            onClick={() => refetch()}
            className="inline-flex items-center px-6 py-3 bg-[#00B207] dark:bg-[#00B207] text-white rounded-lg font-medium hover:bg-[#009a06] dark:hover:bg-[#009a06] transition-colors duration-300"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Intentar de nuevo
          </button>
        </div>
      </section>
  )
}

export default FeaturedCategoriesError
