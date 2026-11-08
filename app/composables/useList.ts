import type { PageOut } from '~/types/api'

export interface ListQuery {
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
  q?: string
  [key: string]: any
}

export function useList<T>(
  fetcher: (query: ListQuery) => Promise<PageOut<T>>,
  initial: ListQuery = {},
) {
  const route = useRoute()
  const router = useRouter()

  function pickFromRoute(): ListQuery {
    const out: ListQuery = {}
    for (const k of Object.keys(route.query)) {
      const v = route.query[k]
      if (typeof v === 'string') {
        if (k === 'page' || k === 'limit' || k === 'year') out[k] = Number(v)
        else out[k] = v
      }
    }
    return out
  }

  const query = reactive<ListQuery>({
    page: 1,
    limit: 10,
    sort: 'created_at',
    order: 'desc',
    ...initial,
    ...pickFromRoute(),
  })

  const data = ref<T[]>([]) as Ref<T[]>
  const total = ref(0)
  const loading = ref(false)
  const error = ref('')

  async function load() {
    loading.value = true
    error.value = ''
    try {
      const res = await fetcher(query)
      data.value = res.data
      total.value = res.total
    } catch (e: any) {
      error.value = e?.message ?? '加载失败'
      data.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  function update(patch: Partial<ListQuery>, opts: { resetPage?: boolean } = {}) {
    if (opts.resetPage) patch.page = 1
    Object.assign(query, patch)

    const next: Record<string, any> = { ...route.query }
    for (const k of Object.keys(query)) {
      const v = query[k]
      if (v === undefined || v === null || v === '') delete next[k]
      else next[k] = String(v)
    }
    router.push({ query: next })
  }

  // URL 变化时同步 query 并重新加载
  watch(() => route.query, () => {
    Object.assign(query, pickFromRoute())
    load()
  })

  return { query, data, total, loading, error, load, update }
}