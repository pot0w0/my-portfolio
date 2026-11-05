export function useAutoHideHeader(options?: { threshold?: number; topZone?: number }) {
  const threshold = options?.threshold ?? 8
  const topZone = options?.topZone ?? 60
  const hidden = useState('header:hidden', () => false)
  const locked = useState('header:locked', () => false)
  let lastY = 0

  function onScroll() {
    if (locked.value) return
    const y = window.scrollY
    if (y <= topZone) { hidden.value = false; lastY = y; return }
    const dy = y - lastY
    if (Math.abs(dy) < threshold) return
    hidden.value = dy > 0
    lastY = y
  }

  function show() { hidden.value = false }

  onMounted(() => {
    lastY = window.scrollY
    window.addEventListener('scroll', onScroll, { passive: true })
  })
  onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))

  return { hidden, show, locked }
}