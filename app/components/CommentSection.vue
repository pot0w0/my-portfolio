<script setup lang="ts">
import type { Comment, Post } from '~/types/api'

const props = defineProps<{ post: Post }>()
const { list, create, remove } = useComments()
const { user, isLoggedIn, isAdmin } = useAuth()

const comments = ref<Comment[]>([])
const page = ref(1)
const limit = 10
const total = ref(0)          // 根评论数（分页依据）
const commentTotal = ref(0)   // 含回复的总数（展示用）
const loading = ref(false)
const loadError = ref('')

const draft = ref('')
const submitting = ref(false)
const submitError = ref('')

// 回复状态：指向被回复的那条评论（后端会把层级压平到根评论）
const replyTarget = ref<Comment | null>(null)
const replyDraft = ref('')
const replying = ref(false)
const replyError = ref('')

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const res = await list(props.post.id, {
      page: page.value,
      limit,
      sort: 'created_at',
      order: 'asc',
    })
    comments.value = res.data
    total.value = res.total
    commentTotal.value = res.comment_total
  } catch (e: any) {
    loadError.value = e?.message ?? '加载失败'
    comments.value = []
    total.value = 0
    commentTotal.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function submit() {
  if (!draft.value.trim()) return
  submitting.value = true
  submitError.value = ''
  try {
    await create(props.post.id, draft.value.trim())
    draft.value = ''
    // 按时间正序时新评论在最后一页，直接跳到那一页
    page.value = Math.max(1, Math.ceil((total.value + 1) / limit))
    await load()
  } catch (e: any) {
    submitError.value = e?.message ?? '发表失败'
  } finally {
    submitting.value = false
  }
}

function startReply(c: Comment) {
  if (!isLoggedIn.value) {
    navigateTo('/login')
    return
  }
  replyTarget.value = c
  replyDraft.value = ''
  replyError.value = ''
}

function cancelReply() {
  replyTarget.value = null
  replyDraft.value = ''
  replyError.value = ''
}

async function submitReply() {
  if (!replyTarget.value || !replyDraft.value.trim()) return
  replying.value = true
  replyError.value = ''
  try {
    await create(props.post.id, replyDraft.value.trim(), replyTarget.value.id)
    cancelReply()
    await load()
  } catch (e: any) {
    replyError.value = e?.message ?? '回复失败'
  } finally {
    replying.value = false
  }
}

function gotoPage(p: number) {
  page.value = p
  load()
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
      评论 <span class="text-faint text-base">({{ commentTotal }})</span>
    </h2>

    <!-- 发表顶层评论 -->
    <form v-if="isLoggedIn" class="mb-6" @submit.prevent="submit">
      <textarea
        v-model="draft"
        rows="3"
        placeholder="说点什么…支持 @用户名 提及"
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

    <!-- 列表：根评论 + 回复 -->
    <ul v-else class="space-y-4">
      <li v-for="c in comments" :key="c.id">
        <CommentItem
          :comment="c"
          :can-delete="canDelete(c)"
          @reply="startReply"
          @delete="onDelete"
        />

        <!-- 回复根评论 -->
        <form
          v-if="replyTarget?.id === c.id"
          class="ml-8 mt-2 bg-surface-2 border border-border rounded-lg p-3"
          @submit.prevent="submitReply"
        >
          <p class="text-xs text-faint mb-1">回复 @{{ c.author?.username ?? '该评论' }}</p>
          <textarea
            v-model="replyDraft"
            rows="2"
            placeholder="写下你的回复…"
            class="w-full border border-border rounded px-3 py-2 text-sm bg-surface"
          />
          <div class="flex justify-end items-center gap-3 mt-2">
            <p v-if="replyError" class="text-sm text-danger">{{ replyError }}</p>
            <button type="button" class="text-sm text-faint hover:text-text" @click="cancelReply">取消</button>
            <button
              class="px-3 py-1 bg-primary text-white rounded text-sm disabled:opacity-50"
              :disabled="replying || !replyDraft.trim()"
            >{{ replying ? '回复中…' : '回复' }}</button>
          </div>
        </form>

        <!-- 回复列表 -->
        <ul v-if="c.replies?.length" class="ml-8 mt-3 space-y-3 border-l border-border pl-4">
          <li v-for="r in c.replies" :key="r.id">
            <CommentItem
              :comment="r"
              :can-delete="canDelete(r)"
              @reply="startReply"
              @delete="onDelete"
            />

            <!-- 回复某条回复 -->
            <form
              v-if="replyTarget?.id === r.id"
              class="ml-8 mt-2 bg-surface-2 border border-border rounded-lg p-3"
              @submit.prevent="submitReply"
            >
              <p class="text-xs text-faint mb-1">回复 @{{ r.author?.username ?? '该评论' }}</p>
              <textarea
                v-model="replyDraft"
                rows="2"
                placeholder="写下你的回复…"
                class="w-full border border-border rounded px-3 py-2 text-sm bg-surface"
              />
              <div class="flex justify-end items-center gap-3 mt-2">
                <p v-if="replyError" class="text-sm text-danger">{{ replyError }}</p>
                <button type="button" class="text-sm text-faint hover:text-text" @click="cancelReply">取消</button>
                <button
                  class="px-3 py-1 bg-primary text-white rounded text-sm disabled:opacity-50"
                  :disabled="replying || !replyDraft.trim()"
                >{{ replying ? '回复中…' : '回复' }}</button>
              </div>
            </form>
          </li>
        </ul>
      </li>
    </ul>

    <!-- 分页：一页装得下就不显示 -->
    <Pagination
      v-if="total > limit"
      :page="page"
      :total="total"
      :limit="limit"
      @change="gotoPage"
    />
  </section>
</template>
