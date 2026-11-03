export function useMediaUrl() {
  const config = useRuntimeConfig()
  return (path?: string | null) => {
    if (!path) return ''
    if (/^https?:\/\//.test(path)) return path
    return `${config.public.apiBase}${path}`
  }
}