type Theme = 'light' | 'dark' | 'system'

export function useTheme() {
  const theme = useState<Theme>('theme', () => 'system')

  const isDark = computed(() => {
    if (theme.value === 'dark') return true
    if (theme.value === 'light') return false
    if (import.meta.client) return window.matchMedia('(prefers-color-scheme: dark)').matches
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

  async function toggleWithTransition(event?: MouseEvent) {
    if (!import.meta.client) return
    const next = isDark.value ? 'light' : 'dark'
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!(document as any).startViewTransition || reduce) {
      set(next)
      return
    }
    let x = window.innerWidth / 2
    let y = window.innerHeight / 2
    if (event) { x = event.clientX; y = event.clientY }
    const r = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y),
    )
    const root = document.documentElement
    root.style.setProperty('--vt-x', `${x}px`)
    root.style.setProperty('--vt-y', `${y}px`)
    root.style.setProperty('--vt-r', `${r}px`)

    const transition = (document as any).startViewTransition(() => {
      const el = document.documentElement
      if (next === 'dark') el.classList.add('dark')
      else el.classList.remove('dark')
      theme.value = next
      if (import.meta.client) localStorage.setItem('theme', next)
    })

    try { await transition.ready } catch { return }
    await new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)))
    document.documentElement.animate(
      {
        clipPath: [
          `circle(0px at ${x}px ${y}px)`,
          `circle(${r}px at ${x}px ${y}px)`,
        ],
      },
      {
        duration: 500,
        easing: 'cubic-bezier(.4,0,.2,1)',
        pseudoElement: '::view-transition-new(root)',
      },
    )
  }

  function init() {
    if (!import.meta.client) return
    const saved = localStorage.getItem('theme') as Theme | null
    if (saved === 'light' || saved === 'dark' || saved === 'system') theme.value = saved
    apply()
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (theme.value === 'system') apply()
    })
  }

  return { theme, isDark, set, toggle, toggleWithTransition, init, apply }
}