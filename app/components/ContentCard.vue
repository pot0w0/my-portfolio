<script setup lang="ts">
import type { Post, Series } from '~/types/api'

const props = defineProps<{
  item: { kind: 'post'; post: Post } | { kind: 'series'; series: Series }
}>()

const mediaUrl = useMediaUrl()

const isSeries = computed(() => props.item.kind === 'series')

// 统一抽取字段，避免模板里到处 as any
const data = computed(() => {
  if (props.item.kind === 'series') {
    const s = props.item.series
    return {
      kind: 'series' as const,
      title: s.title,
      to: `/series/${s.slug}`,
      summary: s.description,
      cover: s.cover,
      tags: [] as { id: number; name: string }[],
      featured: false,
      seriesName: undefined as string | undefined,
      metaText: `${s.post_count ?? 0} 篇`,
      createdAt: s.created_at,
      author: s.author,
      authorId: s.user_id,
      status: undefined as Post['status'],
    }
  }
  const p = props.item.post
  return {
    kind: 'post' as const,
    title: p.title,
    to: `/posts/${p.id}`,
    summary: p.content?.slice(0, 120),
    cover: p.cover,
    tags: p.tags ?? [],
    featured: p.featured,
    seriesName: p.series?.title,
    metaText: undefined as string | undefined,
    createdAt: p.created_at,
    author: p.author,
    authorId: p.user_id,
    status: p.status,
  }
})
</script>

<template>
  <article class="bg-surface border border-border rounded-lg p-5 hover:shadow-md transition">
    <div class="flex gap-4">
      <!-- 左：文字 -->
      <div class="flex-1 min-w-0">
        <!-- 徽标行：状态 / 系列 / 精选 / post 所属系列 -->
        <div class="flex items-center gap-2 mb-2 flex-wrap">
          <span
            v-if="data.status === 'draft'"
            class="text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300"
          >草稿</span>
          <span
            v-else-if="data.status === 'archived'"
            class="text-xs px-2 py-0.5 rounded bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
          >已归档</span>
          <span
            v-if="data.kind === 'series'"
            class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
          >系列</span>
          <span
            v-if="data.featured"
            class="text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300"
          >精选</span>
          <span
            v-if="data.seriesName"
            class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
          >系列 · {{ data.seriesName }}</span>
        </div>

        <h2 class="text-lg font-semibold mb-1">
          <NuxtLink :to="data.to" class="hover:text-primary">{{ data.title }}</NuxtLink>
        </h2>

        <p v-if="data.summary" class="text-sm text-muted line-clamp-2 mb-3">
          {{ data.summary }}
        </p>

        <div class="flex items-center gap-2 text-xs text-faint flex-wrap">
          <span
            v-for="t in data.tags"
            :key="t.id"
            class="px-2 py-0.5 rounded bg-surface-2"
          >#{{ t.name }}</span>
          <span v-if="data.metaText" class="px-2 py-0.5 rounded bg-surface-2">
            {{ data.metaText }}
          </span>
        </div>
      </div>

      <!-- 右：封面 -->
      <NuxtLink
        v-if="data.cover"
        :to="data.to"
        class="shrink-0 w-28 h-20 md:w-36 md:h-24 rounded-lg overflow-hidden border border-border bg-surface-2"
      >
        <img
          :src="mediaUrl(data.cover)"
          class="w-full h-full object-cover"
          alt=""
          loading="lazy"
        />
      </NuxtLink>
    </div>

    <!-- 底部：作者 + 时间 -->
    <div class="flex items-center justify-between text-sm mt-3">
      <UserBadge
        v-if="data.authorId"
        :user="data.author"
        :user-id="data.authorId"
      />
      <time v-if="data.createdAt" class="text-faint">
        {{ new Date(data.createdAt).toLocaleDateString() }}
      </time>
    </div>
  </article>
</template>