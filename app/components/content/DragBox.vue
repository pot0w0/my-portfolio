<template>
  <!-- relative 容器：撑开空间，作为方块定位基准 -->
  <div ref="containerRef" class="drag-container">
    <div
      ref="boxRef"
      class="drag-box"
      :class="{ dragging }"
      :style="{
        transform: `translate(${pos.x}px, ${pos.y}px)`,
        '--box-color': color
      }"
      @pointerdown="onPointerDown"
    >
      <span class="drag-handle">✥</span>
      <span class="drag-label">拖我</span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  color?: string
  startX?: number
  startY?: number
  /** 容器高度（撑开文档空间，避免方块盖住正文） */
  height?: number
}>()

const containerRef = ref<HTMLElement | null>(null)
const boxRef = ref<HTMLElement | null>(null)
const pos = reactive({ x: props.startX ?? 20, y: props.startY ?? 20 })
const dragging = ref(false)
const color = computed(() => props.color ?? '#00ccff')

let offsetX = 0
let offsetY = 0

function onPointerDown(e: PointerEvent) {
  if (!boxRef.value) return

  const rect = boxRef.value.getBoundingClientRect()
  offsetX = e.clientX - rect.left
  offsetY = e.clientY - rect.top

  dragging.value = true
  boxRef.value.setPointerCapture(e.pointerId)

  document.addEventListener('pointermove', onPointerMove)
  document.addEventListener('pointerup', onPointerUp, { once: true })
}

function onPointerMove(e: PointerEvent) {
  if (!dragging.value || !containerRef.value) return

  // 关键：减去容器在文档中的偏移
  const containerRect = containerRef.value.getBoundingClientRect()

  // 新位置 = 鼠标相对容器左上角的坐标 - 抓取偏移
  pos.x = e.clientX - containerRect.left - offsetX
  pos.y = e.clientY - containerRect.top - offsetY
}

function onPointerUp() {
  dragging.value = false
  document.removeEventListener('pointermove', onPointerMove)
}

onBeforeUnmount(() => {
  document.removeEventListener('pointermove', onPointerMove)
  document.removeEventListener('pointerup', onPointerUp)
})
</script>

<style scoped>
.drag-container {
  position: relative;      /* 定位基准 */
  width: 100%;
  height: v-bind('(props.height ?? 200) + "px"');
  margin: 1.5rem 0;
  /* 调试用：背景可见 */
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px dashed rgba(255, 255, 255, 0.1);
  overflow: hidden;        /* 防止方块拖出容器遮挡其它内容 */
}

.drag-box {
  position: absolute;      /* 相对容器定位，随文档滚动 */
  top: 0;
  left: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 18px;
  border-radius: 12px;
  cursor: grab;
  user-select: none;
  touch-action: none;
  background: rgba(20, 25, 45, 0.9);
  border: 2px solid var(--box-color);
  box-shadow:
    0 0 20px color-mix(in srgb, var(--box-color) 50%, transparent),
    inset 0 0 12px color-mix(in srgb, var(--box-color) 20%, transparent);
  color: var(--box-color);
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 13px;
  letter-spacing: 0.5px;
  transition: box-shadow 0.2s;
  will-change: transform;
}

.drag-box:hover {
  box-shadow:
    0 0 30px color-mix(in srgb, var(--box-color) 70%, transparent),
    inset 0 0 16px color-mix(in srgb, var(--box-color) 30%, transparent);
}

.drag-box.dragging {
  cursor: grabbing;
  box-shadow:
    0 0 40px color-mix(in srgb, var(--box-color) 90%, transparent),
    inset 0 0 20px color-mix(in srgb, var(--box-color) 40%, transparent);
}

.drag-handle {
  font-size: 16px;
  opacity: 0.8;
}

.drag-label {
  font-weight: 500;
  opacity: 0.9;
}
</style>