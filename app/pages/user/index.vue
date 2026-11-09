<script setup lang="ts">
import type { Post, User } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const api = useApi()
const { user, logout } = useAuth()
const { list } = usePosts()
const router = useRouter()
const avatarUrl = useAvatarUrl()

const profile = ref<User | null>(user.value)
const posts = ref<Post[]>([])
const loading = ref(false)
const showEdit = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    profile.value = await api.get<User>('/api/user/me')
    const res = await list({ page: 1, limit: 50, user_id: profile.value.id })
    posts.value = res.data
  } catch {} finally { loading.value = false }
})

async function onLogout() {
  await logout()
  await router.push('/')
}

function onProfileUpdated(u: User) {
  profile.value = u
}
</script>

<template>
  <div class="space-y-8">
    <section v-if="profile" class="bg-surface border border-border rounded-lg p-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <img
            :src="avatarUrl(profile.avatar)"
            class="w-14 h-14 rounded-full object-cover border border-border"
            alt=""
          />
          <div>
            <h1 class="text-xl font-bold flex items-center gap-2">
              {{ profile.username }}
              <span v-if="profile.role === 'admin'" class="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded dark:bg-amber-900/40 dark:text-amber-300">管理员</span>
            </h1>
            <p v-if="profile.email" class="text-sm text-faint">{{ profile.email }}</p>
          </div>
        </div>
        <div class="flex gap-2">
          <button class="px-4 py-2 border border-border rounded hover:bg-surface-2 text-sm" @click="showEdit = true">
            编辑资料
          </button>
          <button class="px-4 py-2 border border-border rounded hover:bg-surface-2 text-sm" @click="onLogout">
            登出
          </button>
        </div>
      </div>
    </section>

    <ProfileEditDialog :open="showEdit" @close="showEdit = false" @updated="onProfileUpdated" />

    <section>
      <h2 class="text-xl font-semibold mb-4">我的文章</h2>
      <p v-if="loading" class="text-faint">加载中…</p>
      <p v-else-if="!posts.length" class="text-faint">还没有文章</p>
      <div v-else class="flex flex-col gap-4">
        <ContentCard
          v-for="p in posts"
          :key="p.id"
          :item="{ kind: 'post', post: p }"
        />
      </div>
    </section>
  </div>
</template>