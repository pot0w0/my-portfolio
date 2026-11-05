<script setup lang="ts">
import type { Post, Series } from '~/types/api'

const props = defineProps<{
  item: { kind: 'post'; post: Post } | { kind: 'series'; series: Series }
}>()

const mediaUrl = useMediaUrl()
const isSeries = computed(() => props.item.kind === 'series')

const title = computed(() => isSeries.value ? (props.item as any).series.title : (props.item as any).post.title)
const to = computed(() => isSeries.value
  ? `/series/${(props.item as any).series.slug}`
  : `/posts/${(props.item as any).post.id}`)
const summary = computed(() => isSeries.value
  ? (props.item as any).series.description
  : (props.item as any).post.content?.slice(0, 120))
const cover = computed(() => isSeries.value ? (props.item as any).series.cover : null)
const metaText = computed(() => isSeries.value ? `${(props.item as any).series.post_count ?? 0} 篇` : '')
const createdAt = computed(() => isSeries.value ? (props.item as any).series.created_at : (props.item as any).post.created_at)
const author = computed(() => isSeries.value ? (props.item as any).series.author : (props.item as any).post.author)
const authorId = computed(() => isSeries.value ? (props.item as any).series.user_id : (props.item as any).post.user_id)
</script>

<template>
  <article class="bg-surface border border-border rounded-lg overflow-hidden hover:shadow-md transition">
    <NuxtLink v-if="isSeries && cover" :to="to" class="block aspect-video overflow-hidden">
      <img :src="mediaUrl(cover)" class="w-full h-full object-cover" alt="" />
    </NuxtLink>

    <div class="p-5">
      <div class="flex items-center gap-2 mb-2">
        <span v-if="isSeries" class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">系列</span>
        <span v-if="item.kind === 'post' && item.post.featured"
          class="text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">精选</span>
      </div>

      <h2 class="text-lg font-semibold mb-1">
        <NuxtLink :to="to" class="hover:text-primary">{{ title }}</NuxtLink>
      </h2>
      <p v-if="summary" class="text-sm text-muted line-clamp-2 mb-3">{{ summary }}</p>

      <div v-if="item.kind === 'post' && item.post.tags?.length" class="flex gap-2 flex-wrap mb-3">
        <span v-for="t in item.post.tags" :key="t.id" class="text-xs px-2 py-0.5 rounded bg-surface-2">#{{ t.name }}</span>
      </div>

      <div class="flex items-center justify-between text-sm mt-3">
        <div class="flex items-center gap-2">
          <UserBadge :user="author" :user-id="authorId" />
          <span v-if="metaText" class="text-xs text-faint">{{ metaText }}</span>
        </div>
        <time v-if="createdAt" class="text-xs text-faint">{{ new Date(createdAt).toLocaleDateString() }}</time>
      </div>
    </div>
  </article>
</template>