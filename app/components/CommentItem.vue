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

// 作者主页链接
const authorLink = computed(() => {
  const c = props.comment
  if (c.user_id) return `/user/${c.user_id}`
  const name = c.author?.username
  return name ? `/user/${encodeURIComponent(name)}` : null
})

const authorName = computed(() => props.comment.author?.username ?? '匿名')
</script>

<template>
  <div class="bg-surface border border-border rounded-lg p-4 flex gap-3 items-start">
    <!-- 左侧：头像 + 昵称（竖排，固定窄列，右侧正文自然留白） -->
    <div class="flex flex-col items-center w-20 shrink-0">
      <UserBadge
        :user="comment.author"
        :user-id="comment.user_id"
        class="[&_img]:w-16 [&_img]:h-16 [&_img]:rounded-full"
      />
      <NuxtLink
        v-if="authorLink"
        :to="authorLink"
        class="mt-1 max-w-full truncate text-xs text-faint hover:text-primary hover:underline"
        :title="authorName"
      >
        <!-- {{ authorName }} -->
      </NuxtLink>
      <span v-else class="mt-1 max-w-full truncate text-xs text-faint" :title="authorName">
        {{ authorName }}
      </span>
    </div>

    <!-- 右侧内容区 -->
    <div class="flex-1 min-w-0">
      <!-- 被回复信息 -->
      <p v-if="comment.reply_to_username" class="text-xs text-faint mb-1">
        回复
        <NuxtLink v-if="replyToLink" :to="replyToLink" class="text-primary hover:underline">
          @{{ comment.reply_to_username }}
        </NuxtLink>
        <span v-else>@{{ comment.reply_to_username }}</span>
      </p>

      <!-- 评论正文 -->
      <CommentContent :content="comment.content" />

      <!-- 底部：时间、回复、点赞 -->
      <div class="mt-2 flex items-center gap-3 text-xs text-faint">
        <time v-if="comment.created_at">{{ new Date(comment.created_at).toLocaleString() }}</time>
        <button class="hover:text-primary hover:underline" @click="emit('reply', comment)">回复</button>
        <button
          type="button"
          class="inline-flex items-center gap-1 disabled:opacity-50 transition"
          :class="liked ? 'text-danger' : 'text-faint hover:text-danger'"
          :disabled="liking"
          @click="toggleLike"
          :aria-pressed="liked"
        >
          <span>{{ liked ? '♥' : '♡' }}</span>
          <span v-if="likeCount">{{ likeCount }}</span>
          <span v-else>赞</span>
        </button>
        <button v-if="canDelete" class="text-danger hover:underline" @click="emit('delete', comment)">删除</button>
      </div>
    </div>
  </div>
</template>
