'use client'

import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Button,
} from '@/components/ui'
import { AdminDecisionCenterChat } from '@/components/admin/admin-decision-center-chat'
import { MessageResponse } from '@/components/ai-elements/message'
import { aiService, type AIBusinessModulePayload } from '@/services/ai.service'
import { IconArrowLeft, IconRefresh } from '@tabler/icons-react'

function BusinessModulePanel({
  title,
  description,
  tabValue,
  queryKey,
  queryFn,
}: {
  title: string
  description: string
  tabValue: string
  queryKey: readonly string[]
  queryFn: () => Promise<AIBusinessModulePayload>
}) {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey,
    queryFn,
    staleTime: 60_000,
  })

  return (
    <TabsContent value={tabValue} className="mt-4 space-y-4">
      <Card>
        <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-2 space-y-0">
          <div className="space-y-1">
            <CardTitle className="text-lg">{title}</CardTitle>
            <CardDescription>{description}</CardDescription>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => void refetch()}
            disabled={isFetching}
            className="shrink-0 gap-1"
          >
            <IconRefresh className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
            Actualizar
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading && (
            <p className="text-sm text-muted-foreground">Cargando análisis…</p>
          )}
          {isError && (
            <p className="text-sm text-destructive">
              {(error as Error)?.message ?? 'No se pudo cargar este módulo.'}
            </p>
          )}
          {data && !isLoading && (
            <>
              <div className="rounded-lg border bg-muted/30 p-3">
                <MessageResponse>{data.summary}</MessageResponse>
              </div>
              {data.recommendations?.length ? (
                <div>
                  <h4 className="mb-2 text-sm font-medium">Recomendaciones</h4>
                  <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
                    {data.recommendations.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              <details className="rounded-md border text-sm">
                <summary className="cursor-pointer select-none px-3 py-2 font-medium">
                  Datos estructurados (JSON)
                </summary>
                <pre className="max-h-64 overflow-auto border-t bg-muted/20 p-3 text-xs leading-relaxed">
                  {JSON.stringify(data.data, null, 2)}
                </pre>
              </details>
              <p className="text-xs text-muted-foreground">
                Generado: {data.generated_at}
              </p>
            </>
          )}
        </CardContent>
      </Card>
    </TabsContent>
  )
}

export default function AdminAIDecisionCenterPage() {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2 w-fit gap-1">
            <Link href="/admin/analytics">
              <IconArrowLeft className="h-4 w-4" />
              Volver a analíticas
            </Link>
          </Button>
          <h1 className="text-2xl font-semibold tracking-tight">
            Centro de decisiones IA
          </h1>
          <p className="text-muted-foreground text-sm text-pretty max-w-2xl">
            Paneles de demanda, producción, anomalías y exportación más un chat con
            el mismo asistente del panel (streaming). Los datos provienen de heurísticas
            sobre ventas completadas; el chat puede combinar herramientas automáticamente.
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2 lg:items-start">
        <div className="min-w-0 space-y-2">
          <h2 className="text-sm font-medium text-muted-foreground">
            Inteligencia estructurada
          </h2>
          <Tabs defaultValue="demand" className="w-full">
            <TabsList className="flex h-auto w-full flex-wrap justify-start gap-1">
              <TabsTrigger value="demand">Demanda</TabsTrigger>
              <TabsTrigger value="production">Producción</TabsTrigger>
              <TabsTrigger value="anomalies">Anomalías</TabsTrigger>
              <TabsTrigger value="export">Exportación</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>

            <BusinessModulePanel
              tabValue="demand"
              title="Predicción de demanda"
              description="Heurística por ventana temporal y tendencia reciente vs histórico."
              queryKey={['admin-ai', 'demand'] as const}
              queryFn={() => aiService.getDemandPrediction({ time_range: 30 })}
            />
            <BusinessModulePanel
              tabValue="production"
              title="Recomendaciones de producción"
              description="Cruce de demanda estimada e inventario con factor de seguridad."
              queryKey={['admin-ai', 'production'] as const}
              queryFn={() =>
                aiService.getProductionRecommendations({
                  time_range: 30,
                  safety_factor: 1.15,
                })
              }
            />
            <BusinessModulePanel
              tabValue="anomalies"
              title="Detección de anomalías"
              description="Reglas sobre caídas, picos y baja rotación."
              queryKey={['admin-ai', 'anomalies'] as const}
              queryFn={() =>
                aiService.getAnomalies({ days_recent: 14, days_baseline: 28 })
              }
            />
            <BusinessModulePanel
              tabValue="export"
              title="Preparación para exportación"
              description="Candidatos y pasos sugeridos según desempeño."
              queryKey={['admin-ai', 'export'] as const}
              queryFn={() => aiService.getExportReadiness({ limit: 10 })}
            />
            <BusinessModulePanel
              tabValue="insights"
              title="Insights unificados"
              description="Resumen agregado de los módulos anteriores."
              queryKey={['admin-ai', 'insights'] as const}
              queryFn={() => aiService.getBusinessInsights()}
            />
          </Tabs>
        </div>

        <div className="min-w-0 space-y-2 lg:sticky lg:top-20">
          <h2 className="text-sm font-medium text-muted-foreground">
            Asistente (assistant-ui)
          </h2>
          <AdminDecisionCenterChat />
          <p className="text-xs text-muted-foreground text-pretty">
            Misma API que el widget del header. Usa el panel izquierdo para números
            rápidos y el chat para preguntas abiertas o planes de acción.
          </p>
        </div>
      </div>
    </div>
  )
}
