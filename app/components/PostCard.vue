<script setup lang="ts">
import type { Post } from '~/types/api'

defineProps<{ post: Post }>()
</script>

<template>
  <article class="bg-white rounded-lg border p-5 hover:shadow-sm transition">
    <h2 class="text-lg font-semibold mb-1">
      <NuxtLink :to="`/posts/${post.id}`" class="hover:text-blue-600">
        {{ post.title }}
      </NuxtLink>
    </h2>
    <p class="text-sm text-slate-600 line-clamp-2 mb-3">
      {{ post.content?.slice(0, 120) }}
    </p>
    <div class="flex items-center justify-between text-sm">
      <UserBadge :user="post.author" :user-id="post.user_id" />
      <time class="text-slate-400" v-if="post.created_at">
        {{ new Date(post.created_at).toLocaleDateString() }}
      </time>
    </div>
  </article>
</template>