/**
 * Cuando es true, la ruta /admin/ai puede usarse sin sesión (layout sin AdminGuard)
 * y el streaming no envía Bearer (evita 401 por token caducado).
 * El backend en development ya permite chat sin JWT; en production hace falta
 * ADMIN_AI_PUBLIC_CHAT=true o usuario admin autenticado.
 */
export const isAdminAiPublicChatEnabled =
  process.env.NEXT_PUBLIC_ADMIN_AI_PUBLIC_CHAT === 'true' ||
  process.env.NEXT_PUBLIC_ADMIN_AI_PUBLIC_CHAT === '1'
