<script setup lang="ts">
const props = defineProps<{
  page: number
  total: number
  limit: number
}>()
const emit = defineEmits<{ (e: 'change', page: number): void }>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.limit)))

function go(p: number) {
  if (p < 1 || p > totalPages.value || p === props.page) return
  emit('change', p)
}
</script>

<template>
  <div v-if="total > limit" class="flex items-center justify-center gap-3 mt-8">
    <button
      class="px-3 py-1 rounded border border-border disabled:opacity-40"
      :disabled="page <= 1"
      @click="go(page - 1)"
    >上一页</button>
    <span class="text-sm text-muted">{{ page }} / {{ totalPages }}</span>
    <button
      class="px-3 py-1 rounded border border-border disabled:opacity-40"
      :disabled="page >= totalPages"
      @click="go(page + 1)"
    >下一页</button>
  </div>
</template>