import type { Tag } from '~/types/api'

export function useTaxonomy() {
  const api = useApi()
  const tags = useState<Tag[]>('tax:tags', () => [])
  const loaded = useState<boolean>('tax:loaded', () => false)

  async function load(force = false) {
    if (loaded.value && !force) return
    try {
      const res = await api.get<PageOut<Tag>>('/api/tags', { limit: 200 }, { silent: true })
      tags.value = res.data
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