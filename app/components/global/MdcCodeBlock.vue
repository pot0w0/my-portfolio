<script setup lang="ts">
/**
 * Markdown 代码块：折叠 + 展开
 * - 所有围栏代码块默认折叠（超过 COLLAPSED_MAX 才出现"展开"按钮）
 * - ```html 额外提供"运行"按钮，在独立窗口（沙箱 iframe）里渲染效果
 *
 * 通过 nuxt.config.ts 的 mdc.components.map 把 <pre> 映射到本组件；
 * 放在 components/global 下是为了让 MDCRenderer 能在运行时按名字找到它。
 */
const props = defineProps<{
  code?: string
  language?: string | null
  filename?: string | null
  class?: string | null
}>()

const COLLAPSED_MAX = 320

const preRef = ref<HTMLElement | null>(null)
const expanded = ref(false)
const overflowing = ref(false)
const dialogOpen = ref(false)

const normalizedLang = computed(() => (props.language || 'text').toLowerCase())
const isHtml = computed(() => normalizedLang.value === 'html' || normalizedLang.value === 'htm')

const showFade = computed(() => overflowing.value && !expanded.value)

const preStyle = computed(() =>
  expanded.value ? undefined : { maxHeight: `${COLLAPSED_MAX}px`, overflowY: 'hidden' as const },
)

function measure() {
  const el = preRef.value
  if (!el) return
  overflowing.value = el.scrollHeight > COLLAPSED_MAX + 1
}

let ro: ResizeObserver | undefined

onMounted(() => {
  measure()
  // 字体/高亮渲染完成后高度可能变化，跟着重新量一次
  if (preRef.value?.firstElementChild) {
    ro = new ResizeObserver(measure)
    ro.observe(preRef.value.firstElementChild)
  }
})

onBeforeUnmount(() => ro?.disconnect())

watch(
  () => props.code,
  async () => {
    expanded.value = false
    await nextTick()
    measure()
  },
)
</script>

<template>
  <div class="code-block relative my-5">
    <div
      class="flex items-center justify-between gap-3 px-3 py-1.5 rounded-t-lg border border-b-0 border-border bg-surface text-xs text-faint"
    >
      <span class="truncate font-mono">{{ props.filename || normalizedLang }}</span>
      <div class="flex items-center gap-2 shrink-0">
        <button
          v-if="isHtml"
          type="button"
          class="px-2 py-0.5 rounded border border-border hover:text-primary hover:border-primary transition-colors"
          title="在独立窗口中运行这段 HTML"
          @click="dialogOpen = true"
        >
          ▶ 运行
        </button>
        <button
          v-if="overflowing"
          type="button"
          class="px-2 py-0.5 rounded border border-border hover:text-text hover:border-primary transition-colors"
          :aria-expanded="expanded"
          @click="expanded = !expanded"
        >
          {{ expanded ? '收起' : '展开' }}
        </button>
      </div>
    </div>

    <pre ref="preRef" :class="props.class" :style="preStyle"><slot /></pre>

    <div
      v-if="showFade"
      class="pointer-events-none absolute inset-x-px bottom-px h-16 rounded-b-lg bg-linear-to-t from-surface-2 to-transparent"
    />

    <HtmlRunDialog
      v-if="dialogOpen"
      :code="props.code || ''"
      :title="props.filename || 'HTML'"
      @close="dialogOpen = false"
    />
  </div>
</template>

<style scoped>
.code-block pre {
  margin-top: 0;
  margin-bottom: 0;
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
</style>
