<script setup lang="ts">
const props = defineProps<{
  min?: number
  max?: number
  default?: number
  label?: string
  unit?: string
}>()

const value = ref(props.default ?? Math.floor(((props.min ?? 0) + (props.max ?? 100)) / 2))
</script>

<template>
  <div class="my-4 p-4 border border-border rounded-lg bg-surface space-y-2">
    <div class="flex items-center justify-between text-sm">
      <span class="text-muted">{{ label || '值' }}</span>
      <span class="text-primary font-medium">{{ value }}{{ unit || '' }}</span>
    </div>
    <input
      v-model.number="value"
      type="range"
      :min="min ?? 0"
      :max="max ?? 100"
      class="w-full accent-primary"
    />
  </div>
</template>