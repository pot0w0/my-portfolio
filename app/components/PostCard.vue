<script setup lang="ts">
import type { Post } from '~/types/api'
defineProps<{ post: Post }>()
</script>

<template>
  <article class="bg-surface border border-border rounded-lg p-5 hover:shadow-md transition">
    <h2 class="text-lg font-semibold mb-1">
      <NuxtLink :to="`/posts/${post.id}`" class="hover:text-primary">{{ post.title }}</NuxtLink>
    </h2>
    <p class="text-sm text-muted line-clamp-2 mb-3">{{ post.content?.slice(0, 120) }}</p>
    <div class="flex items-center gap-2 text-xs text-faint flex-wrap mb-3">
      <span v-if="post.category" class="px-2 py-0.5 rounded bg-primary/10 text-primary">{{ post.category.name }}</span>
      <span v-for="t in post.tags" :key="t.id" class="px-2 py-0.5 rounded bg-surface-2">#{{ t.name }}</span>
      <span v-if="post.featured" class="px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">精选</span>
      <span v-if="post.series" class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
        系列 · {{ post.series.title }}
      </span>
    </div>
    <div class="flex items-center justify-between text-sm">
      <UserBadge :user="post.author" :user-id="post.user_id" />
      <time v-if="post.created_at" class="text-faint">{{ new Date(post.created_at).toLocaleDateString() }}</time>
    </div>
  </article>
</template>