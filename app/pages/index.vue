<script setup lang="ts">
import type { PageOut, Post, Series, User } from '~/types/api'

const api = useApi()
const { list } = usePosts()
const { isLoggedIn } = useAuth()
const mediaUrl = useMediaUrl()

const featured = ref<Post[]>([])
const latest = ref<Post[]>([])
const seriesList = ref<Series[]>([])
const loading = ref(true)

// 如果后端有"站点 owner"概念，这里可以硬编码或从 /api/user/me 拿
// 假后端里 alice 是种子 admin，先演示用 id=1
const owner = ref<User | null>(null)

onMounted(async () => {
  try {
    const [featuredRes, latestRes, seriesRes, ownerRes] = await Promise.all([
      list({ page: 1, limit: 3, featured: true }),
      list({ page: 1, limit: 5, standalone: true }),
      api.get<PageOut<Series>>('/api/series', { page: 1, limit: 3 }, { silent: true }),
      api.get<User>('/api/user/1', undefined, { silent: true }),
    ])
    featured.value = featuredRes.data
    latest.value = latestRes.data
    seriesList.value = seriesRes.data.slice(0, 3)
    owner.value = ownerRes
  } catch {} finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-16">
    <!-- Hero -->
    <section class="text-center py-10 md:py-16">
      <div class="flex justify-center mb-6">
        <img
          v-if="owner?.avatar"
          :src="mediaUrl(owner.avatar)"
          class="w-24 h-24 rounded-full object-cover border-2 border-border"
          alt=""
        />
        <div
          v-else
          class="w-24 h-24 rounded-full bg-surface-2 flex items-center justify-center text-3xl font-bold text-faint border-2 border-border"
        >
          {{ owner?.username?.[0]?.toUpperCase() || 'A' }}
        </div>
      </div>

      <h1 class="text-4xl md:text-5xl font-bold mb-3">
        {{ owner?.username || 'Portfolio' }}
      </h1>
      <p class="text-lg text-muted max-w-xl mx-auto mb-2">
        <!-- 写代码的人，偶尔写字。这里记录我的项目、文章与思考。 -->
        foo
      </p>
      <p class="text-sm text-faint mb-8">
        <!-- 前端 · Nuxt · 开源 · 咖啡 -->
        foobar
      </p>

      <div class="flex gap-3 justify-center flex-wrap">
        <NuxtLink
          to="/posts"
          class="px-6 py-2.5 bg-primary text-white rounded-lg hover:opacity-90 transition"
        >
          读文章 →
        </NuxtLink>
        <NuxtLink
          v-if="isLoggedIn"
          to="/posts"
          class="px-6 py-2.5 border border-border rounded-lg hover:bg-surface-2 transition"
        >
          写文章
        </NuxtLink>
        <a
          href="https://github.com/pot0w0"
          target="_blank"
          rel="noopener"
          class="px-6 py-2.5 border border-border rounded-lg hover:bg-surface-2 transition"
        >
          GitHub
        </a>
      </div>
    </section>

    <!-- About 摘要 -->
    <section class="max-w-2xl mx-auto text-center space-y-3">
      <h2 class="text-sm font-medium text-faint uppercase tracking-wider">about</h2>
      <p class="text-muted leading-relaxed">
        <!-- 你好，我是 {{ owner?.username || '某个开发者' }}。平时写前端、折腾 Nuxt，
        偶尔写点随笔。这里是我的数字花园——文章、系列、项目都在这。 -->
        DOMO, {{ owner?.username || '某个开发者' }} desu
      </p>
      <NuxtLink to="/about" class="text-sm text-primary hover:underline">
        了解更多 →
      </NuxtLink>
    </section>

    <!-- 精选 -->
    <section v-if="featured.length" class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-semibold">精选</h2>
        <NuxtLink to="/posts?view=all" class="text-sm text-primary hover:underline">
          全部文章 →
        </NuxtLink>
      </div>
      <div class="grid gap-4 md:grid-cols-2">
        <ContentCard v-for="p in featured" :key="p.id" :item="{ kind: 'post', post: p }" />
      </div>
    </section>

    <!-- 系列 -->
    <section v-if="seriesList.length" class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-semibold">系列</h2>
        <NuxtLink to="/posts" class="text-sm text-primary hover:underline">
          全部系列 →
        </NuxtLink>
      </div>
      <div class="grid gap-4 md:grid-cols-3">
        <ContentCard
          v-for="s in seriesList"
          :key="s.id"
          :item="{ kind: 'series', series: s }"
        />
      </div>
    </section>

    <!-- 最新 -->
    <section v-if="latest.length" class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-2xl font-semibold">最新</h2>
        <NuxtLink to="/posts?view=standalone" class="text-sm text-primary hover:underline">
          查看全部 →
        </NuxtLink>
      </div>
      <div class="flex flex-col gap-4">
        <ContentCard v-for="p in latest" :key="p.id" :item="{ kind: 'post', post: p }" />
      </div>
    </section>

    <!-- 联系 -->
    <section class="text-center space-y-3 py-8 border-t border-border">
      <h2 class="text-sm font-medium text-faint uppercase tracking-wider">联系</h2>
      <div class="flex justify-center gap-4 text-sm">
        <a href="mailto:you@example.com" class="text-primary hover:underline">邮箱</a>
        <a href="https://github.com/pot0w0" target="_blank" rel="noopener" class="text-primary hover:underline">GitHub</a>
        <a href="/rss.xml" class="text-primary hover:underline">RSS</a>
      </div>
    </section>
  </div>
</template>