<script setup lang="ts">
import type { Post, PostPayload, Series } from '~/types/api'

const route = useRoute()
const api = useApi()

const series = ref<Series | null>(null)
const intro = ref<Post | null>(null)
const posts = ref<Post[]>([])
const loading = ref(true)
const errorMsg = ref('')
const { user, isAdmin } = useAuth()
const defaultIntroText = '不想写介绍文了，好懒喵~'
const showEditor = ref(false)
const saving = ref(false)
const editorError = ref('')

const canEdit = computed(() =>
  !!user.value && !!series.value &&
  (user.value.id === series.value.user_id || isAdmin.value)
)

const mediaUrl = useMediaUrl()

function onCoverUpdated(s: Series) {
  series.value = s
}

onMounted(async () => {
  try {
    const res = await api.get<{ series: Series; intro: Post | null; posts: Post[] }>(
      `/api/series/${route.params.slug}`,
      undefined,
      { silent: true },
    )
    series.value = res.series
    intro.value = res.intro
    posts.value = res.posts
  } catch (e: any) {
    errorMsg.value = e?.status === 404 ? '系列不存在' : e?.message ?? '加载失败'
  } finally {
    loading.value = false
  }
})

const nextOrder = computed(() => {
  const maxOrder = posts.value.reduce((m, p) => Math.max(m, p.series_order ?? 0), 0)
  return maxOrder + 1
})

// function onSeriesSave(payload: PostPayload) {
//   editorError.value = ''
//   // 强制绑到当前系列
//   saveSeriesPost({
//     ...payload,
//     series_id: series.value!.id,
//     series_order: payload.series_order ?? nextOrder.value,
//   })
// }

function onSeriesSaved(p: Post) {
  posts.value.push(p)
  posts.value.sort((a, b) => (a.series_order ?? 0) - (b.series_order ?? 0))
  showEditor.value = false
}

async function saveSeriesPost(payload: PostPayload) {
  saving.value = true
  try {
    const p = await api.post<Post>('/api/posts', payload)
    posts.value.push(p)
    posts.value.sort((a, b) => (a.series_order ?? 0) - (b.series_order ?? 0))
    showEditor.value = false
  } catch (e: any) {
    editorError.value = e?.message ?? '保存失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-10">
    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>

    <template v-else-if="series">
      <section class="grid md:grid-cols-[280px_1fr] gap-6 items-start">
        <!-- 左：封面（不变） -->
        <div class="relative">
          <div class="aspect-[3/4] rounded-xl overflow-hidden border border-border bg-surface-2">
            <img
              v-if="series.cover"
              :src="mediaUrl(series.cover)"
              :alt="series.title"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center text-faint text-sm">
              暂无封面
            </div>
          </div>

          <p v-if="canEdit" class="text-xs text-faint mt-2">
            系列封面来自介绍文。想换封面，请
            <NuxtLink :to="`/posts/${series.intro_post_id}`" class="text-primary hover:underline">编辑介绍文</NuxtLink>。
          </p>
        </div>

        <!-- 右：标题 + 介绍文（不再显示 series.description） -->
        <div class="space-y-4">
          <header class="space-y-2">
            <h1 class="text-3xl font-bold leading-tight">{{ series.title }}</h1>
            <p class="text-sm text-faint">
              {{ posts.length }} 篇 ·
              <NuxtLink :to="`/user/${series.user_id}`" class="text-primary hover:underline">
                {{ series.author?.username }}
              </NuxtLink>
            </p>
          </header>

          <!-- 介绍文：系列的"描述"就是这篇文章 -->
          <div v-if="intro" class="relative">
            <div class="max-h-72 overflow-hidden prose prose-slate max-w-none">
              <MDC v-if="intro.content?.trim()" :value="intro.content" />
              <p v-else class="text-muted">
                {{ defaultIntroText }}
              </p>
            </div>
            <!-- 渐隐 + 阅读完整介绍 只在有内容时显示 -->
            <template v-if="intro.content?.trim()">
              <div class="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-surface to-transparent" />
              <div class="mt-2">
                <NuxtLink :to="`/posts/${intro.id}`" class="text-sm text-primary hover:underline">阅读完整介绍 →</NuxtLink>
              </div>
            </template>
          </div>

          <NuxtLink
            v-if="posts[0]"
            :to="`/posts/${posts[0].id}`"
            class="inline-block px-5 py-2.5 bg-primary text-white rounded-lg hover:opacity-90 transition"
          >
            开始阅读 →
          </NuxtLink>
        </div>
      </section>

      <!-- 文章目录（不变） -->
      <section class="space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold">文章目录</h2>
          <button
            v-if="canEdit"
            class="px-3 py-1.5 border border-border rounded text-sm hover:bg-surface-2"
            @click="showEditor = !showEditor"
          >
            {{ showEditor ? '收起' : '新建系列文章' }}
          </button>
        </div>

        <!-- 编辑器：预置系列，序号自动 -->
        <div v-if="showEditor" class="space-y-2">
          <p class="text-sm text-faint">
            新文章将加入《{{ series.title }}》，序号 {{ nextOrder }}
          </p>
          <PostEditor
            v-if="showEditor"
            :post="null"
            :lock-series="true"
            :preset-series-id="series.id"
            :preset-series-order="nextOrder"
            :preset-series-title="series.title"
            @saved="onSeriesSaved"
            @cancel="showEditor = false"
          />
          <p v-if="editorError" class="text-sm text-danger">{{ editorError }}</p>
        </div>
        <ol v-if="posts.length" class="space-y-2">
          <li v-for="(p, i) in posts" :key="p.id">
            <NuxtLink
              :to="`/posts/${p.id}`"
              class="flex items-center gap-3 p-3 rounded-lg border border-border
                     bg-surface hover:bg-surface-2 transition"
            >
              <span class="text-faint text-sm w-6 text-right">{{ i + 1 }}</span>
              <span class="flex-1">{{ p.title }}</span>
              <span v-if="p.created_at" class="text-xs text-faint">
                {{ new Date(p.created_at).toLocaleDateString() }}
              </span>
            </NuxtLink>
          </li>
        </ol>
        <p v-else class="text-faint">系列还没有正文</p>
      </section>
    </template>
  </div>
</template>