<script setup lang="ts">
import type { Post, Series } from '~/types/api'

const route = useRoute()
const api = useApi()

const series = ref<Series | null>(null)
const intro = ref<Post | null>(null)
const posts = ref<Post[]>([])
const loading = ref(true)
const errorMsg = ref('')
const { user, isAdmin } = useAuth()
const canEdit = computed(() =>
  !!user.value && !!series.value &&
  (user.value.id === series.value.user_id || isAdmin.value)
)

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
</script>

<template>
  <div class="space-y-8">
    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>

    <template v-else-if="series">
      <!-- 系列头部 -->
      <header class="space-y-2">
        <h1 class="text-3xl font-bold">{{ series.title }}</h1>
        <p v-if="series.description" class="text-muted">{{ series.description }}</p>
        <p class="text-sm text-faint">
          {{ posts.length }} 篇 ·
          <NuxtLink :to="`/user/${series.user_id}`" class="text-primary">
            {{ series.author?.username }}
          </NuxtLink>
        </p>
      </header>

      <section v-if="canEdit">
        <h3 class="text-sm font-medium text-muted mb-2">管理封面</h3>
        <CoverUploader :series-id="series.id" :current="series.cover" @updated="onCoverUpdated" @removed="onCoverUpdated" />
      </section>

      <!-- 介绍文（系列描述本身就是一篇文章） -->
      <section v-if="intro" class="bg-surface border border-border rounded-lg p-6">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xl font-semibold">{{ intro.title }}</h2>
          <NuxtLink :to="`/posts/${intro.id}`" class="text-sm text-primary hover:underline">
            单独打开 →
          </NuxtLink>
        </div>
        <article class="prose prose-slate max-w-none">
          <MDC :value="intro.content" />
        </article>
      </section>

      <!-- 开始阅读 -->
      <NuxtLink
        v-if="posts[0]"
        :to="`/posts/${posts[0].id}`"
        class="inline-block px-4 py-2 bg-primary text-white rounded hover:opacity-90"
      >
        开始阅读 →
      </NuxtLink>

      <!-- 文章目录 -->
      <ol v-if="posts.length" class="space-y-2">
        <li v-for="(p, i) in posts" :key="p.id">
          <NuxtLink
            :to="`/posts/${p.id}`"
            class="flex items-center gap-3 p-3 rounded border border-border bg-surface hover:bg-surface-2 transition"
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
    </template>
  </div>
</template>