<script setup lang="ts">
import type { Post } from '~/types/api'

const { list } = usePosts()
const { isLoggedIn } = useAuth()

const latest = ref<Post[]>([])
const featured = ref<Post[]>([])

onMounted(async () => {
  try {
    const [f, l] = await Promise.all([
      list({ page: 1, limit: 2, featured: true }),
      list({ page: 1, limit: 3, standalone: true }),
    ])
    featured.value = f.data
    latest.value = l.data
  } catch {
    featured.value = []
    latest.value = []
  }
})
</script>

<template>
  <div class="space-y-12">
    <section class="text-center py-16 relative overflow-hidden rounded-xl" style="background-image: url('/dontknow.jpg'); background-size: cover; background-position: center;">
      <div class="absolute inset-0 bg-black/40"></div>
      <div class="relative z-10 text-white">
        <h1 class="text-4xl font-bold mb-4">欢迎来到我的作品集</h1>
        <p class="text-white/90 mb-8 max-w-xl mx-auto">这里记录我的文章、项目与思考。</p>
        <div class="flex gap-3 justify-center">
          <NuxtLink to="/posts" class="px-5 py-2 bg-primary text-white rounded hover:opacity-90">浏览博客</NuxtLink>
          <NuxtLink v-if="isLoggedIn" to="/posts" class="px-5 py-2 border border-white rounded hover:bg-white/20">写文章</NuxtLink>
        </div>
      </div>
    </section>

    <section v-if="featured.length" class="space-y-4">
      <h2 class="text-2xl font-semibold">精选</h2>
      <div class="grid gap-4 md:grid-cols-2">
        <PostCard v-for="p in featured" :key="p.id" :post="p" />
      </div>
    </section>

    <section v-if="latest.length">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-semibold">最新散篇</h2>
        <NuxtLink to="/posts" class="text-sm text-primary hover:underline">查看全部 →</NuxtLink>
      </div>
      <div class="grid gap-4 md:grid-cols-3">
        <PostCard v-for="p in latest" :key="p.id" :post="p" />
      </div>
    </section>
  </div>
</template>