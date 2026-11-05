<script setup lang="ts">
import type { Post } from '~/types/api'

const route = useRoute()
const router = useRouter()
const { list, create } = usePosts()
const { isLoggedIn } = useAuth()
const { categories, tags, load: loadTax } = useTaxonomy()

const category = computed(() => (route.query.category as string) || '')
const tag = computed(() => (route.query.tag as string) || '')

onMounted(() => loadTax())

watch(
  () => route.query,
  () => { page.value = Number(route.query.page) || 1; fetchPosts() },
  { immediate: true },
)

function setCategory(slug: string) {
  router.push({ query: { ...route.query, category: slug || undefined, page: '1' } })
}
function setTag(slug: string) {
  router.push({ query: { ...route.query, tag: slug || undefined, page: '1' } })
}


const page = ref(Number(route.query.page) || 1)
const limit = ref(10)
const userId = computed(() =>
  route.query.user_id ? Number(route.query.user_id) : undefined,
)

const posts = ref<Post[]>([])
const total = ref(0)
const loading = ref(false)
const errorMsg = ref('')

const { totalPages, canPrev, canNext, go } = usePagination(page, limit, total)

async function fetchPosts() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await list({
      page: page.value,
      limit: limit.value,
      user_id: userId.value,
    })
    posts.value = res.data
    total.value = res.total
  } catch (e: any) {
    errorMsg.value = e?.message ?? '加载失败'
  } finally {
    loading.value = false
  }
}

function changePage(p: number) {
  go(p)
  router.push({ query: { ...route.query, page: page.value } })
}

function clearUserFilter() {
  const q = { ...route.query }
  delete q.user_id
  q.page = '1'
  router.push({ query: q })
}

watch(
  () => route.query,
  () => {
    page.value = Number(route.query.page) || 1
    fetchPosts()
  },
  { immediate: true },
)

// 新建文章
const showEditor = ref(false)
const saveError = ref('')

async function onSave(payload: { title: string; content: string }) {
  saveError.value = ''
  try {
    await create(payload)
    showEditor.value = false
    await fetchPosts()
  } catch (e: any) {
    saveError.value = e?.message ?? '保存失败'
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- 分类 tab -->
    <div class="flex gap-2 border-b border-border pb-2 mb-4 overflow-x-auto">
      <button
        class="px-3 py-1 rounded-full text-sm whitespace-nowrap"
        :class="!category ? 'bg-primary text-white' : 'hover:bg-surface-2'"
        @click="setCategory('')"
      >全部</button>
      <button
        v-for="c in categories" :key="c.id"
        class="px-3 py-1 rounded-full text-sm whitespace-nowrap"
        :class="category === c.slug ? 'bg-primary text-white' : 'hover:bg-surface-2'"
        @click="setCategory(c.slug)"
      >{{ c.name }}</button>
    </div>
    <!-- 标签筛选 -->
    <div class="flex gap-2 flex-wrap mb-6">
      <button
        v-for="t in tags" :key="t.id"
        class="px-2 py-0.5 rounded text-xs border border-border"
        :class="tag === t.slug ? 'bg-primary/10 text-primary border-primary/40' : 'text-muted'"
        @click="setTag(tag === t.slug ? '' : t.slug)"
      ># {{ t.name }}</button>
    </div>
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold">
        博客
        <span v-if="userId" class="text-base font-normal text-faint">
          · 用户 #{{ userId }} 的文章
          <button class="text-primary ml-2" @click="clearUserFilter">清除</button>
        </span>
      </h1>
      <button
        v-if="isLoggedIn"
        class="px-4 py-2 bg-primary text-white rounded hover:bg-blue-700"
        @click="showEditor = !showEditor"
      >
        {{ showEditor ? '收起' : '写文章' }}
      </button>
    </div>

    <PostEditor
      v-if="showEditor"
      @save="onSave"
      @cancel="showEditor = false"
    />
    <p v-if="saveError" class="text-sm text-danger">{{ saveError }}</p>

    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>
    <p v-else-if="!posts.length" class="text-faint">暂无文章</p>

    <div v-else class="grid gap-4">
      <PostCard v-for="p in posts" :key="p.id" :post="p" />
    </div>

    <Pagination
      v-if="total > 0"
      :page="page"
      :total-pages="totalPages"
      @change="changePage"
    />
  </div>
</template>