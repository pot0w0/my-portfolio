<script setup lang="ts">
import type { Series } from '~/types/api'
const api = useApi()
const seriesList = ref<Series[]>([])
onMounted(async () => {
  seriesList.value = await api.get<Series[]>('/api/series')
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold">系列</h1>
    <div class="grid gap-4 md:grid-cols-2">
      <NuxtLink
        v-for="s in seriesList"
        :key="s.id"
        :to="`/series/${s.slug}`"
        class="block bg-surface border border-border rounded-lg p-5 hover:shadow-md transition"
      >
        <h2 class="font-semibold text-lg">{{ s.title }}</h2>
        <p class="text-sm text-muted line-clamp-2 mt-1">{{ s.description }}</p>
        <p class="text-xs text-faint mt-2">{{ s.post_count }} 篇</p>
      </NuxtLink>
    </div>
  </div>
</template>