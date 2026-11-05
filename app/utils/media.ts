export function useMediaUrl() {
  const config = useRuntimeConfig()
  return (path?: string | null) => {
    if (!path) return ''
    if (/^https?:\/\//.test(path) || path.startsWith('blob:')) return path
    return `${config.public.apiBase}${path}`
  }
}