<script setup lang="ts">
import type { Post, PostPayload } from '~/types/api'

const route = useRoute()
const router = useRouter()
const { list, create } = usePosts()
const { isLoggedIn } = useAuth()
const { tags, load: loadTax } = useTaxonomy()

const page = ref(Number(route.query.page) || 1)
const limit = ref(10)
const userId = computed(() =>
  route.query.user_id ? Number(route.query.user_id) : undefined,
)
const tag = computed(() => (route.query.tag as string) || '')

const posts = ref<Post[]>([])
const total = ref(0)
const loading = ref(false)
const errorMsg = ref('')

const { totalPages, go } = usePagination(page, limit, total)

async function fetchPosts() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await list({
      page: page.value,
      limit: limit.value,
      user_id: userId.value,
      tag: tag.value || undefined,
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
  router.push({ query: { ...route.query, page: String(page.value) } })
}

// function setCategory(slug: string) {
//   router.push({
//     query: { ...route.query, category: slug || undefined, page: '1' },
//   })
// }

function setTag(slug: string) {
  router.push({
    query: { ...route.query, tag: tag.value === slug ? undefined : slug, page: '1' },
  })
}

function clearUserFilter() {
  const q = { ...route.query }
  delete q.user_id
  q.page = '1'
  router.push({ query: q })
}

onMounted(() => loadTax())

// 新建文章
const showEditor = ref(false)
const saveError = ref('')

watch(
  () => route.query,
  () => {
    page.value = Number(route.query.page) || 1
    fetchPosts()
  },
  { immediate: true },
)

async function onSave(payload: PostPayload) {
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
        class="px-4 py-2 bg-primary text-white rounded hover:opacity-90"
        @click="showEditor = !showEditor"
      >
        {{ showEditor ? '收起' : '写文章' }}
      </button>
    </div>

    <!-- 标签筛选 -->
    <div v-if="tags.length" class="flex gap-2 flex-wrap">
      <button
        v-for="t in tags"
        :key="t.id"
        class="px-2 py-0.5 rounded text-xs border border-border"
        :class="tag === t.slug ? 'bg-primary/10 text-primary border-primary/40' : 'text-muted'"
        @click="setTag(t.slug)"
      ># {{ t.name }}</button>
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

    <div v-else class="flex flex-col gap-4">
      <ContentCard
        v-for="p in posts"
        :key="p.id"
        :item="{ kind: 'post', post: p }"
      />
    </div>

    <Pagination
      v-if="total > 0"
      :page="page"
      :total-pages="totalPages"
      @change="changePage"
    />
  </div>
</template>