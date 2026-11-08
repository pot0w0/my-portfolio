<script setup lang="ts">
import type { FriendLink } from '~/types/api'

const api = useApi()
const { query, data: friends, total, loading, load, update } = useList(
  (q) => api.get<PageOut<FriendLink>>('/api/friends', q),
  { limit: 100 },
)
onMounted(() => load())
</script>

<template>
  <div class="space-y-8">
    <header class="text-center space-y-2">
      <h1 class="text-3xl font-bold">友链</h1>
      <p class="text-muted">一些我喜欢的人和他们的站点。</p>
    </header>

    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="!friends.length" class="text-faint">还没有友链</p>

    <div v-else class="grid gap-4 md:grid-cols-2">
      <FriendCard v-for="f in friends" :key="f.id" :friend="f" />
    </div>

    <p class="text-center text-sm text-faint">
      想交换友链？
      <a href="mailto:you@example.com" class="text-primary hover:underline">邮件联系</a>
    </p>
  </div>
</template>