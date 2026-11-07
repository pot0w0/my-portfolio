<script setup lang="ts">
import type { Post } from '~/types/api'
defineProps<{ post: Post }>()
const mediaUrl = useMediaUrl()
</script>

<template>
  <article class="bg-surface border border-border rounded-lg p-5 hover:shadow-md transition">
    <div class="flex gap-4">
      <!-- 左：文字内容 -->
      <div class="flex-1 min-w-0">
        <h2 class="text-lg font-semibold mb-1">
          <NuxtLink :to="`/posts/${post.id}`" class="hover:text-primary">{{ post.title }}</NuxtLink>
        </h2>
        <p class="text-sm text-muted line-clamp-2 mb-3">{{ post.content?.slice(0, 120) }}</p>

        <div class="flex items-center gap-2 text-xs text-faint flex-wrap mb-3">
          <span v-for="t in post.tags" :key="t.id" class="px-2 py-0.5 rounded bg-surface-2">#{{ t.name }}</span>
          <span v-if="post.featured" class="px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">精选</span>
          <span v-if="post.series" class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            系列 · {{ post.series.title }}
          </span>
        </div>
      </div>

      <NuxtLink
        v-if="post.cover"
        :to="`/posts/${post.id}`"
        class="shrink-0 w-28 h-20 md:w-36 md:h-24 rounded-lg overflow-hidden border border-border bg-surface-2"
      >
        <img
          :src="mediaUrl(post.cover)"
          class="w-full h-full object-cover"
          alt=""
          loading="lazy"
        />
      </NuxtLink>
    </div>
    <div class="flex items-center justify-between text-sm">
      <UserBadge :user="post.author" :user-id="post.user_id" />
      <time v-if="post.created_at" class="text-faint">{{ new Date(post.created_at).toLocaleDateString() }}</time>
    </div>
  </article>
</template>