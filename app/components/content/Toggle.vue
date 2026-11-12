<!-- app/components/content/Toggle.vue -->
<script setup lang="ts">
const props = defineProps<{ label?: string; defaultActive?: boolean }>()
const active = ref(props.defaultActive ?? false)
</script>

<template>
  <button
    type="button"
    class="px-3 py-1.5 rounded border text-sm"
    :class="active ? 'bg-primary text-white border-primary' : 'bg-surface border-border'"
    @click="active = !active"
  >
    {{ label || 'Toggle' }} {{ active ? '✓' : '' }}
  </button>
</template>