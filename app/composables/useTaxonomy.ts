import type { Tag } from '~/types/api'

export function useTaxonomy() {
  const api = useApi()
  const tags = useState<Tag[]>('tax:tags', () => [])
  const loaded = useState<boolean>('tax:loaded', () => false)

  async function load(force = false) {
    if (loaded.value && !force) return
    try {
      tags.value = await api.get<Tag[]>('/api/tags', undefined, { silent: true })
      loaded.value = true
    } catch {}
  }

  return { tags, load }
}