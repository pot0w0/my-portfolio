<script setup lang="ts">
import type { Comment } from '~/types/api'

const props = defineProps<{
  comment: Comment
  canDelete?: boolean
}>()
const emit = defineEmits<{
  (e: 'reply', comment: Comment): void
  (e: 'delete', comment: Comment): void
}>()

const { like, unlike } = useComments()
const { isLoggedIn } = useAuth()

const likeCount = ref(props.comment.like_count ?? 0)
const liked = ref(!!props.comment.liked_by_me)
const liking = ref(false)

watch(() => props.comment, (c) => {
  likeCount.value = c.like_count ?? 0
  liked.value = !!c.liked_by_me
})

async function toggleLike() {
  if (!isLoggedIn.value) {
    await navigateTo('/login')
    return
  }
  liking.value = true
  try {
    const stats = liked.value
      ? await unlike(props.comment.id)
      : await like(props.comment.id)
    likeCount.value = stats.like_count
    liked.value = stats.liked_by_me
  } catch {} finally {
    liking.value = false
  }
}

// 被回复者主页：有 id 用 id，否则回退到用户名
const replyToLink = computed(() => {
  const c = props.comment
  if (c.reply_to_user_id) return `/user/${c.reply_to_user_id}`
  return c.reply_to_username ? `/user/${encodeURIComponent(c.reply_to_username)}` : null
})
</script>

<template>
  <div class="bg-surface border border-border rounded-lg p-4">
    <div class="flex items-center justify-between mb-1">
      <UserBadge :user="comment.author" :user-id="comment.user_id" />
      <div class="flex items-center gap-3 text-xs text-faint">
        <time v-if="comment.created_at">{{ new Date(comment.created_at).toLocaleString() }}</time>
        <button class="hover:text-primary hover:underline" @click="emit('reply', comment)">回复</button>
        <button v-if="canDelete" class="text-danger hover:underline" @click="emit('delete', comment)">删除</button>
      </div>
    </div>

    <p v-if="comment.reply_to_username" class="text-xs text-faint mb-1">
      回复
      <NuxtLink v-if="replyToLink" :to="replyToLink" class="text-primary hover:underline">
        @{{ comment.reply_to_username }}
      </NuxtLink>
      <span v-else>@{{ comment.reply_to_username }}</span>
    </p>

    <CommentContent :content="comment.content" />

    <div class="mt-2">
      <button
        type="button"
        class="text-xs inline-flex items-center gap-1 disabled:opacity-50 transition"
        :class="liked ? 'text-danger' : 'text-faint hover:text-danger'"
        :disabled="liking"
        @click="toggleLike"
        :aria-pressed="liked"
      >
        <span>{{ liked ? '♥' : '♡' }}</span>
        <span v-if="likeCount">{{ likeCount }}</span>
        <span v-else>赞</span>
      </button>
    </div>
  </div>
</template>
