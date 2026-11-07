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

  async function createTag(name: string, slug?: string) {
    const api = useApi()
    const s = slug || name.toLowerCase().trim().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
    const t = await api.post<Tag>('/api/tags', { name: name.trim(), slug: s })
    tags.value.push(t)
    return t
  }
  return { tags, load, createTag }
}