import { get, post, getApiConfig, getStoredToken } from '@/utils/apiWrapper'

export interface AIHealthResponse {
  enabled: boolean
  model?: string | null
}

export interface AISummaryResponse {
  summary: string
}

export interface AIChatRequest {
  message: string
  history?: Array<{ role: 'user' | 'assistant'; content: string }>
}

export interface AIChatResponse {
  reply: string
}

/** Respuesta estructurada de módulos de inteligencia de negocio (GET /admin/ai/...). */
export interface AIBusinessModulePayload {
  summary: string
  data: Record<string, unknown>
  recommendations: string[]
  generated_at: string
}

export const aiService = {
  async getHealth(): Promise<AIHealthResponse> {
    return get<AIHealthResponse>('/admin/ai/health')
  },

  async getSummary(timeRange: string = 'monthly'): Promise<AISummaryResponse> {
    return get<AISummaryResponse>(`/admin/ai/summary?time_range=${timeRange}`)
  },

  async chat(message: string, history?: Array<{ role: 'user' | 'assistant'; content: string }>): Promise<AIChatResponse> {
    return post<AIChatResponse>('/admin/ai/chat', { message, history })
  },

  async getDemandPrediction(params?: {
    product_id?: number
    category_id?: number
    time_range?: number
  }): Promise<AIBusinessModulePayload> {
    const sp = new URLSearchParams()
    if (params?.product_id != null) sp.set('product_id', String(params.product_id))
    if (params?.category_id != null) sp.set('category_id', String(params.category_id))
    if (params?.time_range != null) sp.set('time_range', String(params.time_range))
    const q = sp.toString()
    return get<AIBusinessModulePayload>(`/admin/ai/predictions/demand${q ? `?${q}` : ''}`)
  },

  async getProductionRecommendations(params?: {
    time_range?: number
    safety_factor?: number
  }): Promise<AIBusinessModulePayload> {
    const sp = new URLSearchParams()
    if (params?.time_range != null) sp.set('time_range', String(params.time_range))
    if (params?.safety_factor != null) sp.set('safety_factor', String(params.safety_factor))
    const q = sp.toString()
    return get<AIBusinessModulePayload>(`/admin/ai/recommendations/production${q ? `?${q}` : ''}`)
  },

  async getAnomalies(params?: { days_recent?: number; days_baseline?: number }): Promise<AIBusinessModulePayload> {
    const sp = new URLSearchParams()
    if (params?.days_recent != null) sp.set('days_recent', String(params.days_recent))
    if (params?.days_baseline != null) sp.set('days_baseline', String(params.days_baseline))
    const q = sp.toString()
    return get<AIBusinessModulePayload>(`/admin/ai/alerts/anomalies${q ? `?${q}` : ''}`)
  },

  async getExportReadiness(params?: { limit?: number }): Promise<AIBusinessModulePayload> {
    const sp = new URLSearchParams()
    if (params?.limit != null) sp.set('limit', String(params.limit))
    const q = sp.toString()
    return get<AIBusinessModulePayload>(`/admin/ai/export/readiness${q ? `?${q}` : ''}`)
  },

  async getBusinessInsights(): Promise<AIBusinessModulePayload> {
    return get<AIBusinessModulePayload>('/admin/ai/insights')
  },

  /**
   * Chat con streaming (SSE). Llama onChunk(accumulatedText) por cada fragmento y onDone() al terminar.
   * En caso de error llama onError(error) y no onDone.
   * También puede recibir metadata sobre entidades afectadas para invalidar queries.
   */
  async chatStream(
    message: string,
    callbacks: {
      onChunk: (text: string) => void
      onDone: () => void
      onError: (err: Error) => void
      onMetadata?: (metadata: { affected_entities: string[] }) => void
    }
  ): Promise<void> {
    const { baseURL } = getApiConfig()
    const token = getStoredToken()
    const url = `${baseURL}/admin/ai/chat/stream`
    let accumulated = ''

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message }),
      })

      if (!res.ok) {
        const detail = (await res.json().catch(() => ({})))?.detail ?? res.statusText
        callbacks.onError(new Error(detail))
        return
      }

      const reader = res.body?.getReader()
      if (!reader) {
        callbacks.onError(new Error('No se pudo leer la respuesta'))
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const payload = line.slice(6).trim()
            if (payload === '[DONE]' || !payload) continue
            try {
              const data = JSON.parse(payload) as { text?: string; error?: string; metadata?: { affected_entities?: string[] } }
              if (data.error) {
                callbacks.onError(new Error(data.error))
                return
              }
              if (typeof data.text === 'string') {
                accumulated += data.text
                callbacks.onChunk(accumulated)
              }
              // Manejar metadata sobre entidades afectadas
              if (data.metadata?.affected_entities && callbacks.onMetadata) {
                callbacks.onMetadata({ affected_entities: data.metadata.affected_entities })
              }
            } catch {
              // ignorar líneas no JSON
            }
          }
        }
      }

      if (buffer.startsWith('data: ')) {
        const payload = buffer.slice(6).trim()
        if (payload && payload !== '[DONE]') {
          try {
            const data = JSON.parse(payload) as { text?: string; error?: string; metadata?: { affected_entities?: string[] } }
            if (data.error) callbacks.onError(new Error(data.error))
            else if (typeof data.text === 'string') {
              accumulated += data.text
              callbacks.onChunk(accumulated)
            }
            // Manejar metadata sobre entidades afectadas
            if (data.metadata?.affected_entities && callbacks.onMetadata) {
              callbacks.onMetadata({ affected_entities: data.metadata.affected_entities })
            }
          } catch {
            // ignore
          }
        }
      }

      callbacks.onDone()
    } catch (err) {
      callbacks.onError(err instanceof Error ? err : new Error(String(err)))
    }
  },
}
