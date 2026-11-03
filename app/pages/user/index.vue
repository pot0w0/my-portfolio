<script setup lang="ts">
import type { Post, User } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const api = useApi()
const { user, logout } = useAuth()
const { list } = usePosts()
const router = useRouter()

const profile = ref<User | null>(user.value)
const posts = ref<Post[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    profile.value = await api.get<User>('/api/user/me')
    const res = await list({ page: 1, limit: 50, user_id: profile.value.id })
    posts.value = res.data
  } catch {
    // 忽略
  } finally {
    loading.value = false
  }
})

async function onLogout() {
  await logout()
  await router.push('/')
}
</script>

<template>
  <div class="space-y-8">
    <section v-if="profile" class="bg-white border rounded-lg p-6 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <img
          v-if="profile.avatar"
          :src="profile.avatar"
          class="w-14 h-14 rounded-full object-cover"
          alt=""
        />
        <div v-else class="w-14 h-14 rounded-full bg-slate-200 flex items-center justify-center text-xl font-bold">
          {{ profile.username?.[0]?.toUpperCase() }}
        </div>
        <div>
          <h1 class="text-xl font-bold">{{ profile.username }}</h1>
          <p v-if="profile.email" class="text-sm text-slate-500">{{ profile.email }}</p>
        </div>
      </div>
      <button class="px-4 py-2 border rounded hover:bg-slate-100" @click="onLogout">
        登出
      </button>
    </section>

    <section>
      <h2 class="text-xl font-semibold mb-4">我的文章</h2>
      <p v-if="loading" class="text-slate-500">加载中…</p>
      <p v-else-if="!posts.length" class="text-slate-500">还没有文章</p>
      <div v-else class="grid gap-4">
        <PostCard v-for="p in posts" :key="p.id" :post="p" />
      </div>
    </section>
  </div>
</template>