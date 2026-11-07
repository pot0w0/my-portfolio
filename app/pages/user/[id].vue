<script setup lang="ts">
import type { Post, User } from '~/types/api'

const route = useRoute()
const api = useApi()
const { list } = usePosts()
const mediaUrl = useMediaUrl()

const userId = computed(() => Number(route.params.id))
const profile = ref<User | null>(null)
const posts = ref<Post[]>([])
const loading = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  loading.value = true
  errorMsg.value = ''
  try {
    // 若后端提供公开用户接口则用之；否则从文章列表兜底
    try {
      profile.value = await api.get<User>(`/api/user/${userId.value}`, { silent: true } as any)
    } catch {
      profile.value = null
    }
    const res = await list({ page: 1, limit: 50, user_id: userId.value })
    posts.value = res.data
    if (!profile.value && res.data[0]?.author) profile.value = res.data[0].author
  } catch (e: any) {
    errorMsg.value = e?.message ?? '加载失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-8">
    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>

    <template v-else>
      <section class="bg-surface border border-border rounded-lg p-6 flex items-center gap-4">
        <img
          v-if="profile?.avatar"
          :src="mediaUrl(profile.avatar)"
          class="w-14 h-14 rounded-full object-cover border border-border"
          alt=""
        />
        <div
          v-else
          class="w-14 h-14 rounded-full bg-surface-2 flex items-center justify-center text-xl font-bold text-faint"
        >
          {{ profile?.username?.[0]?.toUpperCase() || '?' }}
        </div>
        <div>
          <h1 class="text-xl font-bold">
            {{ profile?.username || `用户 #${userId}` }}
          </h1>
          <p v-if="profile?.created_at" class="text-sm text-faint">
            加入于 {{ new Date(profile.created_at).toLocaleDateString() }}
          </p>
        </div>
      </section>

      <section>
        <h2 class="text-xl font-semibold mb-4">TA 的文章</h2>
        <p v-if="!posts.length" class="text-faint">暂无文章</p>
        <div v-else class="flex flex-col gap-4">
          <ContentCard
            v-for="p in posts"
            :key="p.id"
            :item="{ kind: 'post', post: p }"
          />
        </div>
      </section>
    </template>
  </div>
</template>