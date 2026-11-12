<script setup lang="ts">
/**
 * HTML 运行预览：把代码放进 sandbox iframe 的 srcdoc 里，和页面完全隔离。
 * 不给 allow-same-origin，脚本能跑但拿不到父页面的 DOM / 存储。
 */
const props = defineProps<{
  code: string
  title?: string
}>()

const emit = defineEmits<{ (e: 'close'): void }>()

const content = computed(() => props.code.trim())

let prevOverflow = ''

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => {
  prevOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  document.body.style.overflow = prevOverflow
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-[200] flex items-center justify-center bg-black/60 p-4"
      @click.self="emit('close')"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="HTML 运行预览"
        class="w-[min(1100px,94vw)] h-[min(780px,88vh)] flex flex-col overflow-hidden rounded-lg border border-border bg-surface shadow-2xl"
      >
        <div class="flex items-center justify-between gap-4 px-4 h-11 shrink-0 border-b border-border">
          <span class="text-sm font-medium truncate">{{ props.title || 'HTML' }}</span>
          <button
            type="button"
            class="px-2 py-1 rounded border border-border text-sm text-faint hover:text-danger hover:border-danger transition-colors"
            aria-label="关闭"
            @click="emit('close')"
          >
            ✕
          </button>
        </div>
        <iframe
          :srcdoc="content"
          sandbox="allow-scripts allow-forms allow-modals allow-popups allow-downloads"
          class="flex-1 w-full border-0 bg-white"
          title="HTML 运行预览"
        />
      </div>
    </div>
  </Teleport>
</template>
