<script setup lang="ts">
import type { Post } from '~/types/api'

const route = useRoute()
const router = useRouter()
const { get, update, remove } = usePosts()
const { user, isAdmin } = useAuth()

const post = ref<Post | null>(null)
const loading = ref(true)
const errorMsg = ref('')

const isAuthor = computed(
  () => !!user.value && !!post.value && user.value.id === post.value.user_id,
)
const isAuthorOrAdmin = computed(() => isAuthor.value || isAdmin.value)

async function fetchPost() {
  loading.value = true
  errorMsg.value = ''
  try {
    post.value = await get(route.params.id as string)
  } catch (e: any) {
    errorMsg.value = e?.status === 404 ? '文章不存在' : e?.message ?? '加载失败'
    post.value = null
  } finally {
    loading.value = false
  }
}

onMounted(fetchPost)

const editing = ref(false)
const actionError = ref('')

async function onSave(payload: { title: string; content: string }) {
  if (!post.value) return
  actionError.value = ''
  try {
    post.value = await update(post.value.id, payload)
    editing.value = false
  } catch (e: any) {
    actionError.value = e?.message ?? '保存失败'
  }
}

async function onDelete() {
  if (!post.value) return
  if (!confirm('确定删除这篇文章？')) return
  actionError.value = ''
  try {
    await remove(post.value.id)
    await router.push('/posts')
  } catch (e: any) {
    actionError.value = e?.message ?? '删除失败'
  }
}
</script>

<template>
  <div class="space-y-6">
    <p v-if="loading" class="text-slate-500">加载中…</p>
    <p v-else-if="errorMsg" class="text-red-600">{{ errorMsg }}</p>

    <template v-else-if="post">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-3xl font-bold mb-2">{{ post.title }}</h1>
          <div class="flex items-center gap-4 text-sm text-slate-500">
            <UserBadge :user="post.author" :user-id="post.user_id" />
            <time v-if="post.created_at">
              {{ new Date(post.created_at).toLocaleString() }}
            </time>
          </div>
        </div>
        <div v-if="isAuthorOrAdmin" class="flex gap-2 shrink-0">
          <button
            class="px-3 py-1 border rounded hover:bg-slate-100"
            @click="editing = !editing"
          >
            {{ editing ? '取消' : '编辑' }}
          </button>
          <button
            class="px-3 py-1 border border-red-300 text-red-600 rounded hover:bg-red-50"
            @click="onDelete"
          >
            删除
          </button>
        </div>
      </div>

      <p v-if="actionError" class="text-sm text-red-600">{{ actionError }}</p>

      <PostEditor
        v-if="editing"
        :post="post"
        @save="onSave"
        @cancel="editing = false"
      />

      <article v-else class="prose prose-slate max-w-none bg-white border rounded-lg p-6">
        <MDC :value="post.content" />
      </article>

      <!-- 新增 -->
      <CommentSection :post="post" />
    </template>
  </div>
</template>