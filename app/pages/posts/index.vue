<script setup lang="ts">
import type { Post, PostPayload, Series } from '~/types/api'

type Item = { kind: 'post'; post: Post } | { kind: 'series'; series: Series }

const route = useRoute()
const router = useRouter()
const { list, create } = usePosts()
const { isLoggedIn } = useAuth()
const { tags, load: loadTax } = useTaxonomy()
const api = useApi()

const page = ref(Number(route.query.page) || 1)
const limit = ref(10)
const tag = computed(() => (route.query.tag as string) || '')
const userId = computed(() => route.query.user_id ? Number(route.query.user_id) : undefined)
const q = computed(() => (route.query.q as string) || '')

const items = ref<Item[]>([])
const total = ref(0)
const loading = ref(false)
const errorMsg = ref('')
const { totalPages, go } = usePagination(page, limit, total)

// 搜索框本地输入（防抖后同步到 URL）
const searchInput = ref(q.value)
let searchTimer: ReturnType<typeof setTimeout> | null = null
const showSeriesDialog = ref(false)

watch(searchInput, (v) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    const query = { ...route.query, q: v.trim() || undefined, page: '1' }
    router.push({ query })
  }, 300)
})

// URL 变化时同步回搜索框（比如浏览器前进后退、清空）
watch(q, (v) => {
  if (v !== searchInput.value) searchInput.value = v
})

function onSeriesCreated(s: Series) {
  showSeriesDialog.value = false
  router.push(`/series/${s.slug}`)
}

async function fetchAll() {
  loading.value = true
  errorMsg.value = ''

  const isSearching = !!q.value

  // 系列：搜索时不显示系列卡片，只显示匹配文章
  let seriesItems: Item[] = []
  if (!isSearching && !tag.value && !userId.value) {
    try {
      const seriesRes = await api.get<Series[]>('/api/series', undefined, { silent: true })
      seriesItems = seriesRes.map(series => ({ kind: 'series', series }))
    } catch { seriesItems = [] }
  }

  let postItems: Item[] = []
  try {
    const postsRes = await list({
      page: page.value,
      limit: limit.value,
      user_id: userId.value,
      tag: tag.value || undefined,
      q: q.value || undefined,
      // 搜索时不要 standalone=true，否则系列文章搜不到
      standalone: !isSearching && !tag.value && !userId.value,
    })
    postItems = postsRes.data.map(post => ({ kind: 'post', post }))
    total.value = postsRes.total
  } catch (e: any) {
    errorMsg.value = e?.message ?? '加载失败'
    total.value = 0
  }

  items.value = [...seriesItems, ...postItems]
  loading.value = false
}

function clearSearch() {
  searchInput.value = ''
  router.push({ query: { ...route.query, q: undefined, page: '1' } })
}

function changePage(p: number) {
  go(p)
  router.push({ query: { ...route.query, page: String(page.value) } })
}
function setTag(slug: string) {
  router.push({ query: { ...route.query, tag: tag.value === slug ? undefined : slug, page: '1' } })
}
function clearUserFilter() {
  const q2 = { ...route.query }; delete q2.user_id; q2.page = '1'; router.push({ query: q2 })
}

onMounted(async () => {
  try { await loadTax() } catch {}
  await fetchAll()
})

watch(() => route.query, async () => {
  page.value = Number(route.query.page) || 1
  await fetchAll()
})

const showEditor = ref(false)
async function onSaved(_p: Post) {
  showEditor.value = false
  await fetchAll()
}
</script>

<template>
  <div class="space-y-6">
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
      <span class="absolute left-3 top-1/2 -translate-y-1/2 text-faint pointer-events-none">🔍</span>
      <button
        v-if="searchInput"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-faint hover:text-text"
        @click="clearSearch"
        aria-label="清空搜索"
      >✕</button>
    </div>

    <!-- 标签筛选 -->
    <div v-if="tags.length && !q" class="flex gap-2 flex-wrap">
      <button
        v-for="t in tags" :key="t.id"
        class="px-2 py-0.5 rounded text-xs border border-border"
        :class="tag === t.slug ? 'bg-primary/10 text-primary border-primary/40' : 'text-muted'"
        @click="setTag(t.slug)"
      ># {{ t.name }}</button>
    </div>

    <PostEditor v-if="showEditor" :post="null" @saved="onSaved" @cancel="showEditor = false" />

    <!-- 搜索结果提示 -->
    <p v-if="q" class="text-sm text-muted">
      “{{ q }}” 的搜索结果：{{ total }} 篇
      <button class="text-primary ml-2" @click="clearSearch">清空</button>
    </p>

    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>
    <p v-else-if="!items.length" class="text-faint">
      {{ q ? '没有匹配的文章' : '暂无内容' }}
    </p>

    <div v-else class="flex flex-col gap-4">
      <ContentCard
        v-for="it in items"
        :key="it.kind === 'series' ? `s-${it.series.id}` : `p-${it.post.id}`"
        :item="it"
      />
    </div>

    <Pagination v-if="total > 0" :page="page" :total-pages="totalPages" @change="changePage" />
    
    <SeriesCreateDialog
      :open="showSeriesDialog"
      @close="showSeriesDialog = false"
      @created="onSeriesCreated"
    />
  </div>
</template>