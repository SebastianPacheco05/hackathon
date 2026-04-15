'use client';

import React from 'react'
import { LoginForm } from '@/components/forms/login-form'
import { useLoginRedirect } from '@/hooks/use-role-redirect'
import { Loader2 } from 'lucide-react'
import Image from 'next/image'
import mainLogo from '@/public/main_logo.svg'

/**
 * Página de acceso (`/login`).
 *
 * - Si el usuario ya está autenticado, delega redirección por rol.
 * - Si no, renderiza `LoginForm`.
 */

const LoginPage = () => {
  const { isLoading, isAuthenticated } = useLoginRedirect();

  // Si ya está autenticado, mostrar loader mientras redirige
  if (isAuthenticated) {
    return (
      <div className="bg-[#F5F5F5] dark:bg-gray-950 flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10 transition-colors duration-300">
        <div className="flex h-screen w-full items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-[#FF0000] dark:text-red-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#F5F5F5] dark:bg-gray-950 flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10 transition-colors duration-300">
      <div className="flex w-full max-w-md flex-col gap-6">
        {/* Logo de Compralo */}
        <div className="flex items-center gap-3 self-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center">
              <Image src={mainLogo} alt="Logo principal" width={40} height={40} className="w-8 h-8 sm:w-10 sm:h-10" />
            </div>
                <span className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#ec2538] dark:text-red-500 transition-colors duration-300">Compralo</span>
            </div>
          </div>
        {/* Formulario de login */}
        <LoginForm />
      </div>
    </div>
  )
}

export default LoginPage