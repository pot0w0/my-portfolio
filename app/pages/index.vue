<script setup lang="ts">
import type { Paginated, Post } from '~/types/api'

const { list } = usePosts()
const { isLoggedIn } = useAuth()

const latest = ref<Post[]>([])

onMounted(async () => {
  try {
    const res = await list({ page: 1, limit: 3 })
    latest.value = res.data
  } catch {
    latest.value = []
  }
})
</script>

<template>
  <div class="space-y-12">
    <section 
      class="text-center py-16 relative overflow-hidden"
      style="background-image: url('/bg-home.jpg'); background-size: cover; background-position: center;"
    >
      <!-- 暗色遮罩 -->
      <div class="absolute inset-0 bg-black/40"></div>
      <!-- 内容放到上层，加 relative z-10 -->
      <div class="relative z-10 text-white">
        <h1 class="text-4xl font-bold mb-4">欢迎来到我的作品集</h1>
        <p class="text-white/90 mb-8 max-w-xl mx-auto">
          这里记录我的文章、项目与思考。
        </p>
        <div class="flex gap-3 justify-center">
          <NuxtLink
            to="/posts"
            class="px-5 py-2 bg-primary text-white rounded hover:bg-blue-700"
          >
            浏览博客
          </NuxtLink>
          <NuxtLink
            v-if="isLoggedIn"
            to="/posts"
            class="px-5 py-2 border-border border-white rounded hover:bg-white/20"
          >
            写文章
          </NuxtLink>
        </div>
      </div>
    </section>


    <section v-if="latest.length">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-semibold">最新文章</h2>
        <NuxtLink to="/posts" class="text-sm text-primary hover:underline">
          查看全部 →
        </NuxtLink>
      </div>
      <div class="grid gap-4 md:grid-cols-3">
        <PostCard v-for="p in latest" :key="p.id" :post="p" />
      </div>
    </section>
  </div>
</template>