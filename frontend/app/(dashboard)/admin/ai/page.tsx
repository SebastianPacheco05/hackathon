'use client'

import Link from 'next/link'
import { Button } from '@/components/ui'
import { AdminDecisionCenterChat } from '@/components/admin/admin-decision-center-chat'
import { IconArrowLeft, IconRefresh } from '@tabler/icons-react'

export default function AdminAIDecisionCenterPage() {
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      {/* Barra compacta: deja casi todo el alto para el chat */}
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-2 border-b border-border/50 pb-2">
        <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1">
          <Button variant="ghost" size="sm" asChild className="-ml-2 h-8 gap-1 px-2 text-muted-foreground">
            <Link href="/admin/analytics">
              <IconArrowLeft className="h-4 w-4 shrink-0" />
              <span className="hidden sm:inline">Analíticas</span>
            </Link>
          </Button>
          <div className="hidden h-4 w-px bg-border sm:block" aria-hidden />
          <div className="min-w-0">
            <h1 className="truncate text-lg font-semibold tracking-tight">
              Asistente IA
            </h1>
            <p className="text-muted-foreground hidden max-w-xl truncate text-xs sm:block">
              Preguntas, recomendaciones y decisiones en una conversación.
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" className="h-8 shrink-0 gap-1" asChild>
          <Link href="/admin">
            <IconRefresh className="h-4 w-4" />
            Dashboard
          </Link>
        </Button>
      </div>

      <div className="min-h-0 flex-1">
        <AdminDecisionCenterChat />
      </div>
    </div>
  )
}
