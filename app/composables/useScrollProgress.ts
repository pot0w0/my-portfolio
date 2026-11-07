export function useScrollProgress(el: Ref<HTMLElement | null>, maxOffset = 400) {
  const progress = ref(0)   // 0 → 1
  let raf = 0

  function update() {
    if (!el.value) return
    const rect = el.value.getBoundingClientRect()
    // 元素顶部从 0 滚到 -maxOffset 时，progress 0 → 1
    const p = Math.min(Math.max(-rect.top / maxOffset, 0), 1)
    progress.value = p
  }

  function onScroll() {
    if (!raf) raf = requestAnimationFrame(() => { update(); raf = 0 })
  }

  onMounted(() => {
    update()
    window.addEventListener('scroll', onScroll, { passive: true })
  })
  onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))

  return progress
}