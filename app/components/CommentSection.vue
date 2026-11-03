<script setup lang="ts">
import type { Comment, Post } from '~/types/api'

const props = defineProps<{ post: Post }>()
const { list, create, remove } = useComments()
const { user, isLoggedIn, isAdmin } = useAuth()

const comments = ref<Comment[]>([])
const loading = ref(false)
const errorMsg = ref('')
const draft = ref('')
const submitting = ref(false)

async function fetchComments() {
  loading.value = true
  errorMsg.value = ''
  try {
    comments.value = await list(props.post.id)
  } catch (e: any) {
    errorMsg.value = e?.message ?? '加载评论失败'
  } finally {
    loading.value = false
  }
}

onMounted(fetchComments)

async function submit() {
  if (!draft.value.trim()) return
  submitting.value = true
  errorMsg.value = ''
  try {
    const c = await create(props.post.id, draft.value.trim())
    comments.value.push(c)
    draft.value = ''
  } catch (e: any) {
    errorMsg.value = e?.message ?? '发表失败'
  } finally {
    submitting.value = false
  }
}

function canDelete(c: Comment) {
  if (!user.value) return false
  return (
    c.user_id === user.value.id ||
    props.post.user_id === user.value.id ||
    isAdmin.value
  )
}

async function onDelete(c: Comment) {
  if (!confirm('删除这条评论？')) return
  try {
    await remove(c.id)
    comments.value = comments.value.filter((x) => x.id !== c.id)
  } catch (e: any) {
    errorMsg.value = e?.message ?? '删除失败'
  }
}
</script>

<template>
  <section class="mt-10">
    <h2 class="text-xl font-semibold mb-4">
      评论 <span class="text-faint text-base">({{ comments.length }})</span>
    </h2>

    <form v-if="isLoggedIn" class="mb-6" @submit.prevent="submit">
      <textarea
        v-model="draft"
        rows="3"
        placeholder="说点什么…"
        class="w-full border-border rounded px-3 py-2 text-sm"
      />
      <div class="flex justify-end mt-2">
        <button
          class="px-4 py-1.5 bg-primary text-white rounded text-sm disabled:opacity-50"
          :disabled="submitting || !draft.trim()"
        >
          {{ submitting ? '发表中…' : '发表评论' }}
        </button>
      </div>
    </form>
    <p v-else class="text-sm text-faint mb-6">
      <NuxtLink to="/login" class="text-primary">登录</NuxtLink> 后参与评论
    </p>

    <p v-if="errorMsg" class="text-sm text-danger mb-3">{{ errorMsg }}</p>
    <p v-if="loading" class="text-sm text-faint">加载中…</p>
    <p v-else-if="!comments.length" class="text-sm text-faint">
      还没有评论，来抢沙发
    </p>

    <ul v-else class="space-y-4">
      <li
        v-for="c in comments"
        :key="c.id"
        class="bg-surface border-border rounded-lg p-4"
      >
        <div class="flex items-center justify-between mb-1">
          <UserBadge :user="c.author" :user-id="c.user_id" />
          <div class="flex items-center gap-3 text-xs text-faint">
            <time v-if="c.created_at">
              {{ new Date(c.created_at).toLocaleString() }}
            </time>
            <button
              v-if="canDelete(c)"
              class="text-danger hover:underline"
              @click="onDelete(c)"
            >
              删除
            </button>
          </div>
        </div>
        <p class="text-sm text-text whitespace-pre-wrap">{{ c.content }}</p>
      </li>
    </ul>
  </section>
</template>