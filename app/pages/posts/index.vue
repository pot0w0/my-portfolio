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

const items = ref<Item[]>([])
const total = ref(0)
const loading = ref(false)
const errorMsg = ref('')
const { totalPages, go } = usePagination(page, limit, total)

const showEditor = ref(false)

async function fetchAll() {
  loading.value = true
  errorMsg.value = ''

  let seriesItems: Item[] = []
  if (!tag.value && !userId.value) {
    try {
      const seriesRes = await api.get<Series[]>('/api/series', undefined, { silent: true })
      seriesItems = seriesRes.map(series => ({ kind: 'series', series }))
    } catch (e: any) {
      console.warn('series load failed', e)
      seriesItems = []
    }
  }

  let postItems: Item[] = []
  try {
    const postsRes = await list({
      page: page.value,
      limit: limit.value,
      user_id: userId.value,
      tag: tag.value || undefined,
      standalone: !tag.value && !userId.value,
    })
    postItems = postsRes.data.map(post => ({ kind: 'post', post }))
    total.value = postsRes.total
  } catch (e: any) {
    console.error('posts load failed', e)
    errorMsg.value = e?.message ?? '加载失败'
    total.value = 0
  }

  items.value = [...seriesItems, ...postItems]
  loading.value = false
}

function changePage(p: number) {
  go(p)
  router.push({ query: { ...route.query, page: String(page.value) } })
}
function setTag(slug: string) {
  router.push({ query: { ...route.query, tag: tag.value === slug ? undefined : slug, page: '1' } })
}
function clearUserFilter() {
  const q = { ...route.query }; delete q.user_id; q.page = '1'; router.push({ query: q })
}

onMounted(async () => {
  await loadTax()
  await fetchAll()
})

watch(() => route.query, async () => {
  page.value = Number(route.query.page) || 1
  await fetchAll()
})

async function onSave(payload: PostPayload) {
  try {
    await create(payload)
    showEditor.value = false
    await fetchAll()
  } catch {}
}

const showSeriesDialog = ref(false)

async function onSeriesCreated(s: Series) {
  await fetchAll()
  router.push(`/series/${s.slug}`)
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">
        博客
        <span v-if="userId" class="text-base font-normal text-faint">
          · 用户 #{{ userId }}
          <button class="text-primary ml-2" @click="clearUserFilter">清除</button>
        </span>
      </h1>
        <div class="flex gap-2">
          <button
            v-if="isLoggedIn"
            class="px-4 py-2 border border-border rounded hover:bg-surface-2 text-sm"
            @click="showSeriesDialog = true"
          >新建系列</button>
          <button v-if="isLoggedIn" class="px-4 py-2 bg-primary text-white rounded hover:opacity-90" @click="showEditor = !showEditor">
            {{ showEditor ? '收起' : '写文章' }}
          </button>
        </div>

        <SeriesCreateDialog
          :open="showSeriesDialog"
          @close="showSeriesDialog = false"
          @created="onSeriesCreated"
        />
      <!-- <div class="flex gap-2">
        <NuxtLink v-if="isLoggedIn" to="/series/new" class="px-4 py-2 border border-border rounded hover:bg-surface-2 text-sm">新建系列</NuxtLink>
        <button v-if="isLoggedIn" class="px-4 py-2 bg-primary text-white rounded hover:opacity-90" @click="showEditor = !showEditor">
          {{ showEditor ? '收起' : '写文章' }}
        </button>
      </div> -->
    </div>

    <div v-if="tags.length" class="flex gap-2 flex-wrap">
      <button v-for="t in tags" :key="t.id"
        class="px-2 py-0.5 rounded text-xs border border-border"
        :class="tag === t.slug ? 'bg-primary/10 text-primary border-primary/40' : 'text-muted'"
        @click="setTag(t.slug)"># {{ t.name }}</button>
    </div>

    <PostEditor 
      v-if="showEditor" 
      :post="null"
      @save="onSave" 
      @cancel="showEditor = false" 
    />

    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>
    <p v-else-if="!items.length" class="text-faint">暂无内容</p>

    <div v-else class="flex flex-col gap-4">
      <ContentCard
        v-for="it in items"
        :key="it.kind === 'series' ? `s-${it.series.id}` : `p-${it.post.id}`"
        :item="it"
      />
    </div>

    <Pagination v-if="total > 0" :page="page" :total-pages="totalPages" @change="changePage" />
  </div>
</template>