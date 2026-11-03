type Theme = 'light' | 'dark' | 'system'

export function useTheme() {
  const theme = useState<Theme>('theme', () => 'system')

  const isDark = computed(() => {
    if (theme.value === 'dark') return true
    if (theme.value === 'light') return false
    // system：仅在客户端判断
    if (import.meta.client) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return false
  })

  function apply() {
    if (!import.meta.client) return
    const root = document.documentElement
    if (isDark.value) root.classList.add('dark')
    else root.classList.remove('dark')
  }

  function set(t: Theme) {
    theme.value = t
    if (import.meta.client) localStorage.setItem('theme', t)
    apply()
  }

  function toggle() {
    set(isDark.value ? 'light' : 'dark')
  }

  /** 应用启动时调用：从 localStorage 恢复 + 监听系统变化 */
  function init() {
    if (!import.meta.client) return
    const saved = localStorage.getItem('theme') as Theme | null
    if (saved === 'light' || saved === 'dark' || saved === 'system') {
      theme.value = saved
    }
    apply()

    window
      .matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', () => {
        if (theme.value === 'system') apply()
      })
  }

  async function toggleWithTransition(event?: MouseEvent) {
    if (!import.meta.client) return

    const next = isDark.value ? 'light' : 'dark'

    // 降级：浏览器不支持或用户偏好减少动画
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!document.startViewTransition || reduce) {
      set(next)
      return
    }

    // 扩散圆心：优先鼠标点，否则用按钮中心，否则页面中心
    let x = window.innerWidth / 2
    let y = window.innerHeight / 2
    if (event) {
      x = event.clientX
      y = event.clientY
    }

    // 半径 = 圆心到最远角的距离，保证圆能覆盖全屏
    const r = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y),
    )

    const root = document.documentElement
    root.style.setProperty('--vt-x', `${x}px`)
    root.style.setProperty('--vt-y', `${y}px`)
    root.style.setProperty('--vt-r', `${r}px`)

    const transition = document.startViewTransition(() => {
      set(next)       // 这里改 html.dark，触发快照
      apply()
    })

    await transition.ready

    // 对新快照做圆形揭示
    document.documentElement.animate(
      {
        clipPath: [
          `circle(0px at ${x}px ${y}px)`,
          `circle(${r}px at ${x}px ${y}px)`,
        ],
      },
      {
        duration: 500,
        easing: 'ease-in-out',
        pseudoElement: '::view-transition-new(root)',
      },
    )
  }

  return { theme, isDark, set, toggle, toggleWithTransition, init, apply }
}