export function useAutoHideHeader(options?: { threshold?: number; topZone?: number }) {
  const threshold = options?.threshold ?? 8    // 小于这个位移不触发，防抖
  const topZone = options?.topZone ?? 60       // 距顶多少 px 内强制显示

  const hidden = useState('header:hidden', () => false)
  let lastY = 0

  function onScroll() {
    const y = window.scrollY
    const dy = y - lastY

    // 在顶部区域附近，永远显示
    if (y <= topZone) {
      hidden.value = false
      lastY = y
      return
    }

    // 位移太小，忽略（避免抖动）
    if (Math.abs(dy) < threshold) return

    if (dy > 0) {
      // 向下滚 → 隐藏
      hidden.value = true
    } else {
      // 向上滚 → 显示
      hidden.value = false
    }
    lastY = y
  }

  function show() {
    hidden.value = false
  }

  onMounted(() => {
    lastY = window.scrollY
    window.addEventListener('scroll', onScroll, { passive: true })
  })

  onBeforeUnmount(() => {
    window.removeEventListener('scroll', onScroll)
  })

  return { hidden, show }
}