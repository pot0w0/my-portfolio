<script setup lang="ts">
import type { Post } from '~/types/api'

defineProps<{ post: Post }>()
</script>

<template>
  <article class="bg-surface rounded-lg border-border p-5 hover:shadow-sm transition">
    <h2 class="text-lg font-semibold mb-1">
      <NuxtLink :to="`/posts/${post.id}`" class="hover:text-blue-600">
        {{ post.title }}
      </NuxtLink>
    </h2>
    <p class="text-sm text-muted line-clamp-2 mb-3">
      {{ post.content?.slice(0, 120) }}
    </p>
    <div class="flex items-center justify-between text-sm">
      <UserBadge :user="post.author" :user-id="post.user_id" />
      <time class="text-faint" v-if="post.created_at">
        {{ new Date(post.created_at).toLocaleDateString() }}
      </time>
    </div>
    <div class="flex items-center gap-2 text-xs text-faint mt-2 flex-wrap">
      <span v-if="post.category" class="px-2 py-0.5 rounded bg-primary/10 text-primary">
        {{ post.category.name }}
      </span>
      <span v-for="t in post.tags" :key="t.id" class="px-2 py-0.5 rounded bg-surface-2">
        #{{ t.name }}
      </span>
      <span v-if="post.featured" class="px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
        精选
      </span>
    </div>
  </article>
</template>