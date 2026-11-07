<script setup lang="ts">
const { user, isLoggedIn, logout } = useAuth()
const { hidden, show } = useAutoHideHeader({ topZone: 60 })
const { isDark, toggleWithTransition } = useTheme()
const router = useRouter()
const route = useRoute()
const showSearch = ref(false)

function onKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    showSearch.value = true
  }
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))

async function onLogout() {
  await logout()
  await router.push('/')
}

watch(() => route.fullPath, () => show())

function onMouseMove(e: MouseEvent) {
  if (e.clientY <= 60) show()
}
onMounted(() => {
  if (window.matchMedia('(hover: hover)').matches) {
    window.addEventListener('mousemove', onMouseMove, { passive: true })
  }
})
onBeforeUnmount(() => {
  window.removeEventListener('mousemove', onMouseMove)
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header
      class="fixed top-0 inset-x-0 z-40 border-b border-border bg-surface/90 backdrop-blur
             transition-transform duration-300 will-change-transform"
      :class="hidden ? '-translate-y-full' : 'translate-y-0'"
    >
      <div class="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        <!-- 左：logo -->
        <NuxtLink to="/" class="font-bold text-lg shrink-0">Portfolio</NuxtLink>

        <!-- 右：搜索 + 导航 + 主题 -->
        <div class="flex items-center gap-3 md:gap-4">
          <!-- 搜索按钮：移动端只显示图标 -->
          <button
            class="flex items-center gap-1.5 px-2 py-1 border border-border rounded text-sm text-faint hover:text-text shrink-0"
            @click="showSearch = true"
            aria-label="搜索"
          >
            <span>🔍</span>
            <span class="hidden md:inline">搜索</span>
            <kbd class="hidden md:inline text-xs border border-border rounded px-1">⌘K</kbd>
          </button>

          <nav class="flex items-center gap-3 md:gap-4 text-sm">
            <NuxtLink to="/" class="hover:text-primary">首页</NuxtLink>
            <NuxtLink to="/posts" class="hover:text-primary">博客</NuxtLink>
            <ClientOnly>
              <template v-if="isLoggedIn">
                <NuxtLink to="/user" class="hover:text-primary">我的</NuxtLink>
                <button class="text-faint hover:text-danger" @click="onLogout">登出</button>
              </template>
              <template v-else>
                <NuxtLink to="/login" class="hover:text-primary">登录</NuxtLink>
                <NuxtLink to="/register" class="hover:text-primary">注册</NuxtLink>
              </template>
            </ClientOnly>
          </nav>

          <button
            class="text-primary hover:opacity-80 shrink-0"
            :title="isDark ? '切换到日间' : '切换到夜间'"
            @click="toggleWithTransition($event)"
          >
            {{ isDark ? '日️' : '月' }}
          </button>
        </div>
      </div>
    </header>

    <main class="flex-1 max-w-4xl w-full mx-auto px-4 pt-20 pb-8">
      <slot />
    </main>

    <footer class="border-t border-border bg-surface">
      <div class="max-w-4xl mx-auto px-4 py-4 text-sm text-faint">
        © {{ new Date().getFullYear() }} Portfolio
      </div>
    </footer>

    <!-- 搜索面板：必须挂上，否则 showSearch 无效 -->
    <SearchCommand :open="showSearch" @close="showSearch = false" />
  </div>
</template>