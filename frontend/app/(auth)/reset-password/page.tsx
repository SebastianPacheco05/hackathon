'use client';

import { Suspense } from 'react';
import { ResetPasswordForm } from '@/components/forms';
import Image from 'next/image';
import mainLogo from '@/public/main_logo.svg';

/**
 * Página `reset-password`.
 *
 * Usa `Suspense` porque el formulario depende de search params (token).
 */

export default function ResetPasswordPage() {
  return (
    <div className="bg-[#F5F5F5] dark:bg-gray-950 flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10 transition-colors duration-300">
      <div className="flex w-full max-w-md flex-col gap-6">
        {/* Logo de AGROSALE */}
        <div className="flex items-center gap-3 self-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center">
              <Image src={mainLogo} alt="Logo principal" width={40} height={40} className="w-8 h-8 sm:w-10 sm:h-10" />
            </div>
            <span className="text-xl sm:text-2xl lg:text-3xl font-bold text-[#ec2538] dark:text-red-500 transition-colors duration-300">
              AGROSALE
            </span>
          </div>
        </div>

        {/* Formulario de restablecimiento de contraseña */}
        <Suspense
          fallback={
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600" />
            </div>
          }
        >
          <ResetPasswordForm />
        </Suspense>
      </div>
    </div>
  );
}