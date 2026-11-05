import type { Category, Tag } from '~/types/api'

export function useTaxonomy() {
  const api = useApi()
  const categories = useState<Category[]>('tax:categories', () => [])
  const tags = useState<Tag[]>('tax:tags', () => [])
  const loaded = useState<boolean>('tax:loaded', () => false)

  async function load(force = false) {
    if (loaded.value && !force) return
    try {
      const [c, t] = await Promise.all([
        api.get<Category[]>('/api/categories', undefined, { silent: true }),
        api.get<Tag[]>('/api/tags', undefined, { silent: true }),
      ])
      categories.value = c
      tags.value = t
      loaded.value = true
    } catch {
      // 静默失败，页面用空数组
    }
  }

  return { categories, tags, load }
}