<script setup lang="ts">
import type { Comment, Post } from '~/types/api'

const props = defineProps<{ post: Post }>()
const { list, create, remove } = useComments()
const { user, isLoggedIn, isAdmin } = useAuth()

const draft = ref('')
const submitting = ref(false)

// 用 useList 统一管理分页/加载/错误
const { query, data: comments, total, loading, error: loadError, load, update } = useList(
  (q) => list(props.post.id, q),
  { page: 1, limit: 10, sort: 'created_at', order: 'asc' },
)

const submitError = ref('')

onMounted(() => load())

async function submit() {
  if (!draft.value.trim()) return
  submitting.value = true
  submitError.value = ''
  try {
    await create(props.post.id, draft.value.trim())
    draft.value = ''
    // 分页下本地 push 可能错位（新评论在最后一页），直接重新拉
    // 如果评论少（total <= limit），也可以拉第 1 页
    await load()
  } catch (e: any) {
    submitError.value = e?.message ?? '发表失败'
  } finally {
    submitting.value = false
  }
}

function canDelete(c: Comment) {
  if (!user.value) return false
  return c.user_id === user.value.id || props.post.user_id === user.value.id || isAdmin.value
}

async function onDelete(c: Comment) {
  if (!confirm('删除这条评论？')) return
  try {
    await remove(c.id)
    await load()
  } catch {}
}
</script>

<template>
  <section class="mt-10">
    <h2 class="text-xl font-semibold mb-4">
      评论 <span class="text-faint text-base">({{ total }})</span>
    </h2>

    <!-- 发表 -->
    <form v-if="isLoggedIn" class="mb-6" @submit.prevent="submit">
      <textarea
        v-model="draft"
        rows="3"
        placeholder="说点什么…"
        class="w-full border border-border rounded px-3 py-2 text-sm bg-surface"
      />
      <div class="flex justify-end items-center mt-2 gap-3">
        <p v-if="submitError" class="text-sm text-danger">{{ submitError }}</p>
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

    <!-- 状态 -->
    <p v-if="loadError" class="text-sm text-danger mb-3">{{ loadError }}</p>
    <p v-if="loading" class="text-sm text-faint">加载中…</p>
    <p v-else-if="!comments.length" class="text-sm text-faint">还没有评论，来抢沙发</p>

    <!-- 列表 -->
    <ul v-else class="space-y-4">
      <li v-for="c in comments" :key="c.id" class="bg-surface border border-border rounded-lg p-4">
        <div class="flex items-center justify-between mb-1">
          <UserBadge :user="c.author" :user-id="c.user_id" />
          <div class="flex items-center gap-3 text-xs text-faint">
            <time v-if="c.created_at">{{ new Date(c.created_at).toLocaleString() }}</time>
            <button v-if="canDelete(c)" class="text-danger hover:underline" @click="onDelete(c)">删除</button>
          </div>
        </div>
        <p class="text-sm text-muted whitespace-pre-wrap">{{ c.content }}</p>
      </li>
    </ul>

    <!-- 分页：一页装得下就不显示 -->
    <Pagination
      v-if="total > query.limit!"
      :page="query.page!"
      :total="total"
      :limit="query.limit!"
      @change="(p) => update({ page: p })"
    />
  </section>
</template>