<script setup lang="ts">
const props = defineProps<{
  count?: number
  size?: number
  speed?: number
  containerHeight?: number   // 不再用，全屏
  zIndex?: number
  pointerEvents?: 'none' | 'auto'   // 默认 none，不挡点击
}>()

const n = computed(() => props.count ?? 10)
const boxSize = computed(() => props.size ?? 48)
const baseSpeed = computed(() => props.speed ?? 100)
const zIndex = computed(() => props.zIndex ?? 50)
const pointerEvents = computed(() => props.pointerEvents ?? 'none')

interface Box { x: number; y: number; vx: number; vy: number; hue: number }

const boxes = ref<Box[]>([])
let raf = 0
let lastT = 0

function rand(min: number, max: number) { return min + Math.random() * (max - min) }

function initBoxes() {
  const w = window.innerWidth
  const h = window.innerHeight
  boxes.value = Array.from({ length: n.value }, () => ({
    x: rand(0, w - boxSize.value),
    y: rand(0, h - boxSize.value),
    vx: rand(-1, 1) * baseSpeed.value || baseSpeed.value,
    vy: rand(-1, 1) * baseSpeed.value || baseSpeed.value,
    hue: rand(0, 360),
  }))
}

function step(t: number) {
  if (!lastT) lastT = t
  const dt = Math.min((t - lastT) / 1000, 0.05)
  lastT = t

  const w = window.innerWidth
  const h = window.innerHeight
  const s = boxSize.value

  for (const b of boxes.value) {
    b.x += b.vx * dt
    b.y += b.vy * dt

    if (b.x < 0) { b.x = 0; b.vx = Math.abs(b.vx) }
    if (b.x > w - s) { b.x = w - s; b.vx = -Math.abs(b.vx) }
    if (b.y < 0) { b.y = 0; b.vy = Math.abs(b.vy) }
    if (b.y > h - s) { b.y = h - s; b.vy = -Math.abs(b.vy) }
  }

  raf = requestAnimationFrame(step)
}

function onResize() { initBoxes() }

onMounted(() => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  initBoxes()
  raf = requestAnimationFrame(step)
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', onResize)
})
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 overflow-hidden"
      :style="{ zIndex, pointerEvents }"
      aria-hidden="true"
    >
      <div
        v-for="(b, i) in boxes"
        :key="i"
        class="absolute rounded"
        :style="{
          width: `${boxSize}px`,
          height: `${boxSize}px`,
          transform: `translate(${b.x}px, ${b.y}px)`,
          background: `hsl(${b.hue} 80% 60% / 0.8)`,
          boxShadow: `0 0 12px hsl(${b.hue} 90% 60% / 0.6)`,
        }"
      />
    </div>
  </Teleport>
</template>