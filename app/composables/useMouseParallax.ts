export function useMouseParallax(strength = 20) {
  if (!import.meta.client) return

  let raf = 0
  let targetX = 0
  let targetY = 0
  let currentX = 0
  let currentY = 0

  function onMove(e: MouseEvent) {
    // 归一化到 [-1, 1]，以视口中心为原点
    targetX = (e.clientX / window.innerWidth - 0.5) * 2
    targetY = (e.clientY / window.innerHeight - 0.5) * 2
    if (!raf) raf = requestAnimationFrame(tick)
  }

  function tick() {
    // 缓动逼近，产生"缓慢"跟随
    currentX += (targetX - currentX) * 0.08
    currentY += (targetY - currentY) * 0.08

    const root = document.documentElement
    root.style.setProperty('--mx', currentX.toFixed(4))
    root.style.setProperty('--my', currentY.toFixed(4))

    // 还没逼近到位就继续跑
    if (Math.abs(targetX - currentX) > 0.001 || Math.abs(targetY - currentY) > 0.001) {
      raf = requestAnimationFrame(tick)
    } else {
      raf = 0
    }
  }

  onMounted(() => window.addEventListener('mousemove', onMove, { passive: true }))
  onBeforeUnmount(() => {
    window.removeEventListener('mousemove', onMove)
    if (raf) cancelAnimationFrame(raf)
  })
}