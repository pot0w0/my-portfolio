<script setup lang="ts">
import type { Post, User } from '~/types/api'

const route = useRoute()
const api = useApi()
const { list } = usePosts()
const avatarUrl = useAvatarUrl()

// 路径参数既支持数字 id，也支持用户名（评论里的 @username 直接链到这里）
const userRef = computed(() => String(route.params.id ?? ''))
const profile = ref<User | null>(null)
const posts = ref<Post[]>([])
const loading = ref(false)
const errorMsg = ref('')

async function loadProfile() {
  loading.value = true
  errorMsg.value = ''
  posts.value = []
  try {
    profile.value = await api.get<User>(
      `/api/user/${encodeURIComponent(userRef.value)}`,
      undefined,
      { silent: true },
    )
    const res = await list({ page: 1, limit: 50, user_id: profile.value.id })
    posts.value = res.data
  } catch (e: any) {
    profile.value = null
    errorMsg.value = e?.status === 404 ? '用户不存在' : (e?.message ?? '加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)
watch(userRef, loadProfile)
</script>

<template>
  <div class="space-y-8">
    <p v-if="loading" class="text-faint">加载中…</p>
    <p v-else-if="errorMsg" class="text-danger">{{ errorMsg }}</p>

    <template v-else>
      <section class="bg-surface border border-border rounded-lg p-6 flex items-center gap-4">
        <img
          :src="avatarUrl(profile?.avatar)"
          class="w-14 h-14 rounded-full object-cover border border-border"
          alt=""
        />
        <div>
          <h1 class="text-xl font-bold">
            {{ profile?.username || userRef }}
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