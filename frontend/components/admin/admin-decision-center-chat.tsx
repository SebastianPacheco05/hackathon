'use client'

import { useMemo } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter,
  type ChatModelRunOptions,
} from '@assistant-ui/react'
import { Thread } from '@/components/thread'
import { aiService } from '@/services/ai.service'
import { PRODUCT_KEYS } from '@/hooks/use-products'

function extractLastUserText(
  messages: ChatModelRunOptions['messages']
): string {
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i]
    if (m.role !== 'user') continue
    const { content } = m
    if (typeof content === 'string') return content
    if (!Array.isArray(content)) continue
    const text = content
      .filter(
        (p): p is { type: 'text'; text: string } =>
          p.type === 'text' && typeof (p as { text?: string }).text === 'string'
      )
      .map((p) => p.text)
      .join('')
    if (text) return text
  }
  return ''
}

function useInvalidateAffectedQueries() {
  const queryClient = useQueryClient()
  return (affectedEntities: string[]) => {
    affectedEntities.forEach((entity) => {
      switch (entity) {
        case 'brands':
          queryClient.invalidateQueries({ queryKey: ['brands'] })
          break
        case 'providers':
          queryClient.invalidateQueries({ queryKey: ['providers'] })
          break
        case 'categories':
          queryClient.invalidateQueries({ queryKey: ['categories'] })
          break
        case 'discounts':
          queryClient.invalidateQueries({ queryKey: ['discounts'] })
          break
        case 'products':
          queryClient.invalidateQueries({ queryKey: PRODUCT_KEYS.all })
          break
        case 'filter-options':
          queryClient.invalidateQueries({ queryKey: ['filter-options'] })
          break
        default:
          console.warn(`Entidad desconocida para invalidar: ${entity}`)
      }
    })
    queryClient.invalidateQueries({ queryKey: ['admin-ai'] })
  }
}

/**
 * Shell assistant-ui + streaming del backend existente (/admin/ai/chat/stream).
 */
export function AdminDecisionCenterChat() {
  const invalidateAffected = useInvalidateAffectedQueries()

  const adapter = useMemo<ChatModelAdapter>(
    () => ({
      async *run({ messages, abortSignal }: ChatModelRunOptions) {
        const text = extractLastUserText(messages)
        if (!text) return

        const updates: Array<
          | { type: 'chunk'; accumulated: string }
          | { type: 'done' }
          | { type: 'err'; error: Error }
        > = []
        let resume: (() => void) | null = null
        const waitForUpdate = () =>
          new Promise<void>((resolve) => {
            resume = resolve
          })

        void aiService.chatStream(text, {
          onChunk(accumulated) {
            updates.push({ type: 'chunk', accumulated })
            resume?.()
            resume = null
          },
          onDone() {
            updates.push({ type: 'done' })
            resume?.()
            resume = null
          },
          onError(err) {
            updates.push({ type: 'err', error: err })
            resume?.()
            resume = null
          },
          onMetadata(metadata) {
            if (metadata.affected_entities?.length) {
              invalidateAffected(metadata.affected_entities)
            }
          },
        })

        while (true) {
          if (!updates.length) await waitForUpdate()
          if (abortSignal.aborted) return

          const item = updates.shift()!
          if (item.type === 'err') {
            yield {
              content: [
                {
                  type: 'text',
                  text: item.error.message || 'Error al contactar la IA',
                },
              ],
            }
            return
          }
          if (item.type === 'done') break
          if (item.type === 'chunk') {
            if (item.accumulated) {
              // assistant-ui espera el snapshot acumulado del mensaje en cada update.
              yield { content: [{ type: 'text', text: item.accumulated }] }
            }
          }
        }
      },
    }),
    [invalidateAffected]
  )

  const runtime = useLocalRuntime(adapter)

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div
        className="flex h-full min-h-0 w-full flex-col overflow-hidden rounded-3xl border border-border/60 bg-muted/20 shadow-[0_8px_30px_rgb(0,0,0,0.06)] dark:border-border/50 dark:bg-muted/10 dark:shadow-[0_8px_30px_rgb(0,0,0,0.25)]"
      >
        <Thread contentMaxWidth="min(64rem, 100%)" />
      </div>
    </AssistantRuntimeProvider>
  )
}
