'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import React from 'react';
import { RegisterForm } from '@/components/forms/register-form';
import { useAuth } from '@/hooks/use-auth';
import Image from 'next/image';
import mainLogo from '@/public/main_logo.svg';

/**
 * Página de registro (`/register`).
 *
 * - Espera hidratación/auth state antes de renderizar.
 * - Si ya hay sesión, redirige según rol.
 * - Si no, muestra `RegisterForm`.
 */

const RegisterPage = () => {
  const [mounted, setMounted] = useState(false);
  const { isAuthenticated, isLoadingUser, user, isHydrated } = useAuth();
  const router = useRouter();
  const hasRedirected = useRef(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    // Solo redirigir una vez cuando todo esté listo y el usuario esté autenticado
    if (!mounted || !isHydrated || isLoadingUser || hasRedirected.current) return;
    
    if (isAuthenticated && user) {
      hasRedirected.current = true;
      const userRole = Number(user.id_rol);
      const redirectUrl = userRole === 1 ? '/admin' : '/';
      router.replace(redirectUrl);
    }
  }, [mounted, isAuthenticated, isLoadingUser, user, router, isHydrated]);

  // Mostrar loader durante la inicialización o mientras se verifica autenticación
  // Solo mostrar formulario cuando esté listo Y no esté autenticado
  const isInitializing = !mounted || !isHydrated;
  const isReady = mounted && isHydrated && !isLoadingUser;
  const shouldShowLoader = isInitializing || (isReady && isAuthenticated);
  
  if (shouldShowLoader) {
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
        {/* Logo de AGROSALE */}
        <div className="flex items-center gap-3 self-center">
        <div className="flex items-center space-x-2">
            <div className="w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center">
              <Image src={mainLogo} alt="Logo principal" width={40} height={40} className="w-8 h-8 sm:w-10 sm:h-10" />
            </div>
                <span className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#ec2538] dark:text-red-500 transition-colors duration-300">AGROSALE</span>
            </div>
          </div>
        {/* Formulario de registro */}
        <RegisterForm />
      </div>
    </div>
  )
}

export default RegisterPage