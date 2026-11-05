<script setup lang="ts">
import type { Post, Series } from '~/types/api'

const route = useRoute()
const api = useApi()

const series = ref<Series | null>(null)
const posts = ref<Post[]>([])
const loading = ref(true)
const errorMsg = ref('')

onMounted(async () => {
  try {
    const res = await api.get<{ series: Series; posts: Post[] }>(
      `/api/series/${route.params.slug}`,
    )
    series.value = res.series
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
        <p class="text-muted">{{ series.description }}</p>
        <p class="text-sm text-faint">
          {{ series.post_count }} 篇 ·
          <NuxtLink :to="`/user/${series.user_id}`" class="text-primary">
            {{ series.author?.username }}
          </NuxtLink>
        </p>
      </header>

      <!-- 开始阅读 -->
      <NuxtLink
        v-if="posts.length"
        :to="`/posts/${posts[0]!.id}`"
        class="inline-block px-4 py-2 bg-primary text-white rounded"
        >
        开始阅读 →
      </NuxtLink>

      <!-- 文章目录：这就是"指向 post 的东西" -->
      <ol class="space-y-2">
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
    </template>
  </div>
</template>