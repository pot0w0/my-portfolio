<script setup lang="ts">
import type { Post } from '~/types/api'

const route = useRoute()
const router = useRouter()
const api = useApi()
const { get, remove, like, unlike } = usePosts()
const { user, isAdmin, isLoggedIn } = useAuth()
const mediaUrl = useMediaUrl()

const post = ref<Post | null>(null)
const loading = ref(true)
const errorMsg = ref('')
const editing = ref(false)
const actionError = ref('')

interface AdjacentResponse {
  prev: Post | null
  next: Post | null
  series: { id: number; slug: string; title: string; index: number; total: number } | null
}

const adjacent = ref<AdjacentResponse | null>(null)

async function fetchAdjacent() {
  try {
    adjacent.value = await api.get<AdjacentResponse>(
      `/api/posts/${route.params.id}/adjacent`,
      undefined,
      { silent: true }, // useApi 会自动带 Authorization header
    )
  } catch { adjacent.value = null }
}

onMounted(() => { fetchPost(); fetchAdjacent() })
const isAuthor = computed(
  () => !!user.value && !!post.value && user.value.id === post.value.user_id,
)
const isAuthorOrAdmin = computed(() => isAuthor.value || isAdmin.value)

async function fetchPost() {
  loading.value = true
  errorMsg.value = ''
  try {
    post.value = await get(route.params.id as string, { silent: true })
  } catch (e: any) {
    // 404 可能是"真不存在"，也可能是"draft 无权看"——文案必须统一
    errorMsg.value = e?.status === 404
      ? '文章不存在或已被删除'
      : e?.message ?? '加载失败'
    post.value = null
  } finally {
    loading.value = false
  }
}

function onSaved(updated: Post) {
  post.value = updated
  editing.value = false
}

const liking = ref(false)
async function toggleLike() {
  if (!post.value) return
  if (!isLoggedIn.value) {
    await navigateTo('/login')
    return
  }
  liking.value = true
  try {
    const stats = post.value.liked_by_me
      ? await unlike(post.value.id)
      : await like(post.value.id)
    post.value.like_count = stats.like_count
    post.value.liked_by_me = stats.liked_by_me
  } catch {} finally {
    liking.value = false
  }
}

async function onDelete() {
  if (!post.value) return
  if (!confirm('确定删除这篇文章？')) return
  actionError.value = ''
  try {
    await remove(post.value.id)
    await router.push('/posts')
  } catch (e: any) {
    actionError.value = e?.status === 404
      ? '文章不存在或已被删除'
      : e?.message ?? '删除失败'
  }
}

// // 视差
// const coverEl = ref<HTMLElement | null>(null)
// const progress = useScrollProgress(coverEl, 420)
// const imgStyle = computed(() => {
//   const p = progress.value
//   return {
//     transform: `scale(${1.15 - p * 0.15}) translateY(${p * 40}px)`,
//     willChange: 'transform',
//   }
// })
</script>

<template>
  <div class="space-y-6">
    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>

    <template v-else-if="post">
      <!-- 封面：底部溶解到页面背景色，无文字 -->
      <div
        v-if="post.cover"
        ref="coverEl"
        class="relative w-screen left-1/2 -translate-x-1/2 h-[60vh] min-h-[360px] overflow-hidden -mt-20"
        style="
          -webkit-mask-image: linear-gradient(to bottom, black 50%, transparent 100%);
          mask-image: linear-gradient(to bottom, black 50%, transparent 100%);
        "
      >
        <img
          :src="mediaUrl(post.cover)"
          class="absolute inset-0 w-full h-full object-cover"
          alt=""
        />
        <!-- 用页面背景色做渐变终点，让图片淡出成页面底色（浅色主题=浅底，深色主题=深底） -->
        <div class="absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-bg via-bg/60 to-transparent" />
      </div>

      <!-- 标题区：无框，主题色，落在已淡出的背景上 -->
      <div
        class="max-w-4xl mx-auto px-4 md:px-0"
        :class="post.cover ? '-mt-24 relative z-10' : 'mt-6'"
      >
        <h1 class="text-3xl md:text-4xl font-bold text-fg leading-tight">
          {{ post.title }}
          <span
            v-if="post.status === 'draft'"
            class="inline-block align-middle ml-2 text-sm font-medium px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300"
          >草稿</span>
          <span
            v-else-if="post.status === 'archived'"
            class="inline-block align-middle ml-2 text-sm font-medium px-2 py-0.5 rounded bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
          >已归档</span>
        </h1>

        <div class="mt-3 flex items-center gap-4 text-sm text-muted flex-wrap">
          <UserBadge :user="post.author" :user-id="post.user_id" />
          <span v-if="post.series">
            属于系列
            <NuxtLink
              :to="`/series/${post.series.slug}`"
              class="text-primary hover:underline"
            >
              《{{ post.series.title }}》
            </NuxtLink>
            <span v-if="post.series_order" class="text-faint">第 {{ post.series_order }} 篇</span>
          </span>
          <time v-if="post.created_at" class="text-faint">
            {{ new Date(post.created_at).toLocaleString() }}
          </time>
          <button
            type="button"
            class="inline-flex items-center gap-1 disabled:opacity-50 transition"
            :class="post.liked_by_me ? 'text-danger' : 'text-faint hover:text-danger'"
            :disabled="liking"
            :aria-pressed="!!post.liked_by_me"
            @click="toggleLike"
          >
            <span>{{ post.liked_by_me ? '♥' : '♡' }}</span>
            <span v-if="post.like_count">{{ post.like_count }}</span>
            <span v-else>赞</span>
          </button>
        </div>
      </div>

      <!-- 编辑/删除：无封面时在标题右侧，有封面时浮在封面右上角 -->
      <div
        v-if="isAuthorOrAdmin"
        class="max-w-4xl mx-auto px-4 md:px-0 flex gap-2 justify-end"
        :class="post.cover ? '-mt-2' : 'mt-4'"
      >
        <button
          class="px-3 py-1 border border-border text-fg rounded hover:bg-muted/10"
          @click="editing = !editing"
        >
          {{ editing ? '取消' : '编辑' }}
        </button>
        <button
          class="px-3 py-1 border border-danger text-danger rounded hover:bg-danger/10"
          @click="onDelete"
        >
          删除
        </button>
      </div>

      <p v-if="actionError" class="text-sm text-danger">{{ actionError }}</p>

      <PostEditor v-if="editing" :post="post" @saved="onSaved" @cancel="editing = false" />

      <article
        v-else
        class="prose prose-slate max-w-none bg-surface border border-border rounded-lg p-6"
      >
        <MDC :value="post.content" />
      </article>

      <!-- 系列上下文 + 上一篇/下一篇 -->
      <section v-if="adjacent?.series" class="space-y-3">
        <div class="text-sm text-faint text-center">
          系列
          <NuxtLink :to="`/series/${adjacent.series.slug}`" class="text-primary hover:underline">
            《{{ adjacent.series.title }}》
          </NuxtLink>
          第 {{ adjacent.series.index }} / {{ adjacent.series.total }} 篇
        </div>
        <div class="flex justify-between gap-3">
          <NuxtLink
            v-if="adjacent.prev"
            :to="`/posts/${adjacent.prev.id}`"
            class="flex-1 p-3 rounded border border-border bg-surface hover:bg-surface-2 transition text-sm"
          >
            <span class="text-faint text-xs">← 上一篇</span>
            <p class="truncate">{{ adjacent.prev.title }}</p>
          </NuxtLink>
          <div v-else class="flex-1" />
          <NuxtLink
            v-if="adjacent.next"
            :to="`/posts/${adjacent.next.id}`"
            class="flex-1 p-3 rounded border border-border bg-surface hover:bg-surface-2 transition text-sm text-right"
          >
            <span class="text-faint text-xs">下一篇 →</span>
            <p class="truncate">{{ adjacent.next.title }}</p>
          </NuxtLink>
          <div v-else class="flex-1" />
        </div>
      </section>
      <CommentSection :post="post" />
    </template>
  </div>
</template>