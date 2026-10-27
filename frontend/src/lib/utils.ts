import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleString()
}

export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const then = new Date(date)
  const diffMs = now.getTime() - then.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffSecs < 60) return `${diffSecs}s ago`
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return then.toLocaleDateString()
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'critical': return 'text-crisis-600 bg-crisis-100'
    case 'high': return 'text-alert-600 bg-alert-100'
    case 'medium': return 'text-amber-600 bg-amber-100'
    case 'low': return 'text-blue-600 bg-blue-100'
    default: return 'text-slate-600 bg-slate-100'
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'completed': return 'text-safe-600 bg-safe-100'
    case 'running': return 'text-crisis-600 bg-crisis-100'
    case 'accepted': return 'text-alert-600 bg-alert-100'
    case 'failed': return 'text-crisis-600 bg-crisis-100'
    default: return 'text-slate-600 bg-slate-100'
  }
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export function generateId(): string {
  return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}