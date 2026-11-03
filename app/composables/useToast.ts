export interface Toast {
  id: number
  type: 'error' | 'success' | 'info'
  message: string
}

let seq = 0

export function useToast() {
  const toasts = useState<Toast[]>('toasts', () => [])

  function push(type: Toast['type'], message: string, duration = 4000) {
    const id = ++seq
    toasts.value.push({ id, type, message })
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
    return id
  }

  function dismiss(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  const error = (msg: string, duration?: number) => push('error', msg, duration)
  const success = (msg: string, duration?: number) => push('success', msg, duration)
  const info = (msg: string, duration?: number) => push('info', msg, duration)

  return { toasts, push, dismiss, error, success, info }
}