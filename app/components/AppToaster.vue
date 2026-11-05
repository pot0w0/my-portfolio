<script setup lang="ts">
const { toasts, dismiss } = useToast()
const colors = {
  error: 'bg-danger/10 border-danger/40 text-danger',
  success: 'bg-emerald-500/10 border-emerald-500/40 text-emerald-600 dark:text-emerald-400',
  info: 'bg-primary/10 border-primary/40 text-primary',
} as const
</script>

<template>
  <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-[min(360px,calc(100vw-2rem))]" aria-live="polite">
    <TransitionGroup
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-for="t in toasts" :key="t.id"
        class="border rounded-lg px-4 py-3 text-sm shadow-lg backdrop-blur bg-surface/95 flex items-start gap-3"
        :class="colors[t.type]" role="alert"
      >
        <span class="flex-1 whitespace-pre-wrap break-words">{{ t.message }}</span>
        <button class="shrink-0 opacity-60 hover:opacity-100" aria-label="关闭" @click="dismiss(t.id)">✕</button>
      </div>
    </TransitionGroup>
  </div>
</template>