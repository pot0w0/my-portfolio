<script setup lang="ts">
import type { Post, Series } from '~/types/api'

type Item = { kind: 'post'; post: Post } | { kind: 'series'; series: Series }
type View = 'series' | 'all' | 'standalone'

const route = useRoute()
const router = useRouter()
const { list } = usePosts()
const { isLoggedIn } = useAuth()
const { tags, load: loadTax } = useTaxonomy()
const api = useApi()

// ---------- URL query 派生状态 ----------
const page = computed(() => Number(route.query.page) || 1)
const limit = computed(() => Number(route.query.limit) || 10)
const tag = computed(() => (route.query.tag as string) || '')
const userId = computed(() => (route.query.user_id ? Number(route.query.user_id) : undefined))
const q = computed(() => (route.query.q as string) || '')
const sort = computed(() => (route.query.sort as string) || 'created_at')
const order = computed<'asc' | 'desc'>(() => {
  return route.query.order === 'asc' ? 'asc' : 'desc'
})
const year = computed(() => (route.query.year ? Number(route.query.year) : undefined))
const view = computed<View>(() => {
  const v = route.query.view as string
  if (v === 'all' || v === 'standalone') return v
  return 'series'
})

// ---------- 状态 ----------
const items = ref<Item[]>([])
const total = ref(0)
const loading = ref(false)
const errorMsg = ref('')
const showSeriesDialog = ref(false)
const showEditor = ref(false)

// 搜索框本地输入（防抖同步到 URL）
const searchInput = ref(q.value)
let searchTimer: ReturnType<typeof setTimeout> | null = null

watch(searchInput, (v) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    updateQuery({ q: v.trim() || undefined, page: undefined })
  }, 300)
})
watch(q, (v) => { if (v !== searchInput.value) searchInput.value = v })

// ---------- URL 更新工具（唯一入口） ----------
function updateQuery(patch: Record<string, any>) {
  const next: Record<string, any> = { ...route.query, ...patch }
  for (const k of Object.keys(next)) {
    const val = next[k]
    if (val === undefined || val === null || val === '') delete next[k]
  }
  router.push({ query: next })
}

function setView(v: View) {
  updateQuery({ view: v === 'series' ? undefined : v, page: undefined })
}
function setTag(slug: string) {
  updateQuery({ tag: tag.value === slug ? undefined : slug, page: undefined })
}
function clearSearch() {
  searchInput.value = ''
  updateQuery({ q: undefined, page: undefined })
}
function clearUserFilter() {
  updateQuery({ user_id: undefined, page: undefined })
}
function changePage(p: number) {
  updateQuery({ page: p > 1 ? String(p) : undefined })
}
function onSortChange(e: Event) {
  const [s, o] = (e.target as HTMLSelectElement).value.split(':')
  updateQuery({ sort: s === 'created_at' ? undefined : s, order: o === 'desc' ? undefined : o, page: undefined })
}
function onLimitChange(e: Event) {
  const v = Number((e.target as HTMLSelectElement).value)
  updateQuery({ limit: v === 10 ? undefined : String(v), page: undefined })
}
function onYearChange(e: Event) {
  const v = (e.target as HTMLInputElement).value
  updateQuery({ year: v || undefined, page: undefined })
}

// ---------- 数据获取 ----------
async function fetchAll() {
  loading.value = true
  errorMsg.value = ''
  total.value = 0
  items.value = []

  const isSearching = !!q.value
  const isSeriesOnly = view.value === 'series' && !isSearching && !tag.value && !userId.value

  // 系列视图：只拉系列（分页）
  if (isSeriesOnly) {
    try {
      const res = await api.get<{ data: Series[]; total: number; page: number; limit: number }>(
        '/api/series',
        { page: page.value, limit: limit.value, q: q.value || undefined, sort: sort.value, order: order.value },
        { silent: true },
      )
      items.value = res.data.map(series => ({ kind: 'series', series }))
      total.value = res.total
    } catch (e: any) {
      errorMsg.value = e?.message ?? '加载失败'
    } finally {
      loading.value = false
    }
    return
  }

  // 其他视图：拉文章（分页）
  let seriesItems: Item[] = []
  if (view.value === 'all' && !isSearching && !tag.value && !userId.value) {
    // "全部"视图：系列卡片置顶（不分页，取前 20）
    try {
      const seriesRes = await api.get<{ data: Series[] }>(
        '/api/series',
        { page: 1, limit: 20, sort: 'updated_at', order: 'desc' },
        { silent: true },
      )
      seriesItems = seriesRes.data.map(series => ({ kind: 'series', series }))
    } catch { seriesItems = [] }
  }

  try {
    const res = await list({
      page: page.value,
      limit: limit.value,
      user_id: userId.value,
      tag: tag.value || undefined,
      q: q.value || undefined,
      year: year.value,
      sort: sort.value,
      order: order.value,
      standalone: view.value === 'standalone' ? true : undefined,
    })
    items.value = [
      ...seriesItems,
      ...res.data.map((post): Item => ({ kind: 'post', post })),
    ]
    total.value = res.total
  } catch (e: any) {
    errorMsg.value = e?.message ?? '加载失败'
  } finally {
    loading.value = false
  }
}

// 首次加载：taxonomy + 列表
onMounted(async () => {
  try { await loadTax() } catch {}
  await fetchAll()
})

// URL 变化时重新拉（唯一触发点）
watch(() => route.query, () => fetchAll())

// ---------- 创建后的回调 ----------
function onSeriesCreated(s: Series) {
  showSeriesDialog.value = false
  router.push(`/series/${s.slug}`)
}
async function onSaved(_p: Post) {
  showEditor.value = false
  await fetchAll()
}

// 工具条显隐：系列视图且无搜索/标签/用户时，排序/每页/年份对"系列卡片"意义有限（但排序仍有意义，保留）
const showToolbarFilters = computed(() => true)
</script>

<template>
  <div class="space-y-6">
    <!-- 标题 + 操作 -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <h1 class="text-2xl font-bold">
        博客
        <span v-if="userId" class="text-base font-normal text-faint">
          · 用户 #{{ userId }}
          <button class="text-primary ml-2" @click="clearUserFilter">清除</button>
        </span>
      </h1>
      <div class="flex gap-2">
        <ClientOnly>
          <button
            v-if="isLoggedIn"
            class="px-4 py-2 border border-border rounded hover:bg-surface-2 text-sm"
            @click="showSeriesDialog = true"
          >新建系列</button>
          <button
            v-if="isLoggedIn"
            class="px-4 py-2 bg-primary text-white rounded hover:opacity-90"
            @click="showEditor = !showEditor"
          >
            {{ showEditor ? '收起' : '写文章' }}
          </button>
        </ClientOnly>
      </div>
    </div>

    <!-- 搜索框 -->
    <div class="relative">
      <input
        v-model="searchInput"
        type="search"
        placeholder="搜索文章标题或内容…"
        class="w-full border border-border rounded-lg pl-10 pr-10 py-2 bg-surface"
      />
      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-faint pointer-events-none">Q</span>
      <button
        v-if="searchInput"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-faint hover:text-text"
        @click="clearSearch"
        aria-label="清空搜索"
      >✕</button>
    </div>

    <!-- 视图切换 + 工具条 -->
    <div class="flex flex-wrap items-center gap-3 text-sm">
      <div class="flex rounded border border-border overflow-hidden">
        <button
          class="px-3 py-1"
          :class="view === 'series' ? 'bg-primary text-white' : 'hover:bg-surface-2'"
          @click="setView('series')"
        >系列</button>
        <button
          class="px-3 py-1 border-l border-border"
          :class="view === 'all' ? 'bg-primary text-white' : 'hover:bg-surface-2'"
          @click="setView('all')"
        >全部</button>
        <button
          class="px-3 py-1 border-l border-border"
          :class="view === 'standalone' ? 'bg-primary text-white' : 'hover:bg-surface-2'"
          @click="setView('standalone')"
        >散篇</button>
      </div>

      <template v-if="showToolbarFilters">
        <!-- 排序 -->
        <label class="flex items-center gap-1.5">
          <span class="text-faint">排序</span>
          <select
            class="border border-border rounded px-2 py-1 bg-surface"
            :value="`${sort}:${order}`"
            @change="onSortChange"
          >
            <option value="created_at:desc">最新</option>
            <option value="created_at:asc">最早</option>
            <option value="title:asc">标题 A→Z</option>
            <option value="title:desc">标题 Z→A</option>
            <option v-if="view === 'standalone'" value="series_order:asc">系列内顺序</option>
          </select>
        </label>

        <!-- 每页 -->
        <label class="flex items-center gap-1.5">
          <span class="text-faint">每页</span>
          <select
            class="border border-border rounded px-2 py-1 bg-surface"
            :value="String(limit)"
            @change="onLimitChange"
          >
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </select>
        </label>

        <!-- 年份：系列视图无意义，隐藏 -->
        <label v-if="view !== 'series'" class="flex items-center gap-1.5">
          <span class="text-faint">年份</span>
          <input
            type="number"
            class="border border-border rounded px-2 py-1 w-24 bg-surface"
            :value="year ?? ''"
            placeholder="全部"
            @change="onYearChange"
          />
        </label>
      </template>
    </div>

    <!-- 标签筛选：搜索时不显示 -->
    <div v-if="tags.length && !q" class="flex gap-2 flex-wrap">
      <button
        v-for="t in tags" :key="t.id"
        class="px-2 py-0.5 rounded text-xs border border-border"
        :class="tag === t.slug ? 'bg-primary/10 text-primary border-primary/40' : 'text-muted'"
        @click="setTag(t.slug)"
      ># {{ t.name }}<span v-if="t.post_count" class="text-faint ml-1">({{ t.post_count }})</span></button>
    </div>

    <PostEditor v-if="showEditor" :post="null" @saved="onSaved" @cancel="showEditor = false" />

    <!-- 搜索提示 -->
    <p v-if="q" class="text-sm text-muted">
      “{{ q }}” 的搜索结果：{{ total }} 篇
      <button class="text-primary ml-2" @click="clearSearch">清空</button>
    </p>

    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>
    <p v-else-if="!items.length" class="text-faint">
      {{ q ? '没有匹配的文章' : (view === 'series' ? '还没有系列' : '暂无内容') }}
    </p>

    <div v-else class="flex flex-col gap-4">
      <ContentCard
        v-for="it in items"
        :key="it.kind === 'series' ? `s-${it.series.id}` : `p-${it.post.id}`"
        :item="it"
      />
    </div>

    <Pagination
      v-if="total > limit"
      :page="page"
      :total="total"
      :limit="limit"
      @change="changePage"
    />

    <SeriesCreateDialog
      :open="showSeriesDialog"
      @close="showSeriesDialog = false"
      @created="onSeriesCreated"
    />
  </div>
</template>